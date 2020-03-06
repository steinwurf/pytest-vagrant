import os

from . import machine_status
from . import parse_format
from . import parse
from . import machine


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
