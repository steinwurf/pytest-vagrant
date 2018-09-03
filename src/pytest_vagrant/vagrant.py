import pytest
import subprocess
import re
import os
import py

from ssh import SSH
from status import Status
from utils import walk_up


@pytest.fixture(scope='session')
def vagrant(request):
    """ Creates the py.test fixture to make it usable withing the unit tests.
    See the Vagrant class for more information.
    """

    vagrantfile = request.config.getoption('vagrantfile')

    return Vagrant(vagrantfile=vagrantfile)


def pytest_addoption(parser):
    parser.addoption(
        '--vagrantfile', action='store', default=None,
        help='Specify the vagrantfile to use')


class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant.

    Example:

        def test_this_function(vagrant):
            with vagrant.ssh() as ssh:
                ssh.put('build/executable', 'test/executable')
                stdout, stderr = ssh.run('./test/executable')
                assert 'hello world' in stdout
    """

    def __init__(self, vagrantfile=None):

        if vagrantfile is None:
            self.cwd = os.getcwd()
        elif os.path.isfile(vagrantfile):
            self.cwd = os.path.basename(vagrantfile)
        elif os.path.isdir(vagrantfile):
            self.cwd = vagrantfile
        else:
            raise RuntimeError(
                "Invalid vagrantfile path {}.".format(vagrantfile))

        # The command 'vagrant validate' was not introduced until vagrant
        # version 1.9.4. https://www.hashicorp.com/blog/vagrant-1-9-4
        #
        # We should check for the version.
        version = subprocess.check_output(
            'vagrant --version', shell=True, cwd=self.cwd)

        if version < "1.9.4":
            raise RuntimeError("Vagrant version above or equal to 1.9.4 "
                               "required. You have {}".format(version))

        try:
            subprocess.check_output(
                'vagrant validate', shell=True, cwd=self.cwd)
        except subprocess.CalledProcessError as e:
            print("Unable to validate vagrant file, are you sure it exists? "
                  "Running vagrant validate in {}".format(self.cwd))
            raise e

        if self.status.not_created or self.status.poweroff:
            print "run up"
            self.up()
        elif self.status.saved:
            print "run resume"
            self.resume()

        if not self.status.running:
            raise RuntimeError(
                "Dispite our efforts, the vagrant machine not running")

    def vagrant_file(self):
        """Return the Vagrantfile used for the vagrant machine."""
        for i in walk_up(self.cwd):
            directory, _, nondirs = i
            if 'Vagrantfile' in nondirs:
                return os.path.join(directory, 'Vagrantfile')

    @property
    def status(self):
        """Return the status of the vagrant machine."""
        out = subprocess.check_output(
            'vagrant status', shell=True, cwd=self.cwd)
        return Status(out)

    def ssh(self):
        """Provide ssh access to the vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        out = subprocess.check_output(
            'vagrant ssh-config', shell=True, cwd=self.cwd)
        return SSH(out)

    def port(self):
        """Return a list of port mappings between this and the vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")
        out = subprocess.check_output('vagrant port', shell=True, cwd=self.cwd)
        matches = re.findall(r'(\d+) \(.*\)\s*=>\s*(\d+)\s*\(.*\)', out)
        return matches

    def provision(self):
        """Provision the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        subprocess.check_output('vagrant provision', shell=True, cwd=self.cwd)

    def reload(self):
        """Reload the Vagrantfile for the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        subprocess.check_output('vagrant reload', shell=True, cwd=self.cwd)

    def ssh_config(self):
        """Return the ssh-config of the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")
        return subprocess.check_output('vagrant ssh-config', shell=True, cwd=self.cwd)

    def destroy(self):
        """Destroy the underlying vagrant machine."""
        subprocess.check_output('vagrant destroy', shell=True, cwd=self.cwd)

    def halt(self):
        """Halt the underlying vagrant machine."""
        subprocess.check_output('vagrant halt', shell=True, cwd=self.cwd)

    def up(self):
        """Start the underlying vagrant machine."""
        subprocess.check_output('vagrant up', shell=True, cwd=self.cwd)

    def suspend(self):
        """Suspend the underlying vagrant machine."""
        subprocess.check_output('vagrant suspend', shell=True, cwd=self.cwd)

    def resume(self):
        """Resume the underlying vagrant machine."""
        if self.status.saved:
            raise RuntimeError("Vagrant machine not suspended (saved)")
        subprocess.check_output('vagrant resume', shell=True, cwd=self.cwd)

    def version(self):
        """Return the version of the vagrant machine."""
        out = subprocess.check_output(
            'vagrant version', shell=True, cwd=self.cwd)
        m = re.search('Installed Version: (\d+\.\d+\.\d+)', out)
        return m.group(1)
