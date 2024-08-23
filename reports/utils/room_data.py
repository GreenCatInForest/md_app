import pandas as pd


class RoomData:
    def __init__(self, datafile, index, start_time=None, end_time=None, problem_room=None, monitor_area=None):
        self.datafile = datafile
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.problem_room = problem_room
        self.monitor_area = monitor_area
        self.cleaned_data = self.process_data(datafile)
    
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