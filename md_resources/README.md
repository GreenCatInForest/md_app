APP STATUSES: 

1. REPORT statuses:
    1) status - in Report core.models
        1. ('pending', 'Pending'),
        2. ('generated', 'Generated'),
        3. ('paid', 'Paid'),
        4. ('unpaid', 'Unpaid'),

2. CELERY task statuses:
    1) PENDING, STARTED, RETRY, SUCCESS, FAILURE. 
        They are defined in the celery.states module in [Celery Repository][https://github.com/celery/celery/blob/main/celery/states.py]

3. PAYMENT statuses:
    1) status - in Payment core.models
        1. ('succeeded', 'Succeeded'),
        2. ('failed', 'Failed'),
        3. ('pending', 'Pending'),
        4. ('cancelled', 'Cancelled'),
        5. ('refunded', 'Refunded'), 

PAYMENT IDS:

Using UUID in Generating Payment instead of ID. 

FILE STORAGE PATHS:

1. PCADataTool.py:
    -  output_dir = '/code/imgs/' 
    # Referres to root/imgs
    Used to store graphs for the reports:
    plt.savefig(os.path.join(output_dir, 'Fig1.0.png'))

    - output_report_dir = '/code/reports_save/'
    # Referres to root/reports_save
    Used  to store the reports pdf:
    output_file_name = os.path.join(output_report_dir, "PCA_BMI_Report")

2. reports/utils/resize_and_save_image.py
    - accepts image_path from report generator
    - resizes image to max_size=1500, quality=70, JPG or PNG
    - return new_file_path:
    new_file_path = os.path.splitext(image_path)[0] + f'.{save_format.lower()}'

    Result into paths:
    - company logo: /code/media/img/companies_img/company1/image.png
    - external picture: /code/media/img/properties_img/21 Spencer Hill, SW19 4NY/image.png


3. core/models.py

    Report Model:
    company_logo = models.ImageField(upload_to=company_logo_upload_path)
    external_picture = models.ImageField(upload_to=report_property_photo_upload_path)
    report_file = models.FileField(upload_to='reports_save/')

    Room Model:
    room_picture = models.ImageField(upload_to=room_photo_upload_path)

4. IMAGES PATHS:

Images passed to Celery as <str>, as a paths already. 
Doesn't need to be converted to File objects or to extract image.path

- external picture: /code/media/img/properties_img/16 Spencer Hill, SW19 4NY/icons8-goose-48.png
- company logo: /code/media/img/companies_img/qwdq/icons8-goose-48.png 
- room picture: /code/media/img/rooms_img/Report 356 - lleo@example.com/icons8-goose-32.jpeg

- reports: previous path /code/reports_save, new path /code/media/reports_save



    