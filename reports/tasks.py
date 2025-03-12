from __future__ import absolute_import
import time
from celery import shared_task


import logging
import os
import tempfile
import pandas as pd
from celery import shared_task, current_task
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from .utils.PCAdataTool import RPTGen
from .utils.normalize_logger_serial import normalize_logger_serial  
from .utils.resize_and_save_image import resize_and_save_image
from .utils.room_data import RoomData
from core.models import Logger as LoggerModel, Logger_Data, Room, Report
from django.core.files import File


logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger(__name__)

@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param


@shared_task(bind=True)
def generate_report_task(self, report_id, csv_file_paths, serialized_form_data):
    
    try:
        report = get_object_or_404(Report, id=report_id)
        app_logger.debug(f"Report retrieved: {report}")

    # Deserealizing inspectiontime passed as an ISO format string
        inspectiontime_str = serialized_form_data['inspection_time']
        if isinstance(inspectiontime_str, str):
            inspectiontime = datetime.fromisoformat(inspectiontime_str)
        else:
            inspectiontime = inspectiontime_str
                
        # Extract all necessary parameters from the report instance
        datafiles = csv_file_paths  
        surveyor = report.surveyor
        company = report.company
        address = report.property_address
        occupied = report.occupied
        monitor_time = timedelta(seconds=serialized_form_data['monitor_time'])
        occupied_during_all_monitoring = report.occupied_during_all_monitoring
        occupant_number = report.number_of_occupants
        Problem_rooms = serialized_form_data['Problem_rooms']  # List
        Monitor_areas = serialized_form_data['Monitor_areas']  # List
        moulds = serialized_form_data['moulds']# List
        Image_property = serialized_form_data['Image_property']
        room_pictures = [str(pic) for pic in serialized_form_data['room_pictures'] if pic]
        Image_indoor1 = serialized_form_data['Image_indoor1']
        Image_indoor2 = serialized_form_data['Image_indoor2']
        Image_indoor3 = serialized_form_data['Image_indoor3'] 
        Image_indoor4 = serialized_form_data['Image_indoor4'] 
        Image_logo = serialized_form_data['Image_logo'] 
        comment = serialized_form_data['comment']

        # Call the RPTGen function with all required parameters
        
        
        filename = RPTGen(
            datafiles=datafiles,
            surveyor=surveyor,
            inspectiontime=inspectiontime,
            company=company,
            Address=address,
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
            popup=True
        )
        
        return {'status': 'success', 'pdf_url': filename}
    except Report.DoesNotExist:
        app_logger.error(f'Report with id {report_id} does not exist.')
        return {'status': 'error', 'message': 'Report does not exist.'}
    except Exception as e:
        app_logger.exception(f'Error generating report: {e}')
        return {'status': 'error', 'message': str(e)}


