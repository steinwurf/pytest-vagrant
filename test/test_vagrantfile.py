import os
import pytest_vagrant


def test_vagrantfile(datarecorder, testdirectory):

    vagrantfile = pytest_vagrant.Vagrantfile()
    vagrantfile.write(box='ubuntu/eoan64', box_version=None,
                      name='ubuntu_no_version', cwd=testdirectory.path())

    datarecorder.record_file(
        data_file=os.path.join(testdirectory.path(), 'Vagrantfile'),
        recording_file='test/recordings/ubuntu_no_version.txt')

    vagrantfile.write(box='ubuntu/eoan64', box_version="1.2.3",
                      name='ubuntu_version', cwd=testdirectory.path())

    datarecorder.record_file(
        data_file=os.path.join(testdirectory.path(), 'Vagrantfile'),
        recording_file='test/recordings/ubuntu_version.txt')

    vagrantfile.write(box='hashicorp/bionic64', box_version="1.2.3",
                      name='hashicorp', cwd=testdirectory.path())

    datarecorder.record_file(
        data_file=os.path.join(testdirectory.path(), 'Vagrantfile'),
        recording_file='test/recordings/hashicorp.txt')
