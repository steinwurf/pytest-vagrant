# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import subprocess
import re
import os
import hashlib

from pytest_vagrant.ssh import SSH
from pytest_vagrant.status import Status
from pytest_vagrant.utils import walk_up

INSTALLED_VERSION_RE = re.compile(r'Installed Version: (\d+\.\d+\.\d+)')


class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant.

    Example:

        def test_this_function(vagrant):
            with vagrant.ssh() as ssh:
                ssh.put('build/executable', 'test/executable')
                stdout, stderr = ssh.run('./test/executable')
                assert 'hello world' in stdout
    """

    def __init__(self, project, path=None):
        """ Creates a new Vagrant object

        :param path: The path to where the Vagrantfiles and vagrant commands
                     will run.
        """
        self.project = project
        self.path = path if path is None else self.default_path()

    def from_box(box, name):
        """ Create a machine from the specified box.

        :param box: The Vagrant box to use as a string
        :param name: The name chosen for this machine as a string. Should be
            should be project specific.
        """
        box_hash = hashlib.sha1(box + name.encode('utf-8')).hexdigest()[:6]

    @staticmethod
    def default_path():
        """ This is where we put the Vagrantfiles and run vagrant commands """
        # https://stackoverflow.com/a/4028943
        home_path = os.path.join(os.path.expanduser("~"))
        return os.path.join(home_path, '.pytest_vagrant')

    # def __init__(self, vagrantfile=None):

    #     if vagrantfile is None:
    #         self.cwd = os.getcwd()
    #     elif os.path.isfile(vagrantfile):
    #         self.cwd = os.path.dirname(vagrantfile)
    #     elif os.path.isdir(vagrantfile):
    #         self.cwd = vagrantfile
    #     else:
    #         raise RuntimeError(
    #             "Invalid vagrantfile path {}.".format(vagrantfile))

    #     # The command 'vagrant validate' was not introduced until vagrant
    #     # version 1.9.4. https://www.hashicorp.com/blog/vagrant-1-9-4
    #     #
    #     # We should check for the version.
    #     version = subprocess.check_output(
    #         'vagrant --version', shell=True, cwd=self.cwd)

    #     if version < "1.9.4":
    #         raise RuntimeError("Vagrant version above or equal to 1.9.4 "
    #                            "required. You have {}".format(version))

    #     try:
    #         subprocess.check_output(
    #             'vagrant validate', shell=True, cwd=self.cwd)
    #     except subprocess.CalledProcessError as e:
    #         print("Unable to validate vagrant file, are you sure it exists? "
    #               "Running vagrant validate in {}".format(self.cwd))
    #         raise e

    #     if self.status.not_created or self.status.poweroff:
    #         print("run up")
    #         self.up()
    #     elif self.status.saved:
    #         print("run resume")
    #         self.resume()

    #     if not self.status.running:
    #         raise RuntimeError(
    #             "Despite our efforts, the vagrant machine not running")

    # def vagrant_file(self):
    #     """Return the Vagrantfile used for the vagrant machine."""
    #     for i in walk_up(self.cwd):
    #         directory, _, nondirs = i
    #         if 'Vagrantfile' in nondirs:
    #             return os.path.join(directory, 'Vagrantfile')

    # @property
    # def status(self):
    #     """Return the status of the vagrant machine."""
    #     out = subprocess.check_output(
    #         'vagrant status', shell=True, cwd=self.cwd)
    #     return Status(out)

    # def ssh(self):
    #     """Provide ssh access to the vagrant machine."""
    #     if not self.status.running:
    #         raise RuntimeError("Vagrant machine not running")

    #     out = subprocess.check_output(
    #         'vagrant ssh-config', shell=True, cwd=self.cwd)
    #     return SSH(out)

    # def port(self):
    #     """Return a list of port mappings between this and the vagrant machine."""
    #     if not self.status.running:
    #         raise RuntimeError("Vagrant machine not running")
    #     out = subprocess.check_output('vagrant port', shell=True, cwd=self.cwd)
    #     matches = re.findall(r'(\d+) \(.*\)\s*=>\s*(\d+)\s*\(.*\)', out)
    #     return matches

    # def provision(self):
    #     """Provision the vagrant machine."""
    #     if self.status.not_created:
    #         raise RuntimeError("Vagrant machine not created")
    #     subprocess.check_output('vagrant provision', shell=True, cwd=self.cwd)

    # def reload(self):
    #     """Reload the Vagrantfile for the vagrant machine."""
    #     if self.status.not_created:
    #         raise RuntimeError("Vagrant machine not created")
    #     subprocess.check_output('vagrant reload', shell=True, cwd=self.cwd)

    # def ssh_config(self):
    #     """Return the ssh-config of the vagrant machine."""
    #     if self.status.not_created:
    #         raise RuntimeError("Vagrant machine not created")
    #     if not self.status.running:
    #         raise RuntimeError("Vagrant machine not running")
    #     return subprocess.check_output('vagrant ssh-config', shell=True, cwd=self.cwd)

    # def reset(self):
    #     """ Reset the vagrant box to it's original state. """

    #     # From https://serverfault.com/a/753801
    #     self.destroy()
    #     self.up()

    # def destroy(self):
    #     """Destroy the underlying vagrant machine."""
    #     subprocess.check_output(
    #         'vagrant destroy --force', shell=True, cwd=self.cwd)

    # def halt(self):
    #     """Halt the underlying vagrant machine."""
    #     subprocess.check_output('vagrant halt', shell=True, cwd=self.cwd)

    # def up(self):
    #     """Start the underlying vagrant machine."""
    #     subprocess.check_output('vagrant up', shell=True, cwd=self.cwd)

    # def suspend(self):
    #     """Suspend the underlying vagrant machine."""
    #     subprocess.check_output('vagrant suspend', shell=True, cwd=self.cwd)

    # def resume(self):
    #     """Resume the underlying vagrant machine."""
    #     if self.status.saved:
    #         raise RuntimeError("Vagrant machine not suspended (saved)")
    #     subprocess.check_output('vagrant resume', shell=True, cwd=self.cwd)

    # def snapshot_list(self):
    #     """Return a list of snapshots for the mach."""
    #     if self.status.not_created:
    #         raise RuntimeError("Vagrant machine not created")

    #     output = subprocess.check_output(
    #         'vagrant snapshot list',
    #         shell=True, cwd=self.cwd)

    #     if 'No snapshots have been taken yet!' in output:
    #         return []
    #     else:
    #         return output.splitlines()

    # def snapshot_restore(self, snapshot):
    #     """ Restore the machine to a saved snapshot """
    #     if not self.status.running:
    #         raise RuntimeError("Vagrant machine not running")

    #     return subprocess.check_output(
    #         'vagrant snapshot restore {}'.format(snapshot),
    #         shell=True, cwd=self.cwd)

    # def snapshot_save(self, snapshot):
    #     """ Restore the machine to a saved snapshot """
    #     if not self.status.running:
    #         raise RuntimeError("Vagrant machine not running")

    #     return subprocess.check_output(
    #         'vagrant snapshot save {}'.format(snapshot),
    #         shell=True, cwd=self.cwd)

    # def version(self):
    #     """Return the version of the vagrant machine."""
    #     out = subprocess.check_output(
    #         'vagrant version', shell=True, cwd=self.cwd)
    #     m = INSTALLED_VERSION_RE.search(out)
    #     return m.group(1)
