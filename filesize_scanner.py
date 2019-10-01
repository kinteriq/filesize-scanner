#     This script scans the directory for files with specified extensions
#     and list their sizes and names.

#     Copyright (C) 2019  kinteriq

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
DESCRIPTION:

    Scans the directory for files with specified
    extensions and list their sizes and names.

ARGUMENTS:

    --help                        | see documentation
    <DIRECTORY>                   | default : current directory
    e=<EXTENSION>                 | default : all extensions
    e=-<EXTENSION>                | exclude extension(the same for libraries)
    e=<EXTENSION_1,EXTENSION_2...>| multiple extensions input(the same for libraries)
    l=<LIBRARY>                   | initial libraries : "audio", "video", "documents"
    <NUMBER>                      | print out only <NUMBER> largest files
    -r                            | search all subfolders


EXAMPLE:

    python3 filesize_scanner.py ~/Desktop/ e=mp4,mp3 3 -r

--- command will print out 3 largest 'mp4', 'mp3' files and
their sizes, found in '~/Desktop/' directory and
all its subdirectories.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import re
import stat
import sys
import time


_KB = 1024
_SIZE_INDEX, _NAME_INDEX = 0, 1

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


class Check:
    def library_name(name):
        if name not in LIBRARY:
            raise SystemExit('Availible libraries: ' +\
                ', '.join(list(LIBRARY.keys())))
    
    def directory(d):
        if d.startswith('~'):
            d = os.path.expanduser('~') + d
        if not os.path.isdir(d):
            raise SystemExit(f'There is no "{d}" directory.')
        return d
    
    def exclusion(e):
        if e[2:].startswith('-'):
            e = e[3:].split(',')
            return (e, True)
        e = e[2:].split(',')
        return (e, False)

    def found(files, directory, ext):
        if not files:
            if ext == set(['']):
                ext = 'any'
            raise SystemExit(
                f'No files in "{directory}" with {ext} extension(s).'
            )
    
    def useless_file(path):     # TODO: all platforms
        """
        Check when the file was last opened;
            returns True if more time had passed
            than specified in FILES_NOT_USED.
        """
        today = datetime.today()
        delta = today - relativedelta(**FILES_NOT_USED)
        last_modified = os.stat(path)[stat.ST_ATIME]
        if last_modified < time.mktime(delta.timetuple()):
            return True
        return False


def main():
    dirname, extensions, params = _get_args()
    files_info = get_all_files(dirname, extensions, params)
    pretty_all_print(files_info, params['limit'])


def _get_args() -> tuple:
    dirname = os.getcwd()
    extensions = set([''])
    params = {
        'search_subfolders': False,
        'exclude': False,
        'limit': -1,
        'useless': False,
    }

    args = sys.argv

    if '--help' in args:
        helper()
    if '--useless' in args:
        params['useless'] = True
        args.remove('--useless')

    for arg in args[1:]:
        if '-r' == arg:
            params['search_subfolders'] = True
        elif re.match(r'^\d+?\.?\d*?$', arg):
            params['limit'] = int(float(arg))
        elif arg.startswith('e='):
            ext, params['exclude'] = Check.exclusion(arg)
            extensions = extensions.union(ext)
        elif arg.startswith('l='):
            libraries, params['exclude'] = Check.exclusion(arg)
            for l in libraries:
                Check.library_name(l)
                extensions = extensions.union(
                    LIBRARY[l])
        else:
            dirname = Check.directory(arg)
        if len(extensions) > 1 and '' in extensions:
            extensions.remove('')
    return dirname, extensions, params


def helper():
    try:
        import filesize_scanner
        print(filesize_scanner.__doc__)
    except ImportError as exc:
        raise ImportError(
            'The title of the file should be "filesize_scanner.py".'
        ) from exc
    else:
        raise SystemExit()


def find_useless_files():
    pass


def get_all_files(dirname, extensions, params):
    '''
    :return: list of tuples
             [ (filesize, filepath), ... ]
    '''
    search_subfolders = params['search_subfolders']
    files_data = []
    if search_subfolders:
        for thisDir, *_ in os.walk(dirname):
            files_data.extend(search_the_directory(
                thisDir, extensions, params['exclude']))
    else:
        files_data.extend(search_the_directory(
            dirname, extensions, params['exclude']))
    Check.found(files_data, dirname, extensions)
    files_data.sort(reverse=True)
    return files_data


def search_the_directory(dirname, extensions, exclude=False):
    '''
    :return: list of tuples
             [ (filesize, filepath), ... ]
    '''
    if exclude:
        excluded = extensions
    else:
        extensions = extensions
    sizes_with_paths =[]
    for file in os.listdir(dirname):
        ext = file.split('.')[-1]
        filepath = os.path.join(dirname, file)
        if (not exclude and (ext in extensions or extensions == {''})
            and os.path.isfile(filepath)):
            sizes_with_paths.append(
                (os.path.getsize(filepath), filepath))
        elif exclude and ext not in excluded and os.path.isfile(filepath):
            sizes_with_paths.append(
                (os.path.getsize(filepath), filepath))
    return sizes_with_paths


def pretty_all_print(files_data, limit: int) -> None:
    '''
    :param: files_data -- list of tuples
                          [ (filesize, filepath), ... ]
    '''
    size = convert_bytes(
        sum([data[_SIZE_INDEX] for data in files_data])
    )
    files_num = len(files_data)
    top_msg = f'FOUND {files_num} FILES; THE OVERALL SIZE IS {size}.'
    divider = '=' * len(top_msg)
    print(divider + '\n' + top_msg + '\n' + divider)

    if limit > -1:
        files_data = files_data[:limit]
    beg, end = 0, PRINTABLE
    while beg <= len(files_data):
        for file_i in files_data[beg:end]:
            pretty_single_print(file_i)
        if limit >= files_num or limit == -1 and files_num <= end:
            break
        if limit < files_num and limit != -1 or input('\nMore? (y) ') != 'y':
            raise SystemExit('-- Exit.')
        print()
        beg += PRINTABLE
        end += PRINTABLE
    print('-- Reached the end.')


def pretty_single_print(files_data: tuple) -> None:
    filesize = files_data[_SIZE_INDEX]
    abspath_to_file_name = files_data[_NAME_INDEX]
    print(convert_bytes(filesize) + '\t:\t' + abspath_to_file_name)


def convert_bytes(b: int) -> str:
    sizes = {_KB: ' Kbytes',
             _KB ** 2: ' Mbytes',
             _KB ** 3: ' Gbytes',
             _KB ** 4: ' Tbytes', }
    for key in sorted(sizes, reverse=True):
        if b >= key:
            return str(round(b / key, 2)) + sizes[key]
    return str(b) + ' Bytes'


if __name__ == '__main__':
    main()
