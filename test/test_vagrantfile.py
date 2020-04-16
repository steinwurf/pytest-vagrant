
import pytest_vagrant


def test_vagrantfile(datarecorder, testdirectory):

    vagrantfile = pytest.VagrantFile()
    vagrantfile.write(box='ubuntu/eoan64', box_version=None,
                      name='ubuntu_no_version', cwd=testdirectory.path())
