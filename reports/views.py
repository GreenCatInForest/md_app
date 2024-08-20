
import logging

from django.shortcuts import render, HttpResponse
from django.utils import timezone
from datetime import datetime
from .forms import ReportForm
from core.models import Logger, Logger_Data
from .config import ReportConfig
from .utils import PCAdataTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        
        if form.is_valid():
            logger.debug("Form is valid.")
            # Fetch data from form
            property_address = form.cleaned_data['property_address']
            company_name = form.cleaned_data['company']
            surveyor_name = form.cleaned_data['surveyor']
            room_name = form.cleaned_data['room_name']
            report_date = form.cleaned_data['report_timestamp']
            external_picture = form.cleaned_data['external_picture']
            
            # Logger data from form
            external_logger_serial = form.cleaned_data['external_logger']
            ambient_logger_serial = form.cleaned_data['room_ambient_logger']
            surface_logger_serial = form.cleaned_data['room_surface_logger']
            
            # Additional data
            occupied = form.cleaned_data['occupied']
            occupied_during_all_monitoring = form.cleaned_data['occupied_during_all_monitoring']
            number_of_occupants = form.cleaned_data['number_of_occupants']
            notes = form.cleaned_data['notes']
            room_picture = form.cleaned_data['room_picture']
            room_monitor_area = form.cleaned_data['room_monitor_area']
            room_mould_visible = form.cleaned_data['room_mould_visible']
            
            start_date = form.cleaned_data['start_time']
            end_date = form.cleaned_data['end_time']

            # Convert dates to UTC datetime
            start_date_utc = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), timezone.utc)
            end_date_utc = timezone.make_aware(datetime.combine(end_date, datetime.max.time()), timezone.utc)

            logger.debug("Checking logger existence...")
            # Check logger existence
            external_logger = Logger.objects.filter(serial_number=external_logger_serial).first()
            ambient_logger = Logger.objects.filter(serial_number=ambient_logger_serial).first()
            surface_logger = Logger.objects.filter(serial_number=surface_logger_serial).first()

            if not (external_logger and ambient_logger and surface_logger):
                return HttpResponse('One or more loggers not found.')
            
            logger.debug("Fetching logger data within the date range...")

            # Query Logger_Data for the date range
            try:
                external_logger_data = Logger_Data.objects.filter(
                    logger=external_logger, timestamp__range=(start_date_utc, end_date_utc)
                )
                ambient_logger_data = Logger_Data.objects.filter(
                    logger=ambient_logger, timestamp__range=(start_date_utc, end_date_utc)
                )
                surface_logger_data = Logger_Data.objects.filter(
                    logger=surface_logger, timestamp__range=(start_date_utc, end_date_utc)
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
                    'room_name': room_name,
                    'external_picture': external_picture,
                    'external_logger': external_logger,
                    'ambient_logger': ambient_logger,
                    'surface_logger': surface_logger,
                    'start_date': start_date_utc,
                    'end_date': end_date_utc,
                    'external_logger_data': external_logger_data,
                    'ambient_logger_data': ambient_logger_data,
                    'surface_logger_data': surface_logger_data,
                    'occupied': occupied,
                    'occupied_during_all_monitoring': occupied_during_all_monitoring,
                    'number_of_occupants': number_of_occupants,
                    'notes': notes,
                    'room_monitor_area': room_monitor_area,
                    'room_mould_visible': room_mould_visible,
                    'company_logo': form.cleaned_data['company_logo'],
                    'room_picture': room_picture
                }
                logger.debug("Calling PCAdataTool.RPTGen to generate the report...")
                # Process the report data
                # Process the report data
                PCAdataTool.RPTGen(form_data)
                
                return HttpResponse('Report generated successfully.')

            except Logger_Data.DoesNotExist:
                logger.error("Logger_Data.DoesNotExist: Data not found.")
                return HttpResponse('Data not found.')

        else:
            # If form is not valid, re-render the form with error messages
            logger.error("Form validation failed.")
            logger.error(f"Form validation failed with errors: {form.errors}")
            return render(request, 'reports/report.html', {'form': form})

    else:
        form = ReportForm()

    return render(request, 'reports/report.html', {'form': form})
