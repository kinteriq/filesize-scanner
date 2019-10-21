_KB = 1024

# add extensions to simplify search
LIBRARY = dict(audio={'mp3', 'flac'},
               video={'mkv', 'mp4', 'avi', 'webpm', 'mov'},
               documents={'txt', 'doc', 'pdf'})

# bunch of lines to be printed out at one go
PRINTABLE = 25

# consider files as useless if not accessed in this period of time
FILES_NOT_USED = {
    'days': 0,
    'months': 1,
    'years': 0,
}