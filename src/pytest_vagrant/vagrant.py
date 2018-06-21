import pytest
import subprocess
import re
import os
import py

from ssh import SSH
from status import Status
from utils import walk_up

@pytest.fixture(scope='session')
def vagrant():
    """ Creates the py.test fixture to make it usable withing the unit tests.
    See the Vagrant class for more information.
    """
    return Vagrant()

class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant.

    Example:

        def test_this_function(vagrant):
            with vagrant.ssh() as ssh:
                ssh.put('build/executable', 'test/executable')
                stdout, stderr = ssh.run('./test/executable')
                assert 'hello world' in stdout
    """
    def __init__(self):
        try:
            subprocess.check_output('vagrant validate', shell=True)
        except subprocess.CalledProcessError as e:
            print("Unable to validate vagrant file, are you sure it exists?")
            raise e

        if self.status.not_created or self.status.poweroff:
            print "run up"
            self.up()
        elif self.status.saved:
            print "run resume"
            self.resume()

        if not self.status.running:
            raise RuntimeError("Dispite our efforts, the vagrant machine not running")

    def vagrant_file(self):
        """Return the Vagrantfile used for the vagrant machine."""
        for i in walk_up(os.curdir):
            directory, _, nondirs = i
            if 'Vagrantfile' in nondirs:
                return os.path.join(directory, 'Vagrantfile')

    @property
    def status(self):
        """Return the status of the vagrant machine."""
        out = subprocess.check_output('vagrant status', shell=True)
        return Status(out)

    def ssh(self):
        """Provide ssh access to the vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        out = subprocess.check_output('vagrant ssh-config', shell=True)
        return SSH(out)

    def port(self):
        """Return a list of port mappings between this and the vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")
        out = subprocess.check_output('vagrant port', shell=True)
        matches = re.findall(r'(\d+) \(.*\)\s*=>\s*(\d+)\s*\(.*\)', out)
        return matches

    def provision(self):
        """Provision the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        subprocess.check_output('vagrant provision', shell=True)

    def reload(self):
        """Reload the Vagrantfile for the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        subprocess.check_output('vagrant reload', shell=True)

    def ssh_config(self):
        """Return the ssh-config of the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")
        return subprocess.check_output('vagrant ssh-config', shell=True)

    def destroy(self):
        """Destroy the underlying vagrant machine."""
        subprocess.check_output('vagrant destroy', shell=True)

    def halt(self):
        """Halt the underlying vagrant machine."""
        subprocess.check_output('vagrant halt', shell=True)

    def up(self):
        """Start the underlying vagrant machine."""
        subprocess.check_output('vagrant up', shell=True)

    def suspend(self):
        """Suspend the underlying vagrant machine."""
        subprocess.check_output('vagrant suspend', shell=True)

    def resume(self):
        """Resume the underlying vagrant machine."""
        if self.status.saved:
            raise RuntimeError("Vagrant machine not suspended (saved)")
        subprocess.check_output('vagrant resume', shell=True)

    def version(self):
        """Return the version of the vagrant machine."""
        out = subprocess.check_output('vagrant version', shell=True)
        m = re.search('Installed Version: (\d+\.\d+\.\d+)', out)
        return m.group(1)
