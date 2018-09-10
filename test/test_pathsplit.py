import os
import pytest_vagrant.utils


def test_path_file_split():

    remote_dirs, remote_file = pytest_vagrant.utils.path_file_split(
        '/tmp/ok/go.txt')

    assert remote_dirs == ['/', 'tmp', 'ok']
    assert remote_file == 'go.txt'

    remote_dirs, remote_file = pytest_vagrant.utils.path_file_split(
        'tmp/ok/go.txt')

    assert remote_dirs == ['tmp', 'ok']
    assert remote_file == 'go.txt'

    remote_dirs, remote_file = pytest_vagrant.utils.path_file_split('go.txt')

    assert remote_dirs == []
    assert remote_file == 'go.txt'


def test_path_split():

    remote_dirs = pytest_vagrant.utils.path_split(
        '/tmp/ok/go')

    assert remote_dirs == ['/', 'tmp', 'ok', 'go']

    remote_dirs = pytest_vagrant.utils.path_split(
        'tmp/ok/')

    assert remote_dirs == ['tmp', 'ok']

    remote_dirs = pytest_vagrant.utils.path_split('~/ok/ok')

    assert remote_dirs == ['~', 'ok', 'ok']
