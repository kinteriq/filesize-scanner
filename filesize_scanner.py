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
    e=<EXTENSION_1,EXTENSION_2...>| multiple extensions input
    l=<LIBRARY>                   | availible libraries : "audio", "video", "documents"
    <NUMBER>                      | print out only <NUMBER> largest files
    -r                            | search all subfolders


EXAMPLE:

    python3 filesize_scanner.py ~/Desktop/ e=mp4,mp3 3 -r

--- command will print out 3 largest 'mp4', 'mp3' files and
their sizes, found in '~/Desktop/' directory and
all its subdirectories.
"""

# TODO: fix 'search unusual names' bug


import os
import glob
import sys


_KB: int = 1024
_LIBRARY = dict(audio=('*.mp3', '*.flac'),
                video=('*.mkv', '*.mp4', '*.avi', '*.webpm', '*.mov'),
                documents=('*.txt', '*.doc', '*.pdf'))
_SIZE_INDEX, _NAME_INDEX = 0, 1


def _helper():
    try:
        import filesize_scanner
        print(filesize_scanner.__doc__)
    except ImportError as exc:
        raise ImportError(
            'The title of the file should be "filesize_scanner.py".'
        ) from exc


def _get_args() -> tuple:
    dirname = os.getcwd()
    extensions = ('*',)
    search_subfolders = False
    limit = 0

    args = sys.argv
    if '--help' in args:
        _helper(), sys.exit()

    for arg in args[1:]:
        if arg == '-r':
            search_subfolders = True
        elif arg.isnumeric():
            limit = int(arg)
        elif arg.startswith('e='):
            extensions = set('*.' + argument for argument in arg[2:].split(',')
                         if argument)
            if not extensions:
                print('There should be at least one valid extension.')
                sys.exit()
        elif arg.startswith('l='):
            try:
                extensions = _LIBRARY[arg[2:]]
            except KeyError:
                print('Check the spelling: {}'.format(arg[2:]))
                sys.exit()
        else:
            dirname = arg
            if not os.path.isdir(dirname):
                print('There is no "{}" directory.'.format(dirname))
                sys.exit()

    return dirname, extensions, search_subfolders, limit


def get_all_files(dirname: str, extensions,
                  search_subfolders: bool) -> list:
    '''
    :return: list of tuples
             [ (<filesize>, <abspath_to_file_name>), ... ]
    '''
    files_info = []
    if search_subfolders:
        for thisDir, *_ in os.walk(dirname):
            if not os.path.isdir(thisDir):
                continue
            files_info.extend(_search_the_directory(thisDir, extensions))
    else:
        files_info.extend(_search_the_directory(dirname, extensions))

    if not files_info:
        no_files_msg = 'No such files in "{}" directory \
with {} extension(s)'.format(dirname, extensions)
        print(no_files_msg)
        sys.exit()

    files_info.sort(reverse=True)
    return files_info


def _search_the_directory(dirname: str, extensions) -> list:
    '''
    :return: list of tuples
             [ (<filesize>, <abspath_to_file_name>), ... ]
    '''
    found_files = []
    for ext in extensions:
        found_files.extend(glob.glob(dirname + os.sep + ext))
    sizes = _retrieve_sizes(found_files)
    files_info = zip(sizes, found_files)
    return files_info


def _retrieve_sizes(files: list) -> list:
    sizes = []
    for filepath in files:
        if not os.path.isfile(filepath):
            continue
        filesize = os.path.getsize(filepath)
        sizes.append(filesize)
    return sizes


def pretty_all_print(files_info: list, limit: int) -> None:
    '''
    :param: files_info -- list of tuples
            [ (<filesize>, <abspath_to_file_name>), ... ]
    '''
    top_msg = 'FOUND {number} FILES; THE OVERALL SIZE IS {size}.'.format(
        number=len(files_info),
        size=convert_bytes(
            sum(
                [data[_SIZE_INDEX] for data in files_info]
                )
            )
        )
    divider = '=' * len(top_msg)
    print(divider)
    print('\n', top_msg, '\n')
    print(divider)

    if limit:
        files_info = files_info[:limit]
    for file_i in files_info:
        pretty_single_print(file_i)


def pretty_single_print(file_info: tuple) -> None:
    filesize = file_info[_SIZE_INDEX]
    abspath_to_file_name = file_info[_NAME_INDEX]
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
    dirname, extensions, search_subs, limit = _get_args()
    files_info = get_all_files(dirname, extensions, search_subs)
    pretty_all_print(files_info, limit)
