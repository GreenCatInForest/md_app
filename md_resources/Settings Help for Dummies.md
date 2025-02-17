Settings.py deconstruction

1. BASE_DIR = Path(__file__).resolve().parent.parent

This line calculates the root directory of my Django project (where manage.py is located).

In a Django project, BASE_DIR is often used to create paths relative to the root directory of the project. It prevents the dependency on absolute file paths. 


  STATICFILES_DIRS = [BASE_DIR / "static"]
  TEMPLATES_DIR = BASE_DIR / "templates"

    1. DEFINITION - BASE_DIR represents the root directory of the project. Let us reffer files and define file paths relative to the project's root. It points to the top hierarchy of any Django project. 

    - Absolute path - path to the file from the host machine filesystem. 
    MAC - /home/user/documents/file.txt - / means root directory
    Win - C:\Users\User\Documents\file.txt - C: means a drive letter

    - Path comes from the pathlib module in Python, which provides an object-oriented interface to work with filesystem paths. It's more robust than os.path. 

    EXAMPLE OF PATHLIB
      # Create a Path object
      path = Path("some/directory/file.txt")
      print(path.name)  
      # Output: file.txt
      print(path.parent)  
      # Output: some/directory

  - __file__ is a special variable in Python that contains the path to the current script file being executed. In a settings.py file, __file__ refers to settings.py

  - resolve() is a method of the Path object.
    It returns the absolute path of the file or directory. Resolves path components like .(current directory) and ..(parent directory).

    EXAMPLE OF RESOLVE 
    
    from pathlib import Path
    path = Path("some/../directory/file.txt")
    print(path.resolve())  
    # Resolves to an absolute path, e.g., /full/path/to/directory/file.txt

  - parent is an attribute of a Path object that refers to the directory containing the file or folder.

    EXAMPLE OF PARENT and PARENT.PARENT

    from pathlib import Path
    path = Path("/home/user/project/settings.py")
    print(path.parent)  
    # Output: /home/user/project
    print(path.parent.parent)  
    # Output: /home/user

CONCLUSION:
BASE_DIR = Path(__file__).resolve().parent.parent

- Path(__file__):
# Creates a Path object for the file (e.g., settings.py).

- resolve():
# Converts the relative path of __file__ to its absolute path.

- .parent:
# Moves one directory up (e.g., from settings.py to the directory containing it).

.parent.parent:
# Moves up one more directory, typically to the root of the Django project directory.


    - BASE_DIR in DOCKER 
      - BASE_DIR points to the root directory of project but inside the container.
      - Ensure the correct directories are mounted into the container so BASE_DIR matches the structure of the host machine.
      - To work with files on host machine (source code, static files), you map directories on the host to directories inside the container using volumes in docker-compose.yml

    volumes:
        - ./myproject:/app  # Mount the host's myproject directory to /app in the container
        working_dir: /app

        # Host Path: ./myproject (project folder on the host machine).
        # Container Path: /app (the corresponding folder inside the container).

        BASE_DIR in my Django settings will resolve to /app inside the container.
        Changes to files in ./myproject on the host are reflected in /app inside the container.

[Django Documentation - Settings][https://docs.djangoproject.com/en/5.1/ref/settings/]
