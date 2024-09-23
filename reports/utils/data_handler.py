
import pandas as pd
import logging
from core.models import Logger as LoggerModel, Logger_Data

app_logger = logging.getLogger(__name__)

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

import pandas as pd


class RoomData:
    def __init__(self, datafile, index, start_time=None, end_time=None, problem_room=None, monitor_area=None, room_picture=None):
        self.datafile = datafile
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.problem_room = problem_room
        self.monitor_area = monitor_area
        self.cleaned_data = self.process_data(datafile)
        self.room_picture = room_picture
    
    def process_data(self, datafile):
        if isinstance(datafile, pd.DataFrame):
            return datafile
        else:
            return pd.read_csv(datafile)

    def get_summary(self):
        return {
            'index': self.index,
            'problem_room': self.problem_room,
            'monitor_area': self.monitor_area,
            'data_summary': self.cleaned_data.describe().to_dict()
        }
    def get_data(self):
        return self.cleaned_data.to_dict()
    
    def get_room_picture(self):
        return self.room_picture
    
