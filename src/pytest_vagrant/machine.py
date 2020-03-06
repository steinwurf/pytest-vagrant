
from . import parse


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

        return parse.to_status(output=output)

    def snapshot_list(self):
        """Return a list of snapshots for the Vagrant machine."""
        if self.status.not_created:
            raise RuntimeError("Vagrant machine not created")

        output = self.shell.run(
            cmd='vagrant snapshot list --machine-readable', cwd=self.cwd)

        return parse.to_snapshot_list(output=output)

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
        return parse.to_ssh_config(output=output)

    def ssh(self):
        """Provide ssh access to the Vagrant machine."""
        if not self.status.running:
            raise RuntimeError("Vagrant machine not running")

        return self.ssh_factory(ssh_config=self.ssh_config())

    def up(self):
        """Start the underlying vagrant machine."""
        self.shell.run(cmd='vagrant up', cwd=self.cwd)
