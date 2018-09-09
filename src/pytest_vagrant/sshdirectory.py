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

    def __init__(self, ssh, sftp, cwd):
        self.ssh = ssh
        self.sftp = sftp

        # Some commands like running stats to determine if path is
        # file or directory require abosolute paths
        assert(os.path.isabs(cwd))
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

    def put_file(self, local_file, rename_as=""):
        """Transfer files from this machine to the remote.
        """
        if not os.path.isfile(local_file):
            raise RuntimeError("Not a valid file {}".format(local_file))

        if rename_as:
            remote_file = os.path.join(self.cwd, rename_as)
        else:
            filename = os.path.basename(local_file)
            remote_file = os.path.join(self.cwd, filename)

        self.sftp.put(localpath=local_file, remotepath=remote_file,
                      confirm=True)

        statinfo = os.stat(local_file)
        self.sftp.chmod(path=remote_file, mode=statinfo.st_mode)

    def get_file(self, remote_file, local_file):
        """Transfer files from the remote to this machine.
        """
        remote_file = os.path.join(self.cwd, remote_file)

        self.sftp.get(remotepath=remote_file, localpath=local_file)

        statinfo = self.sftp.stat(remote_file)
        os.chmod(local_file, statinfo.st_mode)

    def rename(self, old_path, new_path):
        self.sftp.rename(oldpath=old_path, newpath=new_path)

    def isdir(self, path):
        """ Return true if path is a directory """

        path = os.path.join(self.cwd, path)

        try:
            mode = self.sftp.stat(path=path).st_mode
        except IOError:
            return False

        return stat.S_ISDIR(mode)

    def listdir(self):
        """ Return a list of files in the directory """
        return self.sftp.listdir(path=self.cwd)

    def rmdir(self, path):

        # Paramiko has a function for removing directories. However,
        # it does not work with non-empty directories. Instead we just
        # resort to basic shell commands
        # https://stackoverflow.com/a/35497166/1717320

        path = os.path.join(self.cwd, path)

        self.run(command="rm -rf %s" % path)

    def mkdir(self, path):

        path = os.path.join(self.cwd, path)

        # As with rmdir Paramiko does not support recursively creating
        # directories so we just resort to shell commands:
        # https://stackoverflow.com/a/14819803/1717320

        self.run(command="mkdir -p %s" % path)

        return SSHDirectory(ssh=self.ssh, sftp=self.sftp, cwd=path)

    def isfile(self, path):
        """ Return true if path is a file """
        path = os.path.join(self.cwd, path)

        try:
            mode = self.sftp.stat(path=path).st_mode
        except IOError:
            print("EXCEPT")
            return False

        return stat.S_ISREG(mode)
