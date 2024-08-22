import logging
from django.shortcuts import render, HttpResponse
from django.http import FileResponse
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from .forms import ReportForm, RoomFormSet
from core.models import Logger, Logger_Data, Room, User
from .config import ReportConfig
from .utils import PCAdataTool
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import pandas as pd
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

def fetch_logger_data(logger_serial, start_timestamp, end_timestamp):
    logger = Logger.objects.get(serial_number=logger_serial)
    data = Logger_Data.objects.filter(logger=logger, timestamp__range=(start_timestamp, end_timestamp))
    return pd.DataFrame(list(data.values()))

@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        room_formset = RoomFormSet(request.POST, request.FILES, prefix='rooms')
        
        if form.is_valid() and room_formset.is_valid():
            logger.debug("Form and formset are valid.")

            # Fetch logger data from form
            external_logger_serial = form.cleaned_data['external_logger']
            ambient_logger_serials = [room_data.get('room_ambient_logger') for room_data in room_formset.cleaned_data]
            surface_logger_serials = [room_data.get('room_surface_logger') for room_data in room_formset.cleaned_data]

            # Convert dates to UTC datetime
            start_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['start_time'], datetime.min.time()), dt_timezone.utc)
            end_date_utc = timezone.make_aware(datetime.combine(form.cleaned_data['end_time'], datetime.max.time()), dt_timezone.utc)

            start_timestamp = int(start_date_utc.timestamp())
            end_timestamp = int(end_date_utc.timestamp())

            logger.debug("Fetching logger data within the date range...")

            # Fetching logger data
            external_logger_data = fetch_logger_data(external_logger_serial, start_timestamp, end_timestamp)
            combined_logger_data_list = []

            for ambient_serial, surface_serial in zip(ambient_logger_serials, surface_logger_serials):
                ambient_logger_data = fetch_logger_data(ambient_serial, start_timestamp, end_timestamp)
                surface_logger_data = fetch_logger_data(surface_serial, start_timestamp, end_timestamp)
                
                # Combine the logger data based on the timestamp
                combined_data = pd.merge_asof(external_logger_data, ambient_logger_data, on='timestamp', direction='nearest')
                combined_data = pd.merge_asof(combined_data, surface_logger_data, on='timestamp', direction='nearest')
                
                logger.debug(f"Columns in combined_data after merge: {combined_data.columns.tolist()}")

                # Rename columns to match expected names
                combined_data.rename(columns={
                    'air_temperature_x': 'IndoorAirTemp',
                    'humidity_x': 'IndoorRelativeH',
                    'surface_temperature_x': 'SurfaceTemp',
                    'air_temperature_y': 'OutdoorAirTemp',
                    'humidity_y': 'OutdoorRelativeH',
                    'surface_temperature': 'SurfaceTemp',
                    # Add more mappings if needed
                }, inplace=True)

                # Print the columns to debug
                print("Renamed Data Columns:", combined_data.columns)

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

            # If you want to allow the user to download the CSV for testing
            csv_buffer = StringIO()
            all_rooms_combined_data.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            # Return the CSV as a downloadable file
            response = HttpResponse(csv_buffer, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="combined_logger_data.csv"'
            return response

        else:
            # If form is not valid, re-render the form with error messages
            logger.error("Form or formset validation failed.")
            return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})

    else:
        room_formset = RoomFormSet(queryset=Room.objects.none(), prefix='rooms')
        form = ReportForm()
        return render(request, 'reports/report.html', {'form': form, 'room_formset': room_formset})