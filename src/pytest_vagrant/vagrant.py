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

# Vagrant uses the Vagrantfile as configuration file. You can read more
# about it here:
# https://www.vagrantup.com/docs/vagrantfile/
VAGRANTFILE_TEMPLATE = r"""
Vagrant.configure("2") do |config|
  config.vm.box = "{box}"
  config.vm.provider "virtualbox" do |v|
    v.name = "{unique_name}"
  end
end
""".strip()


class MachineStatus(object):
    """Wraps the vagrant status."""
    # Some machine-readable state values returned by status
    # There are likely some missing, but if you use vagrant you should
    # know what you are looking for.
    # These exist partly for convenience and partly to document the output
    # of vagrant.
    RUNNING = 'running'  # vagrant up
    NOT_CREATED = 'not created'  # vagrant destroy
    POWEROFF = 'poweroff'  # vagrant halt
    ABORTED = 'aborted'  # The VM is in an aborted state
    SAVED = 'saved'  # vagrant suspend
    # LXC statuses
    STOPPED = 'stopped'
    FROZEN = 'frozen'
    # libvirt
    SHUTOFF = 'shutoff'

    def __init__(self, out):
        m = re.search(r'\w+\s+(.+)\s+\(.+\)', out)
        self.status = m.group(1)

        self.running = self.status == Status.RUNNING
        self.not_created = self.status == Status.NOT_CREATED
        self.poweroff = self.status == Status.POWEROFF
        self.aborted = self.status == Status.ABORTED
        self.saved = self.status == Status.SAVED
        self.stopped = self.status == Status.STOPPED
        self.frozen = self.status == Status.FROZEN
        self.shutoff = self.status == Status.SHUTOFF

    def __str__(self):
        return self.status


class MachineInfo(object):

    def __init__(self, project, box, name, machines_dir):

        hash_input = str(project + name + box).encode('utf-8')
        self.hash = hashlib.sha1(hash_input).hexdigest()[:6]

        self.project = project
        self.box = box
        self.name = name
        self.unique_name = name + '_' + self.hash
        self.cwd = os.path.join(machines_dir, self.unique_name)


class Machine(object):

    def __init__(self, machine_info):
        self.machine_info = machine_info

    def status(self):
        """Return the status of the vagrant machine."""
        out = self._run('vagrant status')

        return MachineStatus(out)

    def up(self):
        """Start the underlying vagrant machine."""
        self._run('vagrant up')

    def _run(self, cmd):
        return subprocess.check_output(
            cmd, shell=True, cwd=self.machine_info.cwd)


class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant.

    Example:

        def test_this_function(vagrant):
            with vagrant.ssh() as ssh:
                ssh.put('build/executable', 'test/executable')
                stdout, stderr = ssh.run('./test/executable')
                assert 'hello world' in stdout
    """

    def __init__(self, project, machines_dir=None):
        """ Creates a new Vagrant object

        :param
        :param machines_dir: The machines_dir to where the Vagrantfiles and vagrant commands
                     will run.
        """
        self.project = project
        self.machines_dir = machines_dir if machines_dir is not None else self.default_machines_dir()

    def from_box(self, box, name):
        """ Create a machine from the specified box.

        :param box: The Vagrant box to use as a string
        :param name: The name chosen for this machine as a string.
        """

        # Lets create a unique id for this machine
        machine_info = MachineInfo(project=self.project, box=box,
                                   name=name, machines_dir=self.machines_dir)

        if not os.path.isdir(machine_info.cwd):
            os.makedirs(machine_info.cwd)
            self._write_vagrantfile(machine_info)

        machine = Machine(machine_info=machine_info)

        status = machine.status()
        print(status)

        if status.not_created or status.poweroff:
            machine.up()

        # # Is this the first time we boot the machine
        # snapshots = machine.snapshot_list()

        # if 'initial_state' not in snapshots:
        #     machine.save_snapshot('initial_state')

        #     self.up()
        #     self.save_snapshot('initial_state')

        #     raise RuntimeError("No machine dir")

    def _write_vagrantfile(self, machine_info):

        assert os.path.isdir(machine_info.cwd)

        vagrantfile_path = os.path.join(machine_info.cwd, "Vagrantfile")
        assert not os.path.isfile(vagrantfile_path)

        vagrantfile_content = VAGRANTFILE_TEMPLATE.format(
            unique_name=machine_info.unique_name, box=machine_info.box)

        with open(vagrantfile_path, 'w') as vagrantfile:
            vagrantfile.write(vagrantfile_content)

    @staticmethod
    def default_machines_dir():
        """ This is where we put the Vagrantfiles and run vagrant commands """
        # https://stackoverflow.com/a/4028943
        home_dir = os.path.join(os.path.expanduser("~"))
        return os.path.join(home_dir, '.pytest_vagrant')

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
