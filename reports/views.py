import logging
import os
import tempfile
from django.shortcuts import render, HttpResponse
from django.http import FileResponse
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from .forms import ReportForm, RoomFormSet
from core.models import Logger as LoggerModel, Logger_Data, Room
from .utils import PCAdataTool  # Assuming PCAdataTool is a module
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import pandas as pd
from io import StringIO
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger(__name__)

User = get_user_model()

def normalize_logger_serial(serial, dash_position=3):
    """Remove non-numeric characters and reformat the logger serial input."""
    cleaned_serial = re.sub(r'\D', '', serial)
    if len(cleaned_serial) > dash_position:
        cleaned_serial = cleaned_serial[:dash_position] + '-' + cleaned_serial[dash_position:]
    return cleaned_serial

def fetch_logger_data(logger_serial, start_timestamp, end_timestamp):
    """Fetch logger data within the specified timestamp range and return as a DataFrame."""
    logger = LoggerModel.objects.get(serial_number=logger_serial)
    data = Logger_Data.objects.filter(logger=logger, timestamp__range=(start_timestamp, end_timestamp))
    return pd.DataFrame(list(data.values()))

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

@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')
        
        if form.is_valid() and room_formset.is_valid():
            app_logger.debug("Form and formset are valid.")

            # Fetch logger data from form
            external_logger_serial = normalize_logger_serial(form.cleaned_data['external_logger'])
            ambient_logger_serials = [normalize_logger_serial(room_data.get('room_ambient_logger')) for room_data in room_formset.cleaned_data]
            surface_logger_serials = [normalize_logger_serial(room_data.get('room_surface_logger')) for room_data in room_formset.cleaned_data]

            # Convert dates to UTC datetime
            start_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['start_time'], datetime.min.time()), dt_timezone.utc)
            end_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['end_time'], datetime.max.time()), dt_timezone.utc)

            start_timestamp = int(start_date_utc.timestamp())
            end_timestamp = int(end_date_utc.timestamp())

            app_logger.debug("Fetching logger data within the date range...")

            # Fetching logger data
            external_logger_data = fetch_logger_data(external_logger_serial, start_timestamp, end_timestamp)
            combined_logger_data_list = []

            for ambient_serial, surface_serial in zip(ambient_logger_serials, surface_logger_serials):
                ambient_logger_data = fetch_logger_data(ambient_serial, start_timestamp, end_timestamp)
                surface_logger_data = fetch_logger_data(surface_serial, start_timestamp, end_timestamp)
                
                # Combine the logger data based on the timestamp
                combined_data = pd.merge_asof(external_logger_data, ambient_logger_data, on='timestamp', direction='nearest')
                combined_data = pd.merge_asof(combined_data, surface_logger_data, on='timestamp', direction='nearest')
                
                app_logger.debug(f"Columns in combined_data after merge: {combined_data.columns.tolist()}")

                # Rename columns to match expected names
                combined_data.rename(columns={
                    'air_temperature_y': 'IndoorAirTemp',
                    'humidity_y': 'IndoorRelativeH',
                    'surface_temperature_x': 'SurfaceTemp',
                    'air_temperature_x': 'OutdoorAirTemp',
                    'humidity_x': 'OutdoorRelativeH',
                    'surface_temperature': 'SurfaceTemp',
                    
                    # Add more mappings if needed
                }, inplace=True)

                # Convert the 'timestamp' column to a human-readable format
                combined_data['timestamp'] = pd.to_datetime(combined_data['timestamp'], unit='s').dt.strftime('%d/%m/%Y %H:%M:%S')

                app_logger.debug(f"Renamed Data Columns: {combined_data.columns}")

                # Check if expected columns exist
                if all(col in combined_data.columns for col in ['IndoorAirTemp', 'IndoorRelativeH', 'SurfaceTemp', 'OutdoorAirTemp', 'OutdoorRelativeH']):
                    # Ensure the correct column order
                    combined_data = combined_data[['timestamp', 'IndoorAirTemp', 'IndoorRelativeH', 'SurfaceTemp', 'OutdoorAirTemp', 'OutdoorRelativeH']]
                else:
                    return HttpResponse(f"Expected columns not found in combined data: {combined_data.columns.tolist()}")

                # Append the combined data to the list
                combined_logger_data_list.append(combined_data)
            
            # Concatenate all the room data into one DataFrame for simplicity
            all_rooms_combined_data = pd.concat(combined_logger_data_list)

            all_rooms_combined_data = clean_data(all_rooms_combined_data)

            # Collect images (ensure only available images are passed)
            image_indoor1 = room_formset.cleaned_data[0].get('room_picture') if len(room_formset.cleaned_data) > 0 and room_formset.cleaned_data[0].get('room_picture') else ''
            image_indoor2 = room_formset.cleaned_data[1].get('room_picture') if len(room_formset.cleaned_data) > 1 and room_formset.cleaned_data[1].get('room_picture') else ''
            image_indoor3 = room_formset.cleaned_data[2].get('room_picture') if len(room_formset.cleaned_data) > 2 and room_formset.cleaned_data[2].get('room_picture') else ''
            image_indoor4 = room_formset.cleaned_data[3].get('room_picture') if len(room_formset.cleaned_data) > 3 and room_formset.cleaned_data[3].get('room_picture') else ''

            app_logger.debug(f"Images collected: Image_indoor1={image_indoor1}, Image_indoor2={image_indoor2}, Image_indoor3={image_indoor3}, Image_indoor4={image_indoor4}")
            
                       # Save DataFrame to a temporary CSV file if needed by RPTGen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmpfile:
                all_rooms_combined_data.to_csv(tmpfile.name, index=False)
                datafile_path = tmpfile.name

            form_data = {
                'surveyor': form.cleaned_data['surveyor'],
                'inspectiontime': timezone.now(),
                'company': form.cleaned_data['company'],
                'Address': form.cleaned_data['property_address'],
                'occupied': form.cleaned_data['occupied'],
                'monitor_time': end_date_utc - start_date_utc,
                'occupant_number': form.cleaned_data['number_of_occupants'],
                'Problem_rooms': [room.get('room_name', 'Unknown Room') for room in room_formset.cleaned_data],
                'Monitor_areas': [room.get('room_monitor_area', 'Unknown Area') for room in room_formset.cleaned_data],
                'moulds': [room.get('room_mould_visible', 'No Data') for room in room_formset.cleaned_data],
                'Image_property': form.cleaned_data.get('external_picture', ''),
                'Image_indoor1': image_indoor1 or '',
                'Image_indoor2': image_indoor2 or '',
                'Image_indoor3': image_indoor3 or '',
                'Image_indoor4': image_indoor4 or '',
                'Image_logo': form.cleaned_data['company_logo'],
                'comment': form.cleaned_data['notes'],
                'datafiles': [datafile_path]  # Pass the path to the CSV file
            }

            app_logger.debug("Form data prepared. Calling RPTGen...")

            # Generate the report
            try:
                pdf_file_path = PCAdataTool.RPTGen(**form_data)
                return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            except Exception as e:
                app_logger.error(f"Error generating report: {e}")
                return HttpResponse('Error generating report.', status=500)
            finally:
                os.remove(datafile_path)  # Clean up the temporary file

           
        else:
            app_logger.error("Form or formset validation failed.")
            app_logger.error(f"Form errors: {form.errors}")
            app_logger.error(f"RoomFormSet errors: {room_formset.errors}")
            return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

    else:
        room_formset = RoomFormSet(queryset=Room.objects.none(), prefix='rooms')
        form = ReportForm()
        return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})