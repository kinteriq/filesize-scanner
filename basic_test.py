from io import StringIO
import os
import pytest
import sys
from unittest import mock

import filesize_scanner
from filesize_scanner import (_get_args, helper,
    retrieve_sizes, get_all_files, _LIBRARY)


@pytest.fixture
def fake_dir():
    dirname = 'test dir -r'
    os.mkdir(dirname)
    dirname = os.path.abspath(dirname)
    yield dirname
    os.rmdir(dirname)


@pytest.fixture
def fake_files():
    names = ['file1', 'file2', 'file3']
    for name in names:
        with open(name, 'w'):
            pass
    yield names
    for name in names:
        os.remove(name)


def test_args_float_limit_number(monkeypatch):
    expecting = (os.getcwd(), set(['']), False, 10)
    args = ['filesize_scanner.py', '10.5']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_any_extension(monkeypatch, fake_dir):
    expecting = (fake_dir, {''}, False, 0)
    args = ['filesize_scanner.py', fake_dir]
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_subfolders(monkeypatch, fake_dir):
    expecting = (fake_dir, {''}, True, 0)
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
    expecting = (fake_dir, {''}, False, 0)
    args = ['filesize_scanner.py', fake_dir, 'e=']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_wrong_library(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=videos']
    expecting = 'Availible libraries: ' +\
        ', '.join(list(_LIBRARY.keys()))
    monkeypatch.setattr(sys, 'argv', args)
    with pytest.raises(SystemExit) as e:
        _get_args()
    assert expecting in e.exconly()


def test_args_several_libraries(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=video,audio']
    ext = set(_LIBRARY['video'])
    ext = ext.union(set(_LIBRARY['audio']))
    expecting = (fake_dir, ext, False, 0)
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_library_with_extensions(monkeypatch, fake_dir):
    args = ['filesize_scanner.py', fake_dir, 'l=video', 'e=mp3']
    ext = set(_LIBRARY['video'])
    ext.add('mp3')
    expecting = (fake_dir, ext, False, 0)
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_args_valid_helper():
    expecting = filesize_scanner.__doc__
    with pytest.raises(SystemExit):
        with mock.patch('sys.stdout', new=StringIO()) as mock_out:
            helper()
            assert mock_out.get_value() == expecting


def test_check_not_found(monkeypatch, fake_dir):
    expecting = f'No files in "{fake_dir}" with any extension(s).'
    args = ['filesize_scanner.py', fake_dir]
    with pytest.raises(SystemExit) as e:
        get_all_files(fake_dir, set(['']), False)
    assert expecting in e.exconly()


def test_retrieve_sizes(fake_files):
    expecting = list(map(lambda x: (os.path.getsize(x), x), fake_files))
    assert retrieve_sizes(fake_files) == expecting