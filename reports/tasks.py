from celery import shared_task, current_task

from django.conf import settings
import time  
import os
import logging

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from core.models import Payment, Report
from .utils import PCAdataTool

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_report_task(self, form_data, report_id):
    """
    Celery task to handle report generation with progress updates.
    """
    try:
        # Retrieve the report instance
        report = Report.objects.get(id=report_id)

        # Convert monitor_time back to timedelta
        monitor_time_seconds = form_data.get('monitor_time', 0)
        monitor_time = timedelta(seconds=monitor_time_seconds)
        
        # Stage 1: Checking the data
        current_task.update_state(state='PROGRESS', meta={'current': 1, 'total': 5, 'status': 'Checking the data...'})
        time.sleep(2)  # Simulate time-consuming task

        # Stage 2: Calculating metrics
        current_task.update_state(state='PROGRESS', meta={'current': 2, 'total': 5, 'status': 'Calculating metrics...'})
        time.sleep(2)

        # Stage 3: Generating charts
        current_task.update_state(state='PROGRESS', meta={'current': 3, 'total': 5, 'status': 'Generating charts...'})
        time.sleep(2)

        # Stage 4: Compiling report
        current_task.update_state(state='PROGRESS', meta={'current': 4, 'total': 5, 'status': 'Compiling report...'})
        time.sleep(2)

        # Stage 5: Finalizing and saving PDF
        current_task.update_state(state='PROGRESS', meta={'current': 5, 'total': 5, 'status': 'Finalizing report...'})
        time.sleep(2)

        # Generate PDF
        pdf_file_path = generate_pdf(form_data, report, monitor_time)
        
        if not pdf_file_path or not os.path.exists(pdf_file_path):
            raise Exception("PDF file was not generated or found.")

        # Update the report instance with the PDF file
        report.report_file = os.path.relpath(pdf_file_path, settings.MEDIA_ROOT)
        report.save()

        logger.debug(f"Generated PDF file path: {pdf_file_path} and updated Report {report.id}")

        # Optionally, create an Invoice here or via signals
        # For example:
        # payment = Payment.objects.filter(report=report, payment_status='paid').first()
        # if payment and not payment.invoices.exists():
        #     create_invoice_for_payment(payment)

        # Return success state with the report's ID
        return {'current': 5, 'total': 5, 'status': 'Report generation completed!', 'result': report.id}
    
    except Exception as e:
        # Handle exceptions and mark the task as failed
        logger.error(f"Error in generate_report_task: {e}")
        current_task.update_state(state='FAILURE', meta={'exc_type': e.__class__.__name__, 'exc_message': str(e)})
        raise e

def generate_pdf(form_data, report, monitor_time):
    """
    Function to generate a PDF report.
    Implement your actual PDF generation logic here.
    """
    try:
        form_data = {key: value for key, value in form_data.items() if key != 'monitor_time'}
        pdf_file_path = PCAdataTool.RPTGen(monitor_time=monitor_time, **form_data)
        if not pdf_file_path or not os.path.exists(pdf_file_path):
            raise Exception("PDF file was not generated or found.")

        logger.debug(f"Generated PDF file path: {pdf_file_path}")
        
        # No need to assign or save the report instance here
        # The task will handle updating the report instance

        return pdf_file_path
    except Exception as e:
        logger.error(f"Error generating report PDF: {e}")
        raise e  # Raise the exception to let Celery handle it