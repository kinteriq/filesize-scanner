import os
import pytest
import shutil


@pytest.fixture
def fake_dir():
    dirname = 'test dir -r'
    try:
        os.mkdir(dirname)
    except FileExistsError:
        shutil.rmtree(dirname)
    dirname = os.path.abspath(dirname)
    yield dirname
    try:
        shutil.rmtree(dirname)
    except FileNotFoundError:
        pass


@pytest.fixture
def fake_files(fake_dir):
    names = list(map(lambda x: os.path.join(fake_dir, x),
        ['file1.txt', 'file2.c', 'file3.a']))
    for name in names:
        with open(name, 'w'):
            pass
    yield names
    for name in names:
        os.remove(name)