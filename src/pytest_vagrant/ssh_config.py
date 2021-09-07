class SSHConfig(object):
    """A SSH configuration"""

    def __init__(self, hostname, username, port, identityfile):
        """Create a new object

        :param hostname: The hostname of the SSH server
        :param username: The username to use for login
        :param port: The port where the SSH server is listening for connections
        :identityfile: The key to use for login
        """
        self.hostname = hostname
        self.username = username
        self.port = port
        self.identityfile = identityfile
