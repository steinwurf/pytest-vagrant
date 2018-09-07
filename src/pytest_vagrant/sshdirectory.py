from __future__ import print_function

import os
import sys
import re


class SSHDirectory(object):
    """
    A directory on the SSH host
    """

    def __init__(self, ssh, cwd='~'):
        self.ssh = ssh
        self.cwd = cwd

    def run(self, cmd):
        """Run command on remote."""
        return self.ssh.run(cmd=cmd, cwd=self.cwd)

    def path(self):
        return self.ssh.pwd(cwd=self.cwd)

    def copy_file(self, local_path, rename_as=""):
        """Transfer files from this machine to the remote.

        This command will create any directories as needed.

        Example:

            ssh.put(local_path='local/file1',
                    remote_path='/remote/location1')

        """

        if not os.path.isfile(local_path):
            raise RuntimeError("Not a valid file {}".format(local_path))

        if rename_as:
            remote_path = os.path.join(self.cwd, rename_as)
        else:
            file_name = os.path.basename(local_path)
            remote_path = os.path.join(self.cwd, file_name)

        self.ssh.put(local_path=local_path, remote_path=remote_path)

    def listdir(self):
        """ Return a list of files in the directory """
        return self.ssh.listdir(path=self.cwd)

    def contains_dir(self, directory):
        """ Return true if path is a directory """
        path = os.path.join(self.cwd, directory)
        return self.ssh.isdir(path)

    def contains_file(self, filename):
        files = self.listdir()

        for f in files:
            if not self.isfile(f):
                continue

            if os.path.basename(f) == filename:
                return True

        return False

    def isfile(self, filename):
        return self.ssh.isfile(os.path.join(self.cwd, filename))

    def mkdir(self, directory):
        """ Return true if path is a directory """
        self.ssh.mkdir(path=directory, cwd=self.cwd)

        return SSHDirectory(ssh=self.ssh,
                            cwd=os.path.join(self.cwd, directory))

    def rmdir(self, directory):
        """ Remove the directory """
        self.ssh.rmdir(path=directory, cwd=self.cwd)
