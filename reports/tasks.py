from md_app.celery import shared_task
from celery.exceptions import Ignore
import time
from .utils import PCAdataTool


from md_app.celery import shared_task
from .utils import RPTGen
from django.conf import settings
import os
import datetime

@shared_task(bind=True)
def generate_report(self, form_data):
    """
    Celery task to generate a PDF report based on form data.
    """
    try:
        # Define a progress callback function
        def progress_callback(current, message):
            self.update_state(state='PROGRESS',
                              meta={'current': current, 'total': 100, 'status': message})

        # Extract necessary data from form_data
        datafiles = form_data.get('datafiles')  # List of data file paths
        surveyor = form_data.get('surveyor')
        inspectiontime = form_data.get('inspectiontime')  # Should be a datetime object
        company = form_data.get('company')
        Address = form_data.get('Address')
        occupied = form_data.get('occupied')
        monitor_time = form_data.get('monitor_time')  # Should be a timedelta object
        occupied_during_all_monitoring = form_data.get('occupied_during_all_monitoring')
        occupant_number = form_data.get('occupant_number')
        Problem_rooms = form_data.get('Problem_rooms')  # List of problem rooms
        Monitor_areas = form_data.get('Monitor_areas')  # List of monitor areas
        moulds = form_data.get('moulds')  # List of booleans indicating visible mould
        Image_property = form_data.get('Image_property')  # Path to property image
        room_pictures = form_data.get('room_pictures')  # List of room picture paths
        Image_indoor1 = form_data.get('Image_indoor1')
        Image_indoor2 = form_data.get('Image_indoor2')
        Image_indoor3 = form_data.get('Image_indoor3')
        Image_indoor4 = form_data.get('Image_indoor4')
        Image_logo = form_data.get('Image_logo')  # Path to company logo
        comment = form_data.get('comment')

        # Call RPTGen with the extracted data and the progress callback
        pdf_file_path = RPTGen(
            datafiles=datafiles,
            surveyor=surveyor,
            inspectiontime=inspectiontime,
            company=company,
            Address=Address,
            occupied=occupied,
            monitor_time=monitor_time,
            occupied_during_all_monitoring=occupied_during_all_monitoring,
            occupant_number=occupant_number,
            Problem_rooms=Problem_rooms,
            Monitor_areas=Monitor_areas,
            moulds=moulds,
            Image_property=Image_property,
            room_pictures=room_pictures,
            Image_indoor1=Image_indoor1,
            Image_indoor2=Image_indoor2,
            Image_indoor3=Image_indoor3,
            Image_indoor4=Image_indoor4,
            Image_logo=Image_logo,
            comment=comment,
            popup=True,
            progress_callback=progress_callback  # Pass the callback function
        )

        # Upon successful completion
        return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': pdf_file_path}

    except Exception as e:
        # Handle exceptions and mark the task as failed
        self.update_state(state='FAILURE', meta={'exc_message': str(e)})
        raise e