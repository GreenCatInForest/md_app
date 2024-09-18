from celery import shared_task
from celery.exceptions import Ignore
import time
from .utils import PCAdataTool

@shared_task(bind=True)
def generate_report(self, form_data):
    try:
        # Define total steps for progress tracking
        total_steps = 5

        # Step 1: Fetch data
        self.update_state(state='PROGRESS', meta={'current': 1, 'total': total_steps, 'status': 'Fetching data...'})
        data = PCAdataTool.fetch_data(form_data)
        
        # Step 2: Process data
        self.update_state(state='PROGRESS', meta={'current': 2, 'total': total_steps, 'status': 'Processing data...'})
        processed_data = PCAdataTool.process_data(data)
        
        # Step 3: Generate visuals (e.g., charts, graphs)
        self.update_state(state='PROGRESS', meta={'current': 3, 'total': total_steps, 'status': 'Generating visuals...'})
        visuals = PCAdataTool.generate_visuals(processed_data)
        
        # Step 4: Compile PDF report
        self.update_state(state='PROGRESS', meta={'current': 4, 'total': total_steps, 'status': 'Compiling PDF report...'})
        pdf_file_path = PCAdataTool.compile_pdf(processed_data, visuals, form_data)
        
        # Step 5: Save and finalize report
        self.update_state(state='PROGRESS', meta={'current': 5, 'total': total_steps, 'status': 'Finalizing report...'})
        PCAdataTool.save_report(pdf_file_path, form_data)
        
        return {
            'current': 100,
            'total': 100,
            'status': 'Task completed!',
            'result': pdf_file_path
        }
    
    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc_message': str(e)})
        raise Ignore() 
        

    
    
    
