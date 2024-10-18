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