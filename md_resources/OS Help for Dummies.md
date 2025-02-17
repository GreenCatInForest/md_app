HOW TO DEFINE PATHS

OS (Operating System) - standard Python library module/utility module. 
It provides an interface between Python programs and the underlying operating system.

It allows to work with:
- Files and directories:
os.path.join: Combines path components.
os.path.exists: Checks if a file or directory exists.
os.path.abspath: Returns the absolute path of a file.
os.remove: Deletes a file.
os.makedirs: Creates directories, including intermediate ones.

- Environment variables
- Process management (run system commands, get process IDs, or change the current working directory.)    rrr
# Run a system command
os.system("echo Hello, World!")
# Get the current process ID
print("Process ID:", os.getpid())
- Cross-Platform Compatibility

- Operating system-level functionality 

os.path - a submodule of os for working with paths. 

[Documentation os][https://docs.python.org/3/library/os.html]