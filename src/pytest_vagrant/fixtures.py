import pytest
import pytest_vagrant


@pytest.fixture(scope='session')
def vagrant(request):
    """ Creates the py.test fixture to make it usable withing the unit
    tests. See the Vagrant class for more information.
    """

    shell = pytest_vagrant.Shell()
    machines_dir = pytest_vagrant.default_machines_dir()

    machine_factory = pytest_vagrant.MachineFactory(
        shell=shell, machines_dir=machines_dir, ssh_factory=pytest_vagrant.SSH)

    return pytest_vagrant.Vagrant(machine_factory=machine_factory, shell=shell)
