from __future__ import print_function

import os
import sys
import re
import stat

import pytest_vagrant.utils
import pytest_vagrant.errors
import pytest_vagrant.runresult


class SSHDirectory(object):
    """
    A directory on the SSH host
    """

    def __init__(self, ssh, sftp, cwd='~'):
        self.ssh = ssh
        self.sftp = sftp
        self.cwd = cwd

    def run(self, command):
        """Run command on remote."""

        # Make sure we are in the right directory
        command = "cd " + self.cwd + ";" + command

        _, stdout, stderr = self.ssh.exec_command(command)

        returncode = stdout.channel.recv_exit_status()
        stdout = ''.join(stdout.readlines())
        stderr = ''.join(stderr.readlines())

        runresult = pytest_vagrant.runresult.RunResult(
            command=command, cwd=self.cwd,
            stdout=stdout, stderr=stderr, returncode=returncode)

        if runresult.returncode:
            raise pytest_vagrant.errors.RunResultError(runresult=runresult)

        return runresult

    def getcwd(self):
        """ Run pwd in the machine """

        # Paramiko has a getcwd function but that relies on the direcotry
        # begin set prio.
        # http://docs.paramiko.org/en/2.4/api/sftp.html
        # So we just roll our own

        result = self.run(command='pwd')
        return result.stdout.strip()

    # def path(self):
    #     return self.ssh.pwd(cwd=self.cwd)

    # def copy_file(self, local_path, rename_as=""):
    #     """Transfer files from this machine to the remote.

    #     This command will create any directories as needed.

    #     Example:

    #         ssh.put(local_path='local/file1',
    #                 remote_path='/remote/location1')

    #     """

    #     if not os.path.isfile(local_path):
    #         raise RuntimeError("Not a valid file {}".format(local_path))

    #     if rename_as:
    #         remote_path = os.path.join(self.cwd, rename_as)
    #     else:
    #         file_name = os.path.basename(local_path)
    #         remote_path = os.path.join(self.cwd, file_name)

    #     self.ssh.put(local_path=local_path, remote_path=remote_path)

    # def listdir(self):
    #     """ Return a list of files in the directory """
    #     return self.ssh.listdir(path=self.cwd)

    # def contains_dir(self, directory):
    #     """ Return true if path is a directory """
    #     path = os.path.join(self.cwd, directory)
    #     return self.ssh.isdir(path)

    def isdir(self, path):
        """ Return true if path is a directory """

        path = os.path.join(self.cwd, path)

        try:
            mode = self.sftp.stat(path=path).st_mode
        except IOError:
            return False

        return stat.S_ISDIR(mode)

    def rmdir(self, path):

        path = os.path.join(self.cwd, path)

        self.sftp.rmdir(path=path)

    def mkdir(self, path):

        path = os.path.join(self.cwd, path)

        remote_dirs = pytest_vagrant.utils.path_split(path=path)

        for path in remote_dirs:
            try:
                # http://docs.paramiko.org/en/2.4/api/sftp.html
                self.sftp.chdir(path=path)
            except IOError:
                self.sftp.mkdir(path=path)
                self.sftp.chdir(path=path)

        self.sftp.chdir(path=None)

        return SSHDirectory(ssh=self.ssh, sftp=self.sftp, cwd=path)

    # def contains_file(self, filename):
    #     files = self.listdir()

    #     for f in files:
    #         if not self.isfile(f):
    #             continue

    #         if os.path.basename(f) == filename:
    #             return True

    #     return False

    # def isfile(self, filename):
    #     return self.ssh.isfile(os.path.join(self.cwd, filename))

    # def mkdir(self, directory):
    #     """ Return true if path is a directory """
    #     self.ssh.mkdir(path=directory, cwd=self.cwd)

    #     return SSHDirectory(ssh=self.ssh,
    #                         cwd=os.path.join(self.cwd, directory))

    # def rmdir(self, directory):
    #     """ Remove the directory """
    #     self.ssh.rmdir(path=directory, cwd=self.cwd)
