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
def generate_report_task(self, report_id, csv_file_paths, inspectiontime):
    
    try:
        report = Report.objects.get(id=report_id)
        app_logger.debug(f"Report retrieved: {report}")
        
        # Extract all necessary parameters from the report instance
        datafiles = csv_file_paths  
        surveyor = report.surveyor
        inspectiontime = report.inspection_time
        company = report.company
        Address = report.address
        occupied = report.occupied
        monitor_time = report.monitor_time
        occupied_during_all_monitoring = report.occupied_during_all_monitoring
        occupant_number = report.occupant_number
        Problem_rooms = report.problem_rooms  # List
        Monitor_areas = report.monitor_areas  # List
        moulds = report.moulds  # List
        Image_property = report.image_property.path if report.image_property else ''
        room_pictures = [pic.path for pic in report.room_pictures.all()]  # Assuming related field
        Image_indoor1 = report.image_indoor1.path if report.image_indoor1 else ''
        Image_indoor2 = report.image_indoor2.path if report.image_indoor2 else ''
        Image_indoor3 = report.image_indoor3.path if report.image_indoor3 else ''
        Image_indoor4 = report.image_indoor4.path if report.image_indoor4 else ''
        Image_logo = report.image_logo.path if report.image_logo else ''
        comment = report.comment

        # Call the RPTGen function with all required parameters
        filename = RPTGen(
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
            popup=True
        )
        
        # Assuming 'filename' is the path to the generated PDF
        return {'status': 'success', 'pdf_url': filename}
    except Report.DoesNotExist:
        app_logger.error(f'Report with id {report_id} does not exist.')
        return {'status': 'error', 'message': 'Report does not exist.'}
    except Exception as e:
        app_logger.exception(f'Error generating report: {e}')
        return {'status': 'error', 'message': str(e)}

# @shared_task(bind=True)
# def generate_report_task(self, report_id):
#     try:
#         self.update_state(state='STARTED', meta={'status':'Initializing report generation'})
#         # Fetch the report instance
#         report_instance = Report.objects.select_related('user').get(id=report_id)
#         user = report_instance.user
#         app_logger.debug(f'Report instance saved: {report_instance}')

#         self.update_state(state="PROGRESS", meta={'status':'Processing data from sensors'})
#         time.sleep(2) 

#         self.update_state(state='PROGRESS', meta={'status':'Analysing...'})
#         time.sleep(3)

#         self.update_state(state='PROPGRESS', meta={'status':'Writing report'})
#         time.sleep(3)

#         report_instance.status='Completed'
#         report_instance.save()

#         return 'Report generation completed successfully.'

#     except Report.DoesNotExist:
#         app_logger.error(f"Report with ID {report_id} does not exist.")
#         self.update_state(state='FAILURE', meta={'status': 'Report does not exist.'})
#         raise

#     except Exception as e:
#         app_logger.error(f"Error in report generation task: {e}")
#         self.update_state(state='FAILURE', meta={'status': str(e)})
#         raise e