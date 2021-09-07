import slugify
import os

from . import machine


class MachineFactory(object):
    """Factory object for building Machine objects"""

    def __init__(self, shell, machines_dir, ssh_factory):
        """Instantiate a new object

        :param shell: A Shell object for running commands
        :param machines_dir: The directory where we store the Vagrantfiles and
            where Vagrant stores information about the created virtual machines
        :param ssh_factory: Factory for building SSH objects
        """

        self.shell = shell
        self.machines_dir = machines_dir
        self.ssh_factory = ssh_factory

    def __call__(self, box, name, version):
        """Build a new Machine object.

        :param box: Name of the box to use
        :param name: The name of the virtual machine
        :param version: Version of the box to use
        """
        # Get the current working directory for this machine
        text = name + "_" + box
        if version is not None:
            text += "_" + version

        slug = slugify.slugify(text=text, separator="_")
        cwd = os.path.join(self.machines_dir, slug)

        return machine.Machine(
            name=name,
            box=box,
            version=version,
            slug=slug,
            cwd=cwd,
            shell=self.shell,
            ssh_factory=self.ssh_factory,
        )
