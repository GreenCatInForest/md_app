import tempfile
import os

def save_uploaded_file(uploaded_file):
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    return ''
