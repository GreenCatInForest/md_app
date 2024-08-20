import pandas as pd

class ReportConfig:
    def __init__(self, property_address, company_name, surveyor_name, report_date, room_name, 
                 external_picture, external_logger, ambient_logger, surface_logger, 
                 start_date, end_date, external_logger_data, ambient_logger_data, 
                 surface_logger_data, occupied, occupied_during_all_monitoring, 
                 number_of_occupants, notes, room_monitor_area, room_mould_visible, 
                 company_logo, room_picture):
        self.property_address = property_address
        self.company_name = company_name
        self.surveyor_name = surveyor_name
        self.room_name = room_name
        self.report_date = report_date
        self.external_picture = external_picture
        self.external_logger = external_logger
        self.ambient_logger = ambient_logger
        self.surface_logger = surface_logger
        self.start_date = start_date
        self.end_date = end_date
        self.occupied = occupied
        self.occupied_during_all_monitoring = occupied_during_all_monitoring
        self.number_of_occupants = number_of_occupants
        self.notes = notes
        self.room_monitor_area = room_monitor_area
        self.room_mould_visible = room_mould_visible
        self.company_logo = company_logo
        self.room_picture = room_picture

        # Convert logger data to DataFrames
        self.external_logger_data = self._convert_to_dataframe(external_logger_data)
        self.ambient_logger_data = self._convert_to_dataframe(ambient_logger_data)
        self.surface_logger_data = self._convert_to_dataframe(surface_logger_data)

    def _convert_to_dataframe(self, logger_data):
        """Convert logger data to a Pandas DataFrame."""
        return pd.DataFrame(list(logger_data.values('timestamp', 'temperature', 'humidity'))).rename(columns={
            'timestamp': 'Time',
            'temperature': 'Temperature',
            'humidity': 'Humidity'
        })
