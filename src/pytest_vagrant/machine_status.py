
class MachineStatus(object):
    """Wraps the vagrant status.

    Some machine-readable state values returned by status
    There are likely some missing, but if you use vagrant you should
    know what you are looking for.
    These exist partly for convenience and partly to document the output
    of vagrant.
    """

    RUNNING = 'running'  # vagrant up
    NOT_CREATED = 'not_created'  # vagrant destroy
    POWEROFF = 'poweroff'  # vagrant halt
    ABORTED = 'aborted'  # The VM is in an aborted state
    SAVED = 'saved'  # vagrant suspend
    STOPPED = 'stopped'  # LXC status
    FROZEN = 'frozen'  # LXC status
    SHUTOFF = 'shutoff'  # libvirt

    def __init__(self, status):
        """ Create a new instance.

        :param status: The status as a string
        """

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
