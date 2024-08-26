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
    
