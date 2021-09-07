class SSHConnection(object):
    """An active SSH connection"""

    def __init__(self, ssh_client, sftp, cwd):
        """Create a new instance

        :param ssh_client: The paramiko.SSHClient
        :param sftp: The SFTP object
        :param cwd: The current working directory, where we will execute
            commands
        """
        self.ssh_client = ssh_client
        self.sftp = sftp
        self.cwd = cwd
