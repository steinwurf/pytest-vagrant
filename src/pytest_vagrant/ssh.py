# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import re
import os
import stat

from paramiko import SSHClient, AutoAddPolicy

import pytest_vagrant


class SSH(object):
    """An SSH Connection
    """

    def __init__(self, ssh_config):
        self.ssh_config = ssh_config
        print("init: " + repr(self.ssh_config))
        self.sftp = None
        self.client = None
        self.cwd = ''

    def open(self):
        """Open the SSH connection."""

        assert self.sftp is None
        assert self.client is None

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

        print(repr(self.ssh_config))

        self.client.connect(
            hostname=self.ssh_config.hostname,
            port=self.ssh_config.port,
            username=self.ssh_config.username,
            key_filename=self.ssh_config.identityfile)

        self.sftp = self.client.open_sftp()

        self.cwd = self.chdir(path='~')

    def close(self):
        """Close the SSH connection."""
        assert self.sftp is not None
        assert self.client is not None

        self.sftp.close()
        self.client.close()

        self.sftp = None
        self.client = None

    def run(self, command, cwd=None):
        """Run command on remote."""
        assert self.client is not None

        if cwd is None:
            cwd = self.cwd

        # Make sure we are in the right directory
        command = "cd " + cwd + ";" + command

        _, stdout, stderr = self.client.exec_command(command)

        returncode = stdout.channel.recv_exit_status()
        stdout = ''.join(stdout.readlines())
        stderr = ''.join(stderr.readlines())

        result = pytest_vagrant.RunResult(
            command=command, cwd=cwd,
            stdout=stdout, stderr=stderr, returncode=returncode)

        if result.returncode:
            raise pytest_vagrant.RunResultError(runresult=result)

        return result

    def getcwd(self):
        """ Return the current working directory (cwd).

        All commands will be relative to this location.

        :return: The current working directory
        """
        return self.cwd

    def chdir(self, path):

        # The path is can be absolute or relative to the current
        # working directory
        path = os.path.join(self.cwd, path)

        self.cwd = self.run(command='pwd', cwd=path).stdout.strip()
        assert self.is_dir(path=self.cwd)

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

    def get_file(self, remote_file, local_directory, rename_as=""):
        """Transfer files from the remote to this machine.
        """
        if not os.path.isdir(local_directory):
            raise RuntimeError(
                "Not a valid directory {}".format(local_directory))

        remote_file = os.path.join(self.cwd, remote_file)

        if rename_as:
            local_file = os.path.join(local_directory, rename_as)
        else:
            filename = os.path.basename(remote_file)
            local_file = os.path.join(local_directory, filename)

        self.sftp.get(remotepath=remote_file, localpath=local_file)

        statinfo = self.sftp.stat(remote_file)
        os.chmod(local_file, statinfo.st_mode)

    def is_dir(self, path):
        """ Return true if path is a directory """

        path = os.path.join(self.cwd, path)

        try:
            mode = self.sftp.stat(path=path).st_mode
        except IOError:
            return False

        return stat.S_ISDIR(mode)

    def __enter__(self):
        """Use SSH with the with statement."""
        print("__enter__")
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Use SSH with the with statement."""
        self.close()
