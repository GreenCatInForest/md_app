import os
import shutil
import tempfile
import stripe
from celery import shared_task, current_task
from django.conf import settings
import logging
from core.models import Payment, Report
from .utils import PCAdataTool

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_report_task(self, task_data):
    """
    Celery task to handle report generation with room data and file management.
    """
    try:
        # Step 1: Retrieve Report instance by ID
        report = Report.objects.get(id=task_data['report_id'])

        # Step 2: Create a temporary directory for file management
        temp_dir = tempfile.mkdtemp()
        temp_files = {}

        # Step 3: Save uploaded files to the temporary directory
        for key, uploaded_file in task_data['files'].items():
            if uploaded_file:
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                temp_files[key] = temp_file_path

        # Handle room files (e.g., CSVs)
        room_files = task_data.get('room_files', [])
        for room_file in room_files:
            if room_file and os.path.exists(room_file):
                shutil.copy(room_file, temp_dir)

        # Step 4: Prepare data for RPTGen
        rptgen_data = {
            **task_data['form_data'],
            'monitor_time': task_data['monitor_time'],
            'datafiles': temp_files,
        }

        # Step 5: Update task progress
        stages = ["Starting report generation...", "Processing data...", "Generating PDF..."]
        for i, stage in enumerate(stages):
            current_task.update_state(state='PROGRESS', meta={'current': i+1, 'total': len(stages), 'status': stage})
            # Simulate processing time (remove in production)
            import time
            time.sleep(2)

        # Step 6: Generate PDF report
        pdf_file_path = PCAdataTool.RPTGen(**rptgen_data)

        # Step 7: Check if PDF was generated successfully
        if not pdf_file_path or not os.path.exists(pdf_file_path):
            raise Exception("PDF file was not generated or found.")

        # Step 8: Update the report instance with the PDF path
        report.report_file = os.path.relpath(pdf_file_path, settings.MEDIA_ROOT)
        report.save()

        # Step 9: Complete the task
        return {'status': 'completed', 'report_id': report.id}

    except Exception as e:
        logger.error(f"Error in generate_report_task: {str(e)}")
        self.update_state(state='FAILURE', meta={'exc_message': str(e)})
        raise e

    finally:
        # Step 10: Clean up the temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Temporary directory {temp_dir} deleted")

@shared_task(bind=True)
def process_payment_task(self, payment_id):
    """
    Celery task to handle payment processing.
    """
    try:
        # Retrieve the Payment instance
        payment = Payment.objects.get(id=payment_id)

        # Simulate payment processing (replace with actual Stripe integration)
        # Here, we assume payment is already processed and update status
        payment.payment_status = 'paid'
        payment.save()

        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 1, 'total': 1, 'status': 'Payment processed'})

        return {'status': 'completed', 'payment_id': payment.id}

    except Exception as e:
        logger.error(f"Error in process_payment_task: {str(e)}")
        self.update_state(state='FAILURE', meta={'exc_message': str(e)})
        raise e