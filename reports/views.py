import logging
import os
import tempfile
import re

import pandas as pd
from io import StringIO

from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import FileResponse, Http404, JsonResponse
from django.utils import timezone
from django.utils._os import safe_join
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from datetime import datetime, timezone as dt_timezone
from django.conf import settings

from .forms import ReportForm, RoomFormSet
from core.models import Logger as LoggerModel, Logger_Data, Room, Report
from .utils import PCAdataTool
from .utils.normalize_logger_serial import normalize_logger_serial  
from .utils.resize_and_save_image import resize_and_save_image
from .utils.room_data import RoomData

from .tasks import progress_callback, generate_report


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

# REDUNDAND FUNCTION
# def save_uploaded_room_pic(uploaded_file):
#     if uploaded_file:
#         temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
#         for chunk in uploaded_file.chunks():
#             temp_file.write(chunk)
#         temp_file.close()
#         return temp_file.name
#     return ''


@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')
        user = request.user 

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
                external_picture_preview = request.FILES['external_picture']

            if company_logo_file:
                report_instance.company_logo = company_logo_file
                preview_company_logo = request.FILES['company_logo']
                
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


            # Initialize list to store room pictures
            room_pictures = []
            csv_file_paths = []
            

            # Save Room formset with the associated Report instance
            for room_form in room_formset:
                room_instance = room_form.save(commit=False)

                if room_form.cleaned_data and not room_form.cleaned_data.get('DELETE', False):
                        room_instance = room_form.save(commit=False)
                        room_instance.report = report_instance

                if room_instance.pk: 
                    # Check if it's an existing room (has a primary key)
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
            ambient_logger_serials = [normalize_logger_serial(room_data.get('room_ambient_logger')) for room_data in room_formset.cleaned_data]
            surface_logger_serials = [normalize_logger_serial(room_data.get('room_surface_logger')) for room_data in room_formset.cleaned_data]
            
            print (f"External Logger Serial: {external_logger_serial}")
            print (f"Ambient Logger Serials: {ambient_logger_serials}")
            print (f"Surface Logger Serials: {surface_logger_serials}")
            
            # Convert dates to UTC datetime
            start_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['start_time'], datetime.min.time()), dt_timezone.utc)
            end_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['end_time'], datetime.max.time()), dt_timezone.utc)

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

                print (f"ambient_logger_data: {ambient_logger_data}")
                print (f"surface_logger_data: {surface_logger_data}")

                if ambient_logger_data is None:
                    room_formset.forms[index].add_error('room_ambient_logger', 'No data found for the ambient logger within the specified date range.')
                if surface_logger_data is None:
                    room_formset.forms[index].add_error('room_surface_logger', 'No data found for the surface logger within the specified date range.')

                if not LoggerModel.objects.filter(serial_number=ambient_serial).exists():
                    room_formset.forms[index].add_error('room_ambient_logger', 'Sensor with the provided serial number does not exist.')
                if not LoggerModel.objects.filter(serial_number=surface_serial).exists():
                    room_formset.forms[index].add_error('room_surface_logger', 'Sensor with the provided serial number does not exist.')
                
        
                # Assume unique renaming before merges
                ambient_logger_data.rename(columns={'surface_temperature': 'AmbientSurfaceTemp'}, inplace=True)
                surface_logger_data.rename(columns={'surface_temperature': 'SurfaceLoggerTemp'}, inplace=True)

                # Combine the logger data based on the timestamp
                combined_data = pd.merge_asof(external_logger_data, ambient_logger_data, on='timestamp', direction='nearest')
                combined_data = pd.merge_asof(combined_data, surface_logger_data, on='timestamp', direction='nearest')

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
                combined_data['timestamp'] = pd.to_datetime(combined_data['timestamp'], unit='s').dt.strftime('%d/%m/%Y %H:%M:%S')

                app_logger.debug(f"Renamed Data Columns: {combined_data.columns}")

                # Initialize RoomData with problem_room and monitor_area
                app_logger.debug(f"Initializing RoomData with room_name={problem_room} and monitor_area={monitor_area}")

                if all(col in combined_data.columns for col in ['IndoorAirTemp', 'IndoorRelativeH', 'SurfaceTemp', 'OutdoorAirTemp', 'OutdoorRelativeH']):
                    combined_data = combined_data[['timestamp', 'IndoorAirTemp', 'IndoorRelativeH', 'SurfaceTemp', 'OutdoorAirTemp', 'OutdoorRelativeH']]
                else:
                    return HttpResponse(f"Expected columns not found in combined data: {combined_data.columns.tolist()}")

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

            app_logger.debug(f"Images collected: Image_property={image_property}, image_logo={image_logo}")
            app_logger.debug(f"Images collected: Image_indoor1={image_indoor1}, Image_indoor2={image_indoor2}, Image_indoor3={image_indoor3}, Image_indoor4={image_indoor4}")

                # Save DataFrame to a temporary CSV file if needed by RPTGen


            form_data = {
                'surveyor': form.cleaned_data['surveyor'],
                'inspectiontime': timezone.now(),
                'company': form.cleaned_data['company'],
                'Address': form.cleaned_data['property_address'],
                'occupied': form.cleaned_data['occupied'],
                'monitor_time': end_date_utc - start_date_utc,
                'occupied_during_all_monitoring': form.cleaned_data['occupied_during_all_monitoring'],
                'occupant_number': form.cleaned_data['number_of_occupants'],
                'Problem_rooms': [room.get('room_name', 'Unknown Room') for room in room_formset.cleaned_data],
                'Monitor_areas': [room.get('room_monitor_area', 'Unknown Area') for room in room_formset.cleaned_data],
                'moulds': [room.get('room_mould_visible', 'No Data') for room in room_formset.cleaned_data],
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

            task = generate_report.delay(form_data)
            
            return JsonResponse({'task_id': task.id}, status=202)
        else:
            # Handle form errors
            return JsonResponse({'errors': form.errors}, status=400)

            # Generate the report
        #     try:
        #         pdf_file_path = PCAdataTool.RPTGen(**form_data)
        #         if not pdf_file_path or not os.path.exists(pdf_file_path):
        #             raise Exception("PDF file was not generated or found.")
        #         app_logger.debug(f"Generated PDF file path: {pdf_file_path}")
        #         report_instance.report_file = pdf_file_path
        #         report_instance.save()
        #         return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf', filename=os.path.basename(pdf_file_path))
        #     except Exception as e:
        #         app_logger.error(f"Error generating report: {e}")
        #         return HttpResponse('Error generating report.', status=500)

        # else:
        #     app_logger.error("Form or formset validation failed.")
        #     app_logger.error(f"Form errors: {form.errors}")
        #     app_logger.error(f"RoomFormSet errors: {room_formset.errors}")
        #     return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

    else:
        room_formset = RoomFormSet(queryset=Room.objects.none(), prefix='rooms')
        form = ReportForm()
        return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

@login_required
def historical_reports_view(request):
    reports = Report.objects.filter(report_file__isnull=False, user=request.user)
    return render(request, 'reports/historical_reports.html', {'reports': reports})

@login_required
def report_detail_view(request, report_id):
    report = get_object_or_404(Report, id=report_id, user=request.user)
    return render(request, 'reports/historical_reports.html', {'report': report})

@login_required
def download_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        file_path = safe_join(report.report_file.name)
        print(file_path)
        if not report.report_file:
            raise Http404("No file found.")
        
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        else:
            raise Http404("No file found.")
    except Report.DoesNotExist:
        raise Http404("Report does not exist.")
    except ValueError:
        raise Http404("Invalid file path.")
    
@login_required
def get_task_status(request, task_id):
    task = generate_report.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'progress': 0
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'progress': task.info.get('current', 0) / task.info.get('total', 1) * 100
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # Something went wrong in the background job
        response = {
            'state': task.state,
            'progress': 100,
            'result': str(task.info),  # this is the exception raised
        }
    return JsonResponse(response)

def report_status(request, task_id):
    return render(request, 'reports/report_status.html', {'task_id': task_id})