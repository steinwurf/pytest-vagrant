import os
import pytest_vagrant.utils


def test_pathsplit():

    remote_dirs, remote_file = pytest_vagrant.utils.path_split(
        '/tmp/ok/go.txt')

    assert remote_dirs == ['/', 'tmp', 'ok']
    assert remote_file == 'go.txt'

    remote_dirs, remote_file = pytest_vagrant.utils.path_split('tmp/ok/go.txt')

    assert remote_dirs == ['tmp', 'ok']
    assert remote_file == 'go.txt'

    remote_dirs, remote_file = pytest_vagrant.utils.path_split('go.txt')

    assert remote_dirs == []
    assert remote_file == 'go.txt'
