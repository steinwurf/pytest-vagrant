import pytest

import pytest_vagrant.vagrant
from pytest_vagrant.sshdirectory import SSHDirectory


@pytest.fixture(scope='session')
def vagrant(request):
    """ Creates the py.test fixture to make it usable withing the unit
    tests. See the Vagrant class for more information.
    """

    vagrantfile = request.config.getoption('vagrantfile')

    return pytest_vagrant.vagrant.Vagrant(vagrantfile=vagrantfile)


def pytest_addoption(parser):
    parser.addoption(
        '--vagrantfile', action='store', default=None,
        help='Specify the vagrantfile to use')


@pytest.fixture(scope='session')
def sshdirectory_pytest(vagrant):
    """ Create a pytest directory for all the ssh directories to be
    created in.
    """

    with vagrant.ssh() as ssh:

        # We create our test directory in the home dir
        home_dir = SSHDirectory(ssh=ssh.client, sftp=ssh.sftp, cwd="~")

        if home_dir.isdir('pytest_temp'):
            home_dir.rmdir('pytest_temp')

        pytest_dir = home_dir.mkdir('pytest_temp')

        yield pytest_dir


@pytest.fixture()
def sshdirectory(sshdirectory_pytest, request):
    """ Creates the py.test fixture to make it usable withing the unit tests.
    See the Vagrant class for more information.
    """

    return sshdirectory_pytest.mkdir(request.node.name)
