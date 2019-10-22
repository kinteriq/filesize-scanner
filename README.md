# filesize-scanner


### Description:

Scans the directory for files with specified
extensions and list their sizes and names.

### Arguments:

Argument                      | Description
------------------------------|------------------
--help                        | see documentation
*directory*                   | __default__ : current directory
e=*extension*                 | __default__ : all extensions
e=-*extension*\*              | exclude extension
e=*extension_1,extension_2*\* | multiple extensions input
l=*library*\*\*               | initial libraries : *audio*, *video*, *documents*
*number*                      | print out only *number* largest files
-r                            | search all subfolders

### Example:

        python3 filesize_scanner.py ~/Desktop/ e=mp4,mp3 3 -r

*The command will print out __three__ largest __"mp4"__, __"mp3"__ files
and their sizes, found in __"~/Desktop/"__ directory and __all its subdirectories__.*

## Requirements:
- MacOS/Linux;
- python3.6 or later;

---

\* _the same for libraries_

\*\* *to create your own libraries or edit existing ones: manipulate __LIBRARY__
variable inside __config.py__*