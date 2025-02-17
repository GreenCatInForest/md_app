 Django stores files locally, using the MEDIA_ROOT and MEDIA_URL settingsby default. 

 When we use a FileField or ImageField, Django provides a set of APIs we can use to deal with that file.

1. How Django Receives File Uploads

RECEIVIND FILES AND DATA TO STORE

- USER feels the form
- BROWSER sends the file data as a part of a HTTP request POST using multipart/form-data
- Django SERVER receives the request and parse out:
  - non-file fields
  - file fields via request.FILES.get('external_picture')

PROCESSING FILES AND DATA TO STORE

Django internally uses its MultiPartParser to parse the multipart data. 
The parsing process separates the file content from the textual form fields, placing the files into **request.FILES** and the other form data into **request.POST**
- less than 2.5 megabytes - upload to memory (in a UploadedFile object).
  UploadedFile object - is a wrapper around an uploaded file.
- larger - generate tmp.upload file on disk, stores in tmp directory. 

STORING FILES

- Uploaded files Django stores on the local filesystem in the directory pointed to in settings.py MEDIA_ROOT.

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

- MEDIA_ROOT - Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT tells Django where (in the file system) the uploaded files will be stored.
This means any uploaded files will end up in the media folder inside the project directory.

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Absolute filesystem path on my server’s filesystem (/var/www/myproject/media or my_project/media).
MEDIA_URL tells Django what URL prefix to use when referring to these uploaded files.
MEDIA_URL = '/media/'
# the url endpoint from which the files can be served

MEDIA_ROOT = "Where on the server’s hard drive do we physically keep uploaded files?"
MEDIA_URL = "How do we map a browser-accessible URL path to those actual files on disk?"

- The path specified in upload_to (in the model’s FileField) is relative to MEDIA_ROOT. 

EXAMPLE:

# Models
    report_file = models.FileField(upload_to='reports_save/', null=True, blank=True)

# Final path:
    MEDIA_ROOT/reports_save/report_file<NN123>

DATA FLOW:
1) HTTP POST request with multipart-form
2) parsing data and files: files to **request.FILES** and non-files to **request.POST**
3) storind files to the directory specified by MEDIA_ROOT.
4) MEDIA_URL is used to construct the URL that serves these files
5) The final path construction uses parametres **upload_to** from Models ImageField or FileField. **Upload_to** specifies the subdirectory in MEDIA_ROOT where files will be stored.


ABOUT request.FILES 
- request.FILES handles the uploaded files and stores them in the directory specified by MEDIA_ROOT.

ABOUT request.POST
- request.POST is a QueryDict object that holds the non-file data sent in the POST request.


HOW DJANGO MANAGE THE DATA

1) During processing Django loads data into memory. request.POST and request.FILES are available as attributes of the HttpRequest object for the duration of the request.

def my_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

2) Request.POST saved to the database only when we are calling form.save() manually. 
Request.FILES stores to the database via MEDIA_ROOT automatically. 
It happens in views. 
View Processing:
- View accesses request.POST to retrieve form data.
- Validates and processes the data (e.g., saving to the database).

3) After processing the data Django server returns HTTP responce back to client and data in request.POST is discarded unless saved.
