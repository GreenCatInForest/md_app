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
from .utils import PCAdataTool
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

@shared_task
def long_running_task():
    # Simulate a long-running task
    time.sleep(10)  # Sleep for 10 seconds
    return 'Task Completed!'

@shared_task
def add(x, y):
    """A simple task that adds two numbers."""
    time.sleep(5)  # Simulate a long-running task
    return x + y

@shared_task
def multiply(x, y):
    """A simple task that multiplies two numbers."""
    time.sleep(5)
    return x * y

@shared_task(bind=True)
def generate_report_task(self, report_id):
    try:
        self.update_state(state='STARTED', meta={'status':'Initializing report generation'})
        # Fetch the report instance
        report_instance = Report.objects.select_related('user').get(id=report_id)
        user = report_instance.user
        app_logger.debug(f'Report instance saved: {report_instance}')

        self.update_state(state="PROGRESS", meta={'status':'Processing data from sensors'})
        time.sleep(2) 

        self.update_state(state='PROGRESS', meta={'status':'Analysing...'})
        time.sleep(3)

        self.update_state(state='PROPGRESS', meta={'status':'Writing report'})
        time.sleep(3)

        report_instance.status='Completed'
        report_instance.save()

        return 'Report generation completed successfully.'

    except Report.DoesNotExist:
        app_logger.error(f"Report with ID {report_id} does not exist.")
        self.update_state(state='FAILURE', meta={'status': 'Report does not exist.'})
        raise

    except Exception as e:
        app_logger.error(f"Error in report generation task: {e}")
        self.update_state(state='FAILURE', meta={'status': str(e)})
        raise e