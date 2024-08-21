import logging
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone  # Import timezone as dt_timezone to avoid confusion
from .forms import ReportForm, RoomFormSet
from core.models import Logger, Logger_Data, Room, User
from .config import ReportConfig
from .utils import PCAdataTool
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')
        
        if form.is_valid() and room_formset.is_valid():
            logger.debug("Form and formset are valid.")

            # Check if the user exists in the database
            if not User.objects.filter(id=request.user.id).exists():
                return HttpResponse('User not found.', status=400)
            
            # Save the report instance
            report = form.save(commit=False)
            report.user = request.user  # Set the user to the currently logged-in user
            report.save()

            # Save the rooms and associate them with the report
            rooms = room_formset.save(commit=False)
            for room in rooms:
                room.report = report
                room.save()

            logger.debug("Rooms have been saved.")

            # Prepare logger serial numbers
            ambient_logger_serials = []
            surface_logger_serials = []

            for room_data in room_formset.cleaned_data:
                ambient_logger_serial = room_data.get('room_ambient_logger')
                surface_logger_serial = room_data.get('room_surface_logger')
                if ambient_logger_serial:
                    ambient_logger_serials.append(ambient_logger_serial)
                if surface_logger_serial:
                    surface_logger_serials.append(surface_logger_serial)

            # Fetch data from form
            property_address = form.cleaned_data['property_address']
            company_name = form.cleaned_data['company']
            surveyor_name = form.cleaned_data['surveyor']
            report_date = timezone.now()
            external_picture = form.cleaned_data['external_picture']
            
            # Logger data from form
            external_logger_serial = form.cleaned_data['external_logger']

            # Additional data
            occupied = form.cleaned_data['occupied']
            occupied_during_all_monitoring = form.cleaned_data['occupied_during_all_monitoring']
            number_of_occupants = form.cleaned_data['number_of_occupants']
            notes = form.cleaned_data['notes']
            
            start_date = form.cleaned_data['start_time']
            end_date = form.cleaned_data['end_time']

            # Convert dates to UTC datetime
            start_date_utc = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), dt_timezone.utc)
            end_date_utc = timezone.make_aware(datetime.combine(end_date, datetime.max.time()), dt_timezone.utc)

            logger.debug("Checking logger existence...")
            # Check logger existence
            external_logger = Logger.objects.filter(serial_number=external_logger_serial).first()
            ambient_loggers = Logger.objects.filter(serial_number__in=ambient_logger_serials)
            surface_loggers = Logger.objects.filter(serial_number__in=surface_logger_serials)

            if not external_logger or not ambient_loggers.exists() or not surface_loggers.exists():
                return HttpResponse('One or more loggers not found.')
            
            logger.debug("Fetching logger data within the date range...")

            # Query Logger_Data for the date range
            try:
                external_logger_data = Logger_Data.objects.filter(
                    logger=external_logger, timestamp__range=(start_date_utc, end_date_utc)
                )
                ambient_logger_data = Logger_Data.objects.filter(
                    logger__in=ambient_loggers, timestamp__range=(start_date_utc, end_date_utc)
                )
                surface_logger_data = Logger_Data.objects.filter(
                    logger__in=surface_loggers, timestamp__range=(start_date_utc, end_date_utc)
                )

                if not (external_logger_data.exists() and ambient_logger_data.exists() and surface_logger_data.exists()):
                    return HttpResponse('No data found for the specified date range and loggers.')
                
                logger.debug("Preparing data for PCA report generation...")
                # Prepare report data for PCA processing
                form_data = {
                    'property_address': property_address,
                    'company_name': company_name,
                    'surveyor_name': surveyor_name,
                    'report_date': report_date,
                    'external_picture': external_picture,
                    'external_logger': external_logger,
                    'ambient_logger': ambient_loggers,
                    'surface_logger': surface_loggers,
                    'start_date': start_date_utc,
                    'end_date': end_date_utc,
                    'external_logger_data': external_logger_data,
                    'ambient_logger_data': ambient_logger_data,
                    'surface_logger_data': surface_logger_data,
                    'occupied': occupied,
                    'occupied_during_all_monitoring': occupied_during_all_monitoring,
                    'number_of_occupants': number_of_occupants,
                    'notes': notes,
                    'rooms': room_formset.cleaned_data, 
                }
                
                logger.debug("Calling PCAdataTool.RPTGen to generate the report...")
                # Process the report data
                PCAdataTool.RPTGen(form_data)
                
                return HttpResponse('Report generated successfully.')

            except Logger_Data.DoesNotExist:
                logger.error("Logger_Data.DoesNotExist: Data not found.")
                return HttpResponse('Data not found.')

        else:
            # If form is not valid, re-render the form with error messages
            logger.error("Form or formset validation failed.")
            logger.error(f"Form validation failed with errors: {form.errors}")
            return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

    else:
        form = ReportForm()
        room_formset = RoomFormSet(prefix='rooms')

    return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})