import os
import tempfile
import logging
from decimal import Decimal
from datetime import datetime, timedelta, timezone as dt_timezone

import pandas as pd
import stripe
from celery.result import AsyncResult

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import (
    JsonResponse,
    HttpResponse,
    FileResponse,
    Http404
)
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils._os import safe_join
from django.views.decorators.csrf import csrf_exempt

from .forms import ReportForm, RoomFormSet
from .tasks import generate_report_task, process_payment_task
from core.models import (
    Logger as LoggerModel,
    Logger_Data,
    Room,
    Report,
    Downloads,
    Payment
)
from .utils import PCAdataTool
from .utils.normalize_logger_serial import normalize_logger_serial
from .utils.resize_and_save_image import resize_and_save_image
from .utils.room_data import RoomData


# Configure strapi 
stripe.api_key = settings.STRIPE_SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger(__name__)

User = get_user_model()


def fetch_logger_data(logger_serial, start_timestamp, end_timestamp):
    """Fetch logger data within the specified timestamp range and return as a DataFrame."""
    try:
        logger = LoggerModel.objects.get(serial_number=logger_serial)
        data = Logger_Data.objects.filter(logger=logger, timestamp__range=(start_timestamp, end_timestamp))

        if not data.exists():
            return None  # No data found for this logger within the range
        return pd.DataFrame(list(data.values()))

    except LoggerModel.DoesNotExist:
        # Log this error for debugging purposes
        app_logger.error(f"Sensor with serial number {logger_serial} does not exist.")
        return None

def clean_data(combined_data: pd.DataFrame) -> pd.DataFrame:
    # Drop any duplicate columns
    combined_data = combined_data.loc[:, ~combined_data.columns.duplicated()]
    
    # Handle missing values if any
    combined_data.fillna("", inplace=True)
    
    # Ensure all columns that should be numeric are numeric
    numeric_cols = ['IndoorAirTemp', 'SurfaceTemp', 'IndoorRelativeH', 
                    'OutdoorAirTemp', 'OutdoorRelativeH']
    for col in numeric_cols:
        combined_data[col] = pd.to_numeric(combined_data[col], errors='coerce')
    
    return combined_data

def save_uploaded_file(uploaded_file):
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    return ''

@login_required
def report_view(request):
    form = ReportForm(request.POST, request.FILES)
    room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')
    user = request.user 
    
    if request.method == 'GET':
        room_formset = RoomFormSet(queryset=Room.objects.none(), prefix='rooms')
        form = ReportForm()
        return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})
        
    else:
        
        if form.is_valid() and room_formset.is_valid():
            app_logger.debug("Form and formset are valid.")
            app_logger.debug(f"Number of rooms being processed: {len(room_formset.cleaned_data)}")

            # Save the Report object first
            report_instance = form.save(commit=False)
            report_instance.user = request.user

            external_picture_file = request.FILES.get('external_picture')
            company_logo_file = request.FILES.get('company_logo')

            if external_picture_file:
                report_instance.external_picture = external_picture_file

            if company_logo_file:
                report_instance.company_logo = company_logo_file

            report_instance.save()

            # Resize external_picture and company_logo after saving
            # Resize and save external_picture as JPEG with 70% quality
            if external_picture_file:
                resized_external_path = resize_and_save_image(
                    report_instance.external_picture.path, 
                    max_size=1500, 
                    quality=70
                )
                if resized_external_path:
                    # Update the external_picture field to point to the new JPEG file
                    report_instance.external_picture.name = os.path.relpath(resized_external_path, settings.MEDIA_ROOT)
                    report_instance.save()
                else:
                    form.add_error('external_picture', 'Failed to process external picture.')

            # Resize and save company_logo as PNG (lossless)
            if company_logo_file:
                resized_logo_path = resize_and_save_image(
                    report_instance.company_logo.path, 
                    max_size=1500
                )
                if resized_logo_path:
                    # Update the company_logo field to point to the new PNG file
                    report_instance.company_logo.name = os.path.relpath(resized_logo_path, settings.MEDIA_ROOT)
                    report_instance.save()
                else:
                    form.add_error('company_logo', 'Failed to process company logo.')

            # Initialize lists to store room pictures and CSV file paths
            room_pictures = []
            csv_file_paths = []

            # Save Room formset with the associated Report instance
            for room_form in room_formset:
                room_instance = room_form.save(commit=False)

                if room_form.cleaned_data and not room_form.cleaned_data.get('DELETE', False):
                    room_instance = room_form.save(commit=False)
                    room_instance.report = report_instance

                if room_instance.pk: 
                    # Update the existing room instance
                    room_instance.report = report_instance
                else:
                    # Create a new room instance
                    room_instance = Room(report=report_instance)

                # Handle room_picture
                room_picture_file = room_form.cleaned_data.get('room_picture')
                if room_picture_file:
                    room_instance.room_picture = room_picture_file
                    room_instance.save()

                    # Resize and save room_picture as JPEG with 70% quality
                    resized_room_path = resize_and_save_image(
                        room_instance.room_picture.path, 
                        max_size=1500, 
                        quality=70,
                        target_format='JPEG'
                    )
                    if resized_room_path:
                        room_instance.room_picture.name = os.path.relpath(resized_room_path, settings.MEDIA_ROOT)
                        room_instance.save()
                        room_pictures.append(room_instance.room_picture.path)
                    else:
                        room_form.add_error('room_picture', 'Failed to process room picture.')
                else:
                    room_instance.save()

            # Fetch logger data from form
            external_logger_serial = normalize_logger_serial(form.cleaned_data['external_logger'])
            ambient_logger_serials = [
                normalize_logger_serial(room_data.get('room_ambient_logger')) 
                for room_data in room_formset.cleaned_data
            ]
            surface_logger_serials = [
                normalize_logger_serial(room_data.get('room_surface_logger')) 
                for room_data in room_formset.cleaned_data
            ]

            print(f"External Logger Serial: {external_logger_serial}")
            print(f"Ambient Logger Serials: {ambient_logger_serials}")
            print(f"Surface Logger Serials: {surface_logger_serials}")

            raw_start_date = form.cleaned_data['start_time']  
            raw_end_date = form.cleaned_data['end_time']

            # Adjust the dates:
            # Start time: Midnight on the day after the start_date
            # End time: 23:59 on the day before the end_date
            adjusted_start_date = raw_start_date + timedelta(days=1)
            adjusted_end_date = raw_end_date

            if adjusted_start_date > adjusted_end_date:
                form.add_error(None, 'After adjustment, the start date is after the end date.')
                return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

            # Convert dates to UTC datetime using Django's timezone utility
            start_date_utc = timezone.make_aware(
                datetime.combine(adjusted_start_date, datetime.min.time()), 
                dt_timezone.utc
            )
            end_date_utc = timezone.make_aware(
                datetime.combine(adjusted_end_date, datetime.min.time()), 
                dt_timezone.utc
            )
            print(start_date_utc, end_date_utc)
            start_timestamp = int(start_date_utc.timestamp())
            end_timestamp = int(end_date_utc.timestamp())

            app_logger.debug("Fetching logger data within the date range...")

            # Fetching logger data
            external_logger_data = fetch_logger_data(external_logger_serial, start_timestamp, end_timestamp)
            # Validate if the logger exists

            if not LoggerModel.objects.filter(serial_number=external_logger_serial).exists():
                form.add_error('external_logger', 'Sensor with the provided serial number does not exist.')
                return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})
            if external_logger_data is None:
                form.add_error('external_logger', 'No data found for the external logger within the specified date range.')
                return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})
            else: 
                form.errors.pop('external_logger', None)

            combined_logger_data_list = []

            app_logger.debug("Inspecting form data before generating the report:")
            app_logger.debug(f"Form cleaned_data: {form.cleaned_data}")
            for i, room in enumerate(room_formset.cleaned_data):
                app_logger.debug(f"Room {i} data: {room}")
                app_logger.debug(f"Room {i} name: {room.get('room_name')}")
                app_logger.debug(f"Room {i} monitor area: {room.get('room_monitor_area')}")
                app_logger.debug(f"Room {i} mould visible: {room.get('room_mould_visible')}")
                app_logger.debug(f"Room {i} ambient logger: {room.get('room_ambient_logger')}")
                app_logger.debug(f"Room {i} surface logger: {room.get('room_surface_logger')}")

            for index, room_data in enumerate(room_formset.cleaned_data):
                # Extracting problem_room and monitor_area from the formset
                problem_room = room_data.get('room_name')
                monitor_area = room_data.get('room_monitor_area')

                ambient_serial = normalize_logger_serial(room_data.get('room_ambient_logger'))
                surface_serial = normalize_logger_serial(room_data.get('room_surface_logger'))

                ambient_logger_data = fetch_logger_data(ambient_serial, start_timestamp, end_timestamp)
                surface_logger_data = fetch_logger_data(surface_serial, start_timestamp, end_timestamp)

                print(f"ambient_logger_data: {ambient_logger_data}")
                print(f"surface_logger_data: {surface_logger_data}")

                if ambient_logger_data is None:
                    room_formset.forms[index].add_error(
                        'room_ambient_logger', 
                        'No data found for the ambient logger within the specified date range.'
                    )
                if surface_logger_data is None:
                    room_formset.forms[index].add_error(
                        'room_surface_logger', 
                        'No data found for the surface logger within the specified date range.'
                    )

                if not LoggerModel.objects.filter(serial_number=ambient_serial).exists():
                    room_formset.forms[index].add_error(
                        'room_ambient_logger', 
                        'Sensor with the provided serial number does not exist.'
                    )
                if not LoggerModel.objects.filter(serial_number=surface_serial).exists():
                    room_formset.forms[index].add_error(
                        'room_surface_logger', 
                        'Sensor with the provided serial number does not exist.'
                    )

                # Proceed only if both ambient and surface data are available
                if ambient_logger_data is None or surface_logger_data is None:
                    continue

                # Assume unique renaming before merges
                ambient_logger_data.rename(columns={'surface_temperature': 'AmbientSurfaceTemp'}, inplace=True)
                surface_logger_data.rename(columns={'surface_temperature': 'SurfaceLoggerTemp'}, inplace=True)

                # Combine the logger data based on the timestamp
                combined_data = pd.merge_asof(
                    external_logger_data, 
                    ambient_logger_data, 
                    on='timestamp', 
                    direction='nearest'
                )
                combined_data = pd.merge_asof(
                    combined_data, 
                    surface_logger_data, 
                    on='timestamp', 
                    direction='nearest'
                )

                app_logger.debug(f"Columns in combined_data after merge: {combined_data.columns.tolist()}")

                # Rename columns to match expected names
                combined_data.rename(columns={
                    'air_temperature_y': 'IndoorAirTemp',
                    'humidity_y': 'IndoorRelativeH',
                    'air_temperature_x': 'OutdoorAirTemp',
                    'humidity_x': 'OutdoorRelativeH',
                    'AmbientSurfaceTemp': 'SurfaceTempAmbient',  
                    'SurfaceLoggerTemp': 'SurfaceTemp',
                }, inplace=True)

                # Convert the 'timestamp' column to a human-readable format
                combined_data['timestamp'] = pd.to_datetime(
                    combined_data['timestamp'], 
                    unit='s'
                ).dt.strftime('%d/%m/%Y %H:%M:%S')

                app_logger.debug(f"Renamed Data Columns: {combined_data.columns}")

                # Initialize RoomData with problem_room and monitor_area
                app_logger.debug(f"Initializing RoomData with room_name={problem_room} and monitor_area={monitor_area}")

                if all(col in combined_data.columns for col in [
                    'IndoorAirTemp', 
                    'IndoorRelativeH', 
                    'SurfaceTemp', 
                    'OutdoorAirTemp', 
                    'OutdoorRelativeH'
                ]):
                    combined_data = combined_data[
                        ['timestamp', 'IndoorAirTemp', 'IndoorRelativeH', 'SurfaceTemp', 'OutdoorAirTemp', 'OutdoorRelativeH']
                    ]
                else:
                    return HttpResponse(
                        f"Expected columns not found in combined data: {combined_data.columns.tolist()}"
                    )

                # Save DataFrame to a temporary CSV file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmpfile:
                    combined_data.to_csv(tmpfile.name, index=False)
                    csv_file_paths.append(tmpfile.name)

                # Initialize RoomData with problem_room and monitor_area
                room_data_instance = RoomData(
                    datafile=combined_data,
                    index=index,
                    start_time=start_date_utc,
                    end_time=end_date_utc,
                    problem_room=problem_room,
                    monitor_area=monitor_area
                )

                app_logger.debug(f"RoomData instance created: {room_data_instance.get_summary()}")

            # Collect images (ensure only available images are passed)
            image_property = save_uploaded_file(form.cleaned_data.get('external_picture'))
            image_logo = save_uploaded_file(form.cleaned_data.get('company_logo'))
            image_indoor1 = room_pictures[0] if len(room_pictures) > 0 else ''
            image_indoor2 = room_pictures[1] if len(room_pictures) > 1 else ''
            image_indoor3 = room_pictures[2] if len(room_pictures) > 2 else ''
            image_indoor4 = room_pictures[3] if len(room_pictures) > 3 else ''

            app_logger.debug(
                f"Images collected: Image_property={image_property}, image_logo={image_logo}"
            )
            app_logger.debug(
                f"Images collected: Image_indoor1={image_indoor1}, Image_indoor2={image_indoor2}, "
                f"Image_indoor3={image_indoor3}, Image_indoor4={image_indoor4}"
            )

            # Convert timedelta to total seconds to make it JSON serializable for Celery
            monitor_time_seconds = (end_date_utc - start_date_utc).total_seconds()

            form_data = {
                'surveyor': form.cleaned_data['surveyor'],
                'inspectiontime': timezone.now(),
                'company': form.cleaned_data['company'],
                'Address': form.cleaned_data['property_address'],
                'occupied': form.cleaned_data['occupied'],
                'monitor_time': monitor_time_seconds,
                'occupied_during_all_monitoring': form.cleaned_data['occupied_during_all_monitoring'],
                'occupant_number': form.cleaned_data['number_of_occupants'],
                'Problem_rooms': [
                    room.get('room_name', 'Unknown Room') 
                    for room in room_formset.cleaned_data
                ],
                'Monitor_areas': [
                    room.get('room_monitor_area', 'Unknown Area') 
                    for room in room_formset.cleaned_data
                ],
                'moulds': [
                    room.get('room_mould_visible', 'No Data') 
                    for room in room_formset.cleaned_data
                ],
                'Image_property': image_property,
                'Image_logo': image_logo,
                'comment': form.cleaned_data['notes'],
                'datafiles': csv_file_paths,  # Pass the path to the CSV file
                'room_pictures': room_pictures,
                'Image_indoor1': image_indoor1,
                'Image_indoor2': image_indoor2,
                'Image_indoor3': image_indoor3,
                'Image_indoor4': image_indoor4,
            }

            app_logger.debug("Form data prepared. Calling RPTGen...")
            app_logger.debug(f"Form data being sent to RPTGen: {form_data}")

            # Prepare data for the Celery task
            task_data = {
                'report_id': report_instance.id,
                'form_data': form_data,
                'monitor_time': monitor_time_seconds,
            }

            # Create a Payment instance
            payment = Payment.objects.create(
                user=user,
                report=report_instance,
                amount=Decimal('9.99'),  # Set the appropriate amount
                currency='GBP',  # Updated to GBP as per user code
            )
            
            app_logger.debug("Payment instance created. Initiating Celery task...")

            # Start the Celery task for report generation
            task = generate_report_task.delay(task_data)

            # Create a Stripe Checkout Session
            domain_url = request.build_absolute_uri('/')[:-1]  # Remove the trailing slash

            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'gbp',
                                'product_data': {
                                    'name': 'Report Generation',
                                },
                                'unit_amount': int(payment.amount * 100),  # Amount in pence
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url=domain_url + reverse('payments:success', kwargs={'task_id': task.id}),
                    cancel_url=domain_url + reverse('payments:cancel'),  # Corrected
                    metadata={
                        'payment_id': payment.id,
                        'task_id': task.id,
                    },
                )
                return JsonResponse({'checkout_url': checkout_session.url})        
            except Exception as e:
                app_logger.error(f"Stripe Checkout Session creation failed: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
          
   
def historical_reports_view(request):
    reports = Report.objects.filter(report_file__isnull=False, user=request.user).order_by('-id')
    return render(request, 'reports/historical_reports.html', {'reports': reports})

@login_required
def report_detail_view(request, report_id):
    report = get_object_or_404(Report, id=report_id, user=request.user)
    return render(request, 'reports/historical_reports.html', {'report': report})

@login_required
def download_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        file_path = safe_join(settings.MEDIA_ROOT, report.report_file.name)
        print(file_path)
        if not report.report_file:
            raise Http404("No file found.")
        
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        else:
            raise Http404("No file found.")
    except Report.DoesNotExist:
        raise Http404("Report does not exist.")
    except ValueError:
        raise Http404("Invalid file path.")
    
@login_required
def manuals_view (request):
    all_manuals = Downloads.objects.all()
    return render(request, "reports/manuals.html", {'all_manuals':all_manuals})

@login_required
def manual_download(request, download_id):
    manual = get_object_or_404(Downloads, id=download_id)
    try:
        # Extract just the basename of the file
        filename = manual.file.name.split('/')[-1]
        response = FileResponse(manual.file.open('rb'), as_attachment=True, filename=filename)
        return response
    except FileNotFoundError:
        raise Http404("File does not exist")
    

@login_required
def task_status(request, task_id):
    """
    Returns the current status of a Celery task.
    """
    try:
        task = AsyncResult(task_id)
        if not task:
            raise Http404("Task not found")
        
        if task.state == 'PENDING':
            # Task is yet to start
            response = {
                'state': task.state,
                'status': 'Pending...',
            }
        elif task.state == 'PROGRESS':
            # Task is in progress
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', ''),
            }
        elif task.state == 'SUCCESS':
            # Task completed successfully
            response = {
                'state': task.state,
                'result': task.info.get('result', ''),
            }
        elif task.state == 'FAILURE':
            # Task failed
            response = {
                'state': task.state,
                'status': str(task.info),  # Exception message
            }
        else:
            # Other states
            response = {
                'state': task.state,
                'status': task.info.get('status', '') if task.info else '',
            }

    except Exception as e:
        response = {
            'error': str(e),
        }
        return JsonResponse(response, status=500)
    
    return JsonResponse(response)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase, e.g., update payment status
        payment_id = session['metadata']['payment_id']
        task_id = session['metadata']['task_id']

        # Update the Payment instance
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.payment_status = 'paid'
            payment.save()

            # Optionally, trigger the Celery task to generate the report if not already started
            # generate_report_task.delay({'report_id': payment.report.id, ...})
        except Payment.DoesNotExist:
            app_logger.error(f"Payment with ID {payment_id} does not exist.")

    return HttpResponse(status=200)

@login_required
def payment_success(request, task_id):
    """
    View to handle successful payment and display report status.
    """
    return render(request, 'payments/success.html', {'task_id': task_id})

@login_required
def payment_cancel(request):
    """
    View to handle canceled payments.
    """
    return render(request, 'payments/cancel.html')