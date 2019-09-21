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
import os
import re
import sys


_KB = 1024
_LIBRARY = dict(audio={'mp3', 'flac'},
                video={'mkv', 'mp4', 'avi', 'webpm', 'mov'},
                documents={'txt', 'doc', 'pdf'})
_SIZE_INDEX, _NAME_INDEX = 0, 1


class Check:
    def library_name(name):
        if name not in _LIBRARY:
            raise SystemExit('Availible libraries: ' +\
                ', '.join(list(_LIBRARY.keys())))
    
    def directory(d):
        if d.startswith('~'):
            d = os.path.expanduser('~') + d
        if not os.path.isdir(d):
            raise SystemExit(f'There is no "{d}" directory.')
        return d
    
    def found(files, directory, ext):
        if not files:
            if ext == set(['']):
                ext = 'any'
            raise SystemExit(
                f'No files in "{directory}" with {ext} extension(s).'
            )


def main():
    *params, limit = _get_args()
    files_info = get_all_files(*params)
    pretty_all_print(files_info, limit)


def _get_args() -> tuple:
    dirname = os.getcwd()
    extensions = set([''])
    search_subfolders = False
    limit = 0

    args = sys.argv

    if '--help' in args:
        helper()

    for arg in args[1:]:
        if '-r' == arg:
            search_subfolders = True
        elif re.match(r'^\d+?\.?\d+?$', arg):
            limit = int(float(arg))
        elif arg.startswith('e='):
            extensions = extensions.union(set(arg[2:].split(',')))
        elif arg.startswith('l='):
            libraries = arg[2:].split(',')
            for l in libraries:
                Check.library_name(l)
                extensions = extensions.union(_LIBRARY[l])
        else:
            dirname = Check.directory(arg)
        if len(extensions) > 1 and '' in extensions:
            extensions.remove('')
    return dirname, extensions, search_subfolders, limit


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


def get_all_files(dirname, extensions, search_subfolders: bool) -> list:
    '''
    :return: list of tuples
             [ (filesize, filepath), ... ]
    '''
    files_data = []
    if search_subfolders:
        for thisDir, *_ in os.walk(dirname):
            if not os.path.isdir(thisDir):
                continue
            files_data.extend(search_the_directory(thisDir, extensions))
    else:
        files_data.extend(search_the_directory(dirname, extensions)) 
    Check.found(files_data, dirname, extensions)
    files_data.sort(reverse=True)
    return files_data


def search_the_directory(dirname, extensions) -> list:
    '''
    :return: list of tuples
             [ (filesize, filepath), ... ]
    '''
    found_files = []
    for file in os.listdir(dirname):
        for ext in extensions:
            if file.endswith(ext):
                found_files.append(os.path.join(dirname, file))
    sizes_with_paths = retrieve_sizes(found_files)
    return sizes_with_paths


def retrieve_sizes(files: list) -> list:
    sizes_with_paths = []
    for filepath in files:
        if not os.path.isfile(filepath):
            continue
        filesize = os.path.getsize(filepath)
        sizes_with_paths.append((filesize, filepath))
    return sizes_with_paths


def pretty_all_print(files_data, limit: int) -> None:
    '''
    :param: files_data -- list of tuples
                          [ (filesize, filepath), ... ]
    '''
    converted_bytes = convert_bytes(
        sum([data[_SIZE_INDEX] for data in files_data])
    )
    top_msg = f'FOUND {len(files_data)} FILES; ' +\
        'THE OVERALL SIZE IS ' + converted_bytes + '.'
    divider = '=' * len(top_msg)
    print(divider + '\n' + top_msg + '\n' + divider)

    if limit:
        files_data = files_data[:limit]
    for file_i in files_data:
        pretty_single_print(file_i)


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
