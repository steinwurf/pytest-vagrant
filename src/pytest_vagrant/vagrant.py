# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import subprocess
import re
import os
import hashlib
import slugify
import csv

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
    v.name = "{name}"
  end
end
""".strip()


class Format(object):
    """ Machine readable format returned by Vagrant"""
    TIMESTAMP = 0
    TARGET = 1
    TYPE = 2
    DATA = 3
    EXTRA = 4


class MachineStatus(object):
    """Wraps the vagrant status."""
    # Some machine-readable state values returned by status
    # There are likely some missing, but if you use vagrant you should
    # know what you are looking for.
    # These exist partly for convenience and partly to document the output
    # of vagrant.
    RUNNING = 'running'  # vagrant up
    NOT_CREATED = 'not_created'  # vagrant destroy
    POWEROFF = 'poweroff'  # vagrant halt
    ABORTED = 'aborted'  # The VM is in an aborted state
    SAVED = 'saved'  # vagrant suspend
    # LXC statuses
    STOPPED = 'stopped'
    FROZEN = 'frozen'
    # libvirt
    SHUTOFF = 'shutoff'

    def __init__(self, status):
        self.status = status
        self.running = self.status == MachineStatus.RUNNING
        self.not_created = self.status == MachineStatus.NOT_CREATED
        self.poweroff = self.status == MachineStatus.POWEROFF
        self.aborted = self.status == MachineStatus.ABORTED
        self.saved = self.status == MachineStatus.SAVED
        self.stopped = self.status == MachineStatus.STOPPED
        self.frozen = self.status == MachineStatus.FROZEN
        self.shutoff = self.status == MachineStatus.SHUTOFF

    def __str__(self):
        return self.status


class Shell(object):

    def run(self, cmd, cwd):
        return subprocess.check_output(
            cmd, shell=True, cwd=cwd)


def parse_status(output):

    for row in csv.reader(output.splitlines()):

        if row[Format.TYPE] == 'state':
            return row[Format.DATA]

    raise RuntimeError("Parsing state failed")


def parse_snapshot_list(output):
    snapshots = []

    for row in csv.reader(output.splitlines()):

        if row[Format.DATA] not in ["detail", "output"]:
            continue

        # if the is a space in the extra data we don't have a valid
        # snapshot
        if " " in row[Format.EXTRA]:
            continue

        snapshots.append(row[Format.EXTRA])

    return snapshots


class SSHConfig(object):
    def __init__(self, hostname, username, port, identityfile):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.identityfile = identityfile


def parse_ssh_config(output):

    hostname = re.search(r'HostName (.*)', output).group(1)
    username = re.search(r'User (.*)', output).group(1)
    port = int(re.search(r'Port (.*)', output).group(1))
    identityfile = re.search(r'IdentityFile (.*)', output).group(1)

    return SSHConfig(hostname=hostname, username=username, port=port,
                     identityfile=identityfile)


class Machine(object):

    def __init__(self, box, name, slug, cwd, shell, ssh_factory):
        self.box = box
        self.name = name
        self.slug = slug
        self.cwd = cwd
        self.shell = shell
        self.ssh_factory = ssh_factory

    @property
    def status(self):
        """Return the status of the Vagrant machine."""
        output = self.shell.run(
            cmd='vagrant status --machine-readable', cwd=self.cwd)

        return MachineStatus(status=parse_status(output=output))

    def snapshot_list(self):
        """Return a list of snapshots for the Vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")

        output = self.shell.run(
            cmd='vagrant snapshot list --machine-readable', cwd=self.cwd)

        return parse_snapshot_list(output=output)

    def snapshot_save(self, snapshot):
        """ Restore the machine to a saved snapshot """
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        self.shell.run(cmd='vagrant snapshot save {}'.format(
            snapshot), cwd=self.cwd)

    def snapshot_restore(self, snapshot):
        """ Restore the machine to a saved snapshot """
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        self.shell.run(cmd='vagrant snapshot restore {}'.format(
            snapshot), cwd=self.cwd)

    def ssh_config(self):
        """Return the ssh-config of the vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        output = self.shell.run('vagrant ssh-config', cwd=self.cwd)
        config = parse_ssh_config(output=output)

        print("output: " + output)

        return config

    def ssh(self):
        """Provide ssh access to the Vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        print("ssh")
        return self.ssh_factory(ssh_config=self.ssh_config())

    def up(self):
        """Start the underlying vagrant machine."""
        self.shell.run(cmd='vagrant up', cwd=self.cwd)


def default_machines_dir():
    """ This is where we put the Vagrantfiles and run vagrant commands """
    # https://stackoverflow.com/a/4028943
    home_dir = os.path.join(os.path.expanduser("~"))
    return os.path.join(home_dir, '.pytest_vagrant')


class MachineFactory(object):

    def __init__(self, shell, machines_dir, ssh_factory):
        self.shell = shell
        self.machines_dir = machines_dir
        self.ssh_factory = ssh_factory

    def __call__(self, box, name):

        # Get the current working directory for this machine
        slug = slugify.slugify(text=name + '_' + box, separator='_')
        cwd = os.path.join(self.machines_dir, slug)

        return Machine(name=name, box=box, slug=slug, cwd=cwd, shell=self.shell,
                       ssh_factory=self.ssh_factory)

    @staticmethod
    def default_machines_dir():
        """ This is where we put the Vagrantfiles and run vagrant commands """
        # https://stackoverflow.com/a/4028943
        home_dir = os.path.join(os.path.expanduser("~"))
        return os.path.join(home_dir, '.pytest_vagrant')


class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant.

    Example:

        def test_this_function(vagrant):
            with vagrant.ssh() as ssh:
                ssh.put('build/executable', 'test/executable')
                stdout, stderr = ssh.run('./test/executable')
                assert 'hello world' in stdout
    """

    def __init__(self, machine_factory):
        """ Creates a new Vagrant object

        :param
        :param machines_dir: The machines_dir to where the Vagrantfiles and vagrant commands
                     will run.
        """
        self.machine_factory = machine_factory

    def from_box(self, box, name, reset=False):
        """ Create a machine from the specified box.

        :param box: The Vagrant box to use as a string
        :param name: The name chosen for this machine as a string.
        """

        machine = self.machine_factory(box=box, name=name)

        if not os.path.isdir(machine.cwd):
            os.makedirs(machine.cwd)
            self._write_vagrantfile(machine)

        print(repr(machine.status.status))
        print(repr(machine.status.not_created))
        if machine.status.not_created or machine.status.poweroff:
            machine.up()

        # Is this the first time we boot the machine
        snapshots = machine.snapshot_list()

        if 'reset' not in snapshots:
            machine.snapshot_save('reset')
        elif reset:

            if 'reset' not in snapshots:
                raise RuntimeError("Trying to reset without snapshot!")

            machine.snapshot_restore('reset')

        return machine

    def _write_vagrantfile(self, machine):

        assert os.path.isdir(machine.cwd)

        vagrantfile_path = os.path.join(machine.cwd, "Vagrantfile")
        assert not os.path.isfile(vagrantfile_path)

        vagrantfile_content = VAGRANTFILE_TEMPLATE.format(
            name=machine.slug, box=machine.box)

        with open(vagrantfile_path, 'w') as vagrantfile:
            vagrantfile.write(vagrantfile_content)

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
