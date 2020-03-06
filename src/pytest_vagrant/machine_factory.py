import subprocess
import slugify
import os

from . import machine


class MachineFactory(object):

    def __init__(self, shell, machines_dir, ssh_factory):
        self.shell = shell
        self.machines_dir = machines_dir
        self.ssh_factory = ssh_factory

    def __call__(self, box, name):

        # Get the current working directory for this machine
        slug = slugify.slugify(text=name + '_' + box, separator='_')
        cwd = os.path.join(self.machines_dir, slug)

        return machine.Machine(
            name=name, box=box, slug=slug, cwd=cwd, shell=self.shell,
            ssh_factory=self.ssh_factory)
