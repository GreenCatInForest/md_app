import logging
import os
import tempfile
from django.shortcuts import render, HttpResponse
from django.http import FileResponse
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from .forms import ReportForm, RoomFormSet
from core.models import Logger as LoggerModel, Logger_Data, Room
from .utils import PCAdataTool  
from .utils.room_data import RoomData
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

def save_uploaded_file(uploaded_file):
    # Save the InMemoryUploadedFile to a temporary file and return the file path
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    return ''

def save_uploaded_room_pic(uploaded_file):
    # Save the InMemoryUploadedFile to a temporary file and return the file path
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    return ''


@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')

        if form.is_valid() and room_formset.is_valid():
            app_logger.debug("Form and formset are valid.")

            # Save the Report object first
            report_instance = form.save(commit=False)
            report_instance.user = request.user

            if 'external_picture' in request.FILES:
                report_instance.external_picture = request.FILES['external_picture']
                external_picture_preview = request.FILES['external_picture']

            if 'company_logo' in request.FILES:
                report_instance.company_logo = request.FILES['company_logo']
                preview_company_logo = request.FILES['company_logo']

            report_instance.save()

            # Initialize list to store room pictures
            room_pictures = []
            

            # Save Room formset with the associated Report instance
            for room_form in room_formset:
                room_instance = room_form.save(commit=False)
                room_instance.report = report_instance

                # Correctly handle room picture files
                room_picture_file = room_form.cleaned_data.get('room_picture')
                if room_picture_file:
                    room_instance.room_picture = room_picture_file
                    # Save uploaded file and store path
                    room_picture_path = save_uploaded_file(room_picture_file)
                    room_pictures.append(room_picture_path)

                room_instance.save()

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

            app_logger.debug("Inspecting form data before generating the report:")
            app_logger.debug(f"Form cleaned_data: {form.cleaned_data}")
            for i, room in enumerate(room_formset.cleaned_data):
                app_logger.debug(f"Room {i} data: {room}")
                app_logger.debug(f"Room {i} name: {room.get('room_name')}")
                app_logger.debug(f"Room {i} monitor area: {room.get('room_monitor_area')}")
                app_logger.debug(f"Room {i} mould visible: {room.get('room_mould_visible')}")

            for index, room_data in enumerate(room_formset.cleaned_data):
                # Extracting problem_room and monitor_area from the formset
                problem_room = room_data.get('room_name')
                monitor_area = room_data.get('room_monitor_area')

                ambient_serial = normalize_logger_serial(room_data.get('room_ambient_logger'))
                surface_serial = normalize_logger_serial(room_data.get('room_surface_logger'))

                ambient_logger_data = fetch_logger_data(ambient_serial, start_timestamp, end_timestamp)
                surface_logger_data = fetch_logger_data(surface_serial, start_timestamp, end_timestamp)

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

                room_data_instance = RoomData(
                    datafile=combined_data,
                    index=index,
                    start_time=start_date_utc,
                    end_time=end_date_utc,
                    problem_room=problem_room,
                    monitor_area=monitor_area
                )

                app_logger.debug(f"RoomData instance created: {room_data_instance.get_summary()}")

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
            image_property = save_uploaded_file(form.cleaned_data.get('external_picture'))
            image_logo = save_uploaded_file(form.cleaned_data.get('company_logo'))
            image_indoor1 = room_pictures[0] if len(room_pictures) > 0 else ''
            image_indoor2 = room_pictures[1] if len(room_pictures) > 1 else ''
            image_indoor3 = room_pictures[2] if len(room_pictures) > 2 else ''
            image_indoor4 = room_pictures[3] if len(room_pictures) > 3 else ''

            app_logger.debug(f"Images collected: Image_property={image_property}, image_logo={image_logo}")
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
                'occupied_during_all_monitoring': form.cleaned_data['occupied_during_all_monitoring'],
                'occupant_number': form.cleaned_data['number_of_occupants'],
                'Problem_rooms': [room.get('room_name', 'Unknown Room') for room in room_formset.cleaned_data],
                'Monitor_areas': [room.get('room_monitor_area', 'Unknown Area') for room in room_formset.cleaned_data],
                'moulds': [room.get('room_mould_visible', 'No Data') for room in room_formset.cleaned_data],
                'Image_property': image_property,
                'Image_logo': image_logo,
                'comment': form.cleaned_data['notes'],
                'datafiles': [datafile_path],  # Pass the path to the CSV file
                'room_pictures': room_pictures,
                'Image_indoor1': image_indoor1,
                'Image_indoor2': image_indoor2,
                'Image_indoor3': image_indoor3,
                'Image_indoor4': image_indoor4,
            }

            app_logger.debug("Form data prepared. Calling RPTGen...")
            app_logger.debug(f"Form data being sent to RPTGen: {form_data}")

            # Generate the report
            try:
                pdf_file_path = PCAdataTool.RPTGen(**form_data)
                if not pdf_file_path or not os.path.exists(pdf_file_path):
                    raise Exception("PDF file was not generated or found.")
                app_logger.debug(f"Generated PDF file path: {pdf_file_path}")
                return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf', filename=os.path.basename(pdf_file_path))
            except Exception as e:
                app_logger.error(f"Error generating report: {e}")
                return HttpResponse('Error generating report.', status=500)

        else:
            app_logger.error("Form or formset validation failed.")
            app_logger.error(f"Form errors: {form.errors}")
            app_logger.error(f"RoomFormSet errors: {room_formset.errors}")
            return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

    else:
        room_formset = RoomFormSet(queryset=Room.objects.none(), prefix='rooms')
        form = ReportForm()
        return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})