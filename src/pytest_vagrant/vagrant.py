import os
import json

from .machine_factory import MachineFactory
from .cloud_factory import CloudFactory
from .shell import Shell
from .vagrantfile import Vagrantfile
from .log import setup_logging
from .ssh import SSH


def default_machines_dir():
    """ This is where we put the Vagrantfiles and run vagrant commands """
    # https://stackoverflow.com/a/4028943
    home_dir = os.path.join(os.path.expanduser("~"))
    return os.path.join(home_dir, '.pytest_vagrant')


def make_vagrant():
    """ Creates a new Vagrant object """
    log = setup_logging(verbose=False)

    shell = Shell(log=log)
    machines_dir = default_machines_dir()

    machine_factory = MachineFactory(
        shell=shell, machines_dir=machines_dir, ssh_factory=SSH,
        log=log)

    cloud_factory = CloudFactory(shell=shell)
    vagrantfile = Vagrantfile()

    return Vagrant(machine_factory=machine_factory,
                   cloud_factory=cloud_factory, shell=shell,
                   vagrantfile=vagrantfile)


class Vagrant(object):
    """ Vagrant provides access to a virtual machine through vagrant."""

    def __init__(self, machine_factory, cloud_factory, shell, vagrantfile):
        """ Creates a new Vagrant object

        :param machines_factory: Factory object to build Machine objects
        :param cloud_factory: Factory object to build Cloud objects
        :param shell: A Shell object for running commands
        :param vagrantfile: A Vagrantfile object
        """
        self.machine_factory = machine_factory
        self.cloud_factory = cloud_factory
        self.shell = shell
        self.vagrantfile = vagrantfile

    def from_box(self, name, box, box_version=None, reset=False):
        """ Create a machine from the specified box.

        :param name: The name chosen for this machine as a string.
        :param box: The Vagrant box to use as a string
        :param box_version: The version of the box to use or None if no
            version
        :param reset: If true we first restore to the 'reset' snapshot
        """

        # Prune Vagrant's state to ensure we have no stale info
        self.shell.run(cmd="vagrant global-status --prune", cwd=None)

        machine = self.machine_factory(box=box, name=name)

        if not os.path.isdir(machine.cwd):
            os.makedirs(machine.cwd)
            self.vagrantfile.write(
                name=machine.slug, box=box, box_version=box_version,
                cwd=machine.cwd)

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

    def cloud(self, token=None):
        """ Work with the Vagrant cloud

        """
        return self.cloud_factory(token=token)
