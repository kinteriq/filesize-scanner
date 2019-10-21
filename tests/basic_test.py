from io import StringIO
import os
import pytest
import sys
from unittest import mock

import filesize_scanner
from filesize_scanner import (_get_args, helper, get_all_files,
    search_the_directory, main)
from config import LIBRARY


class Params:
    def __init__(self, search_subfolders=False, exclude=False, limit=-1):
        self.params = {
            'search_subfolders': search_subfolders,
            'exclude': exclude,
            'limit': limit,
        }

    def get(self):
        return self.params
        
        
def test_args_float_limit_number(monkeypatch):
    expecting = (os.getcwd(), {''}, Params(limit=10).get())
    args = ['filesize_scanner.py', '10.5']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_int_limit_number(monkeypatch):
    expecting = (os.getcwd(), {''}, Params(limit=1).get())
    args = ['filesize_scanner.py', '1']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_any_extension(monkeypatch, fake_dir):
    expecting = (fake_dir, {''}, Params.get()())
    args = ['filesize_scanner.py', fake_dir]
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_subfolders(monkeypatch, fake_dir):
    expecting = (fake_dir, {''}, Params(search_subfolders=True).get())
    args = ['filesize_scanner.py', fake_dir, '-r']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_wrong_directory(monkeypatch):
    name = 'test213213fake_dir'
    expecting = f'There is no "{name}" directory.'
    args = ['filesize_scanner.py', name]
    monkeypatch.setattr(sys, 'argv', args)
    with pytest.raises(SystemExit) as e:
        _get_args()
    assert expecting in e.exconly()


def test_args_no_extension(monkeypatch, fake_dir):
    expecting = (fake_dir, {''}, Params.get())
    args = ['filesize_scanner.py', fake_dir, 'e=']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_wrong_library(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=videos']
    expecting = 'Available libraries: ' +\
        ', '.join(list(LIBRARY.keys()))
    monkeypatch.setattr(sys, 'argv', args)
    with pytest.raises(SystemExit) as e:
        _get_args()
    assert expecting in e.exconly()


def test_args_several_libraries(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=video,audio']
    ext = set(LIBRARY['video'])
    ext = ext.union(set(LIBRARY['audio']))
    expecting = (fake_dir, ext, Params.get())
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_library_with_extensions(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=video', 'e=mp3']
    ext = set(LIBRARY['video'])
    ext.add('mp3')
    expecting = (fake_dir, ext, Params.get())
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_exclude_extensions(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'e=-mp3,mp4']
    expecting = (fake_dir, {'mp3', 'mp4'}, Params(exclude=True).get())
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_exclude_libraries(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=-audio,video']
    ext = set(LIBRARY['audio'])
    ext = ext.union(LIBRARY['video'])
    expecting = (fake_dir, ext, Params(exclude=True).get())
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


@pytest.mark.xfail(strict=True, reason='Weird user input')
def test_args_exclude_include(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=-audio,video', 'e=mp3']
    expecting = (fake_dir, {'mp3'}, Params(exclude=True).get())
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_valid_helper():
    expecting = filesize_scanner.__doc__
    with pytest.raises(SystemExit):
        with mock.patch('sys.stdout', new=StringIO()) as mock_out:
            helper()
            assert mock_out.get_value() == expecting


def test_check_not_found(fake_dir):
    expecting = f'No files in "{fake_dir}" with any extension(s).'
    args = ['filesize_scanner.py', fake_dir]
    with pytest.raises(SystemExit) as e:
        get_all_files(fake_dir, {''}, Params(exclude=True).get())
    assert expecting in e.exconly()


def test_check_found_files(fake_files):
    path = os.path.split(fake_files[0])[0]
    expecting = list(
        map(lambda x: (os.path.getsize(x), x), fake_files)
    )
    args = ['filesize_scanner.py', path]
    result = get_all_files(path, {''}, Params.get())
    assert sorted(expecting, reverse=True) == result


def test_search_dir_exclude_extensions(fake_files):
    path = os.path.split(fake_files[0])[0]
    expecting = [(os.path.getsize(fake_files[0]), fake_files[0])]
    result = search_the_directory(path, {'a', 'c'}, exclude=True)
    assert expecting == result


def test_search_dir(fake_files):
    path = os.path.split(fake_files[0])[0]
    expecting = [(os.path.getsize(fake_files[0]), fake_files[0])]
    result = search_the_directory(path, {'txt'})
    assert expecting == result


def test_search_dir_without_subdir(fake_files):
    path = os.path.split(fake_files[0])[0]
    os.mkdir(os.path.join(path, 'sub_dir'))
    expecting = list(map(lambda x: (os.path.getsize(x), x), fake_files))
    result = search_the_directory(path, {''})
    assert expecting == result


def test_limit_is_zero(monkeypatch, fake_files):
    """
    If limit == 0: user should see the quantity of files and
        their overall size without a list of actual filenames.
    """
    path = os.path.split(fake_files[0])[0]
    readable_result = 'FOUND 3 FILES; THE OVERALL SIZE IS 0 Bytes.'
    divider = '=' * len(readable_result) + '\n'
    expecting = divider + readable_result + '\n' + divider
    args = lambda: (path, {''}, Params(exclude=True).get())
    monkeypatch.setattr(filesize_scanner, '_get_args', args)
    with mock.patch('sys.stdout', new=StringIO()) as mock_out:
        with pytest.raises(SystemExit) as e:
            answer = StringIO('y')
            monkeypatch.setattr('sys.stdin', answer)
            main()
            assert '-- Exit.' in e.exconly()
        assert expecting == mock_out.getvalue()
    

@pytest.mark.xfail(reason='WIP')
def test_find_useless_files(monkeypatch, fake_files):
    # TODO: --useless -> see files list
    path = os.path.split(fake_files[0])[0]
    args = ['filesize_scanner.py', path,'--useless']
    monkeypatch.setattr('sys.argv', args)
    with mock.patch('sys.stdout', new=StringIO()) as mock_out:
        main()
        assert not mock_out.getvalue()