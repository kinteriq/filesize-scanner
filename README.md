# filesize-scanner


#### Description:

Scans the directory for files with specified
extensions and list their sizes and names.

#### Arguments:

Argument                      | Description
------------------------------|------------------
--help                        | see documentation
*DIRECTORY*                   | __default__ : current directory
e=*EXTENSION*                 | __default__ : all extensions
e=*EXTENSION_1,EXTENSION_2*   | multiple extensions input
l=*LIBRARY*                   | available libraries : *audio*, *video*, *documents*
*NUMBER*                      | print out only *NUMBER* largest files
-r                            | search all subfolders

#### Example:

        python3 filesize_scanner.py ~/Desktop/ e=mp4,mp3 3 -r

_The command will print out **three** largest **"mp4"**, **"mp3"** files
and their sizes, found in **"~/Desktop/"** directory and **all its subdirectories**_

---