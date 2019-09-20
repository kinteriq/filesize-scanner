import os
import pytest
import sys

import filesize_scanner
from filesize_scanner import _get_args, helper, retrieve_sizes, get_all_files


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


def test_float_limit_number(monkeypatch):
    expecting = (os.getcwd(), set(['']), False, 10)
    monkeypatch.setattr(sys, 'argv', 'filesize_scanner.py 10.5'.split())
    assert _get_args() == expecting


def test_get_args(monkeypatch, fake_dir):
    expecting = (fake_dir, {'mp3', 'mp4'}, True, 10)
    args = ['filesize_scanner.py', fake_dir, 'e=mp3,mp4', '10.5', '-r']
    monkeypatch.setattr(sys, 'argv', args)
    assert _get_args() == expecting


def test_valid_helper():
    with pytest.raises(SystemExit) as e:
        helper()


def test_check_not_found(monkeypatch, fake_dir):
    expecting = f'No files in "{fake_dir}" with any extension(s).'
    args = ['filesize_scanner.py', fake_dir]
    with pytest.raises(SystemExit) as e:
        get_all_files(fake_dir, set(['']), False)
    assert expecting in e.exconly()


def test_retrieve_sizes(fake_files):
    expecting = list(map(lambda x: (os.path.getsize(x), x), fake_files))
    assert retrieve_sizes(fake_files) == expecting