# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function
import re

# Import 3rd-party libs
from paramiko import SSHClient, AutoAddPolicy


class SSH(object):
    """An SSH Connection
    """

    def __init__(self, ssh_config):
        self.hostname = re.search(r'HostName (.*)', ssh_config).group(1)
        self.username = re.search(r'User (.*)', ssh_config).group(1)
        self.port = re.search(r'Port (.*)', ssh_config).group(1)
        self.key_filename = re.search(
            r'IdentityFile (.*)', ssh_config).group(1)

        self.sftp = None
        self.client = None

    def open(self):
        """Open the SSH connection."""

        assert self.sftp is None
        assert self.client is None

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)

        self.sftp = self.client.open_sftp()

    def close(self):
        """Close the SSH connection."""
        assert self.sftp is not None
        assert self.client is not None

        self.sftp.close()
        self.client.close()

        self.sftp = None
        self.client = None

    def __enter__(self):
        """Use SSH with the with statement."""
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Use SSH with the with statement."""
        self.close()
