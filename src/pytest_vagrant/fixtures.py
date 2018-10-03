import pytest

import pytest_vagrant.vagrant
from pytest_vagrant.sshdirectory import SSHDirectory


@pytest.fixture(scope='session')
def vagrant(request):
    """ Creates the py.test fixture to make it usable withing the unit
    tests. See the Vagrant class for more information.
    """

    vagrantfile = request.config.getoption('vagrantfile')

    vagrant = pytest_vagrant.vagrant.Vagrant(vagrantfile=vagrantfile)

    if request.config.getoption('vagrantreset'):
        snapshots = vagrant.snapshot_list()

        if 'vagrantreset' in snapshots:
            vagrant.snapshot_restore(snapshot='vagrantreset')
        else:
            vagrant.reset()
            vagrant.snapshot_save(snapshot='vagrantreset')

    return vagrant


def pytest_addoption(parser):
    parser.addoption(
        '--vagrantfile', action='store', default=None,
        help='Specify the vagrantfile to use')

    parser.addoption(
        '--vagrantreset', action='store_true', default=False,
        help='We want to reset the machine with every use')


@pytest.fixture(scope='session')
def sshdirectory_pytest(vagrant):
    """ Create a pytest directory for all the ssh directories to be
    created in.
    """

    with vagrant.ssh() as ssh:

        # Get the home dir
        _, stdout, _ = ssh.client.exec_command('cd ~;pwd')
        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError("Could not determine home dir")

        cwd = stdout.read().strip()

        # We create our test directory in the home dir
        home_dir = SSHDirectory(ssh=ssh.client, sftp=ssh.sftp, cwd=cwd)

        if home_dir.contains_dir('pytest_temp'):
            home_dir.rmdir('pytest_temp')

        pytest_dir = home_dir.mkdir('pytest_temp')

        yield pytest_dir


@pytest.fixture()
def sshdirectory(sshdirectory_pytest, request):
    """ Creates the py.test fixture to make it usable withing the unit tests.
    See the Vagrant class for more information.
    """

    assert sshdirectory_pytest.getcwd() == '/home/vagrant/pytest_temp'

    return sshdirectory_pytest.mkdir(request.node.name)
