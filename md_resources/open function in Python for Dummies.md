open() is a built-in Python function. 
It opens a file, and returns it as a file object.  If the file cannot be opened, an OSError is raised. 

open() returns a file object, and is most commonly used with two positional arguments and one keyword argument: 
open(filename, mode, encoding=None)

f = open('workfile', 'w', encoding="utf-8")
file_object = open(file_path, mode)

The first argument is a string containing the filename. 
The second argument is another string containing a few characters 
describing the way in which the file will be used. 

mode can be 'r' when the file will only be read, 
'w' for only writing (an existing file with the same name will be erased), 
and 'a' opens the file for appending; 
any data written to the file is automatically added to the end. 

'r+' opens the file for both reading and writing. 
The mode argument is optional; 'r' will be assumed if it’s omitted.
Appending a 'b' to the mode opens the file in binary mode. 
Data is read and written as bytes objects (b'...'), not as strings ('...').

"r" for read, and "t" for text are the default values, you do not need to specify them.





