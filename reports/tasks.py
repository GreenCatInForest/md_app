from __future__ import absolute_import
import time
from celery import shared_task

@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param

@shared_task
def long_running_task():
    # Simulate a long-running task
    time.sleep(10)  # Sleep for 10 seconds
    return 'Task Completed!'