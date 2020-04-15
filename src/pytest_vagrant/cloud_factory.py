from . import cloud


class CloudFactory(object):
    """Build Cloud objects
    """

    def __init__(self, shell):
        self.shell = shell

    def __call__(self, token):
        return cloud.Cloud(token=token, shell=self.shell)
