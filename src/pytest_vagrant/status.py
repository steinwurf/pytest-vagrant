import re

class Status(object):
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
    SAVED = 'saved' # vagrant suspend
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
