


class Status(object):
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
    # # LXC statuses
    # STOPPED = 'stopped'
    # FROZEN = 'frozen'
    # # libvirt
    # SHUTOFF = 'shutoff'

    def __init__(self, status):
        self.status = status

        self.running = 'running' == self.status # vagrant up
        self.not_created = 'not created' == self.status # vagrant destroy
        self.poweroff = 'poweroff' == self.status # vagrant halt
        self.aborted = 'aborted' == self.status # the vm is in an aborted state
        self.saved = 'saved' == self.status # vagrant suspend

    def __str__(self):
        return self.status
