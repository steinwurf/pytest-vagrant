import pytest
import pytest_vagrant


@pytest.fixture(scope='session')
def vagrant(request):
    """ Creates the py.test fixture to make it usable withing the unit
    tests. See the Vagrant class for more information.
    """

    return pytest_vagrant.make_vagrant()
