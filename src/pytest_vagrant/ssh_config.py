class SSHConfig(object):
    def __init__(self, hostname, username, port, identityfile):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.identityfile = identityfile
