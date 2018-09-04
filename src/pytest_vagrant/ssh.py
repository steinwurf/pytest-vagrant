from __future__ import print_function

import os
import sys
import re

from paramiko import SSHClient, AutoAddPolicy

import pytest_vagrant.utils


class SSH(object):
    """An SSH Connection
    """

    def __init__(self, ssh_config):
        self.hostname = re.search(r'HostName (.*)', ssh_config).group(1)
        self.username = re.search(r'User (.*)', ssh_config).group(1)
        self.port = re.search(r'Port (.*)', ssh_config).group(1)
        self.key_filename = re.search(
            r'IdentityFile (.*)', ssh_config).group(1)

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)
        self._sftp = None

    def open(self):
        """Open the ssh connection."""
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)

    @property
    def sftp(self):
        if self._sftp is None:
            self._sftp = self.client.open_sftp()

        return self._sftp

    def close(self):
        """Close the ssh connection."""
        if self._sftp:
            self._sftp.close()
        self.client.close()

    def run(self, cmd, cwd=None):
        """Run command on remote."""

        if cwd:
            cmd = "cd " + cwd + ";" + cmd

        _, stdout, stderr = self.client.exec_command(cmd)
        status_code = stdout.channel.recv_exit_status()
        stdout = ''.join(stdout.readlines())
        stderr = ''.join(stderr.readlines())
        print('\nrunning \'{cmd}\''.format(cmd=cmd))
        if stdout:
            print("stdout:\n%s" % stdout)
        if stderr:
            print("stderr:\n%s" % stderr, file=sys.stderr)
        if status_code != 0:
            raise RuntimeError('Command "{}" returned {}.\nstdout: {}\nstderr:{}\n'.format(
                cmd,
                status_code,
                stdout,
                stderr,
            ))
        return stdout, stderr

    def put(self, local_path, remote_path):
        """Transfer files from this machine to the remote.

        Example:

            ssh.put(local_path='local/file1',
                    remote_path='/remote/location1')

        """

        if not os.path.isfile(local_path):
            raise RuntimeError("Not a valid file {}".format(local_path))

        # Save this location so that we can go back here once
        # we've transferred the file
        cwd = self.sftp.getcwd()

        remote_dirs, remote_file = pytest_vagrant.utils.path_split(
            remote_path)

        for path in remote_dirs:

            try:
                # http://docs.paramiko.org/en/2.4/api/sftp.html
                self.sftp.chdir(path=path)
            except IOError:
                self.sftp.mkdir(path=path)
                self.sftp.chdir(path=path)

        self.sftp.put(localpath=local_path,
                      remotepath=remote_file, confirm=True)

        statinfo = os.stat(local_path)
        self.sftp.chmod(path=remote_file, mode=statinfo.st_mode)

        self.sftp.chdir(path=cwd)

    def listdir(self, path='.'):
        """ Return a list of files in the directory """
        return self.sftp.listdir(path=path)

    def isdir(self, path):
        """ Return true if path is a directory """
        is_directory = True

        try:
            self.sftp.chdir(path)
        except IOError:
            is_directory = False

        self.sftp.chdir(None)
        return is_directory

    def mkdir(self, path, cwd=None):
        self.run(cmd='mkdir -p %s' % path, cwd=cwd)

    def rmdir(self, path, cwd=None):
        """ Remove the directory """

        # Paramiko has a rmdir function.. but for some reason
        # it fails to work..

        self.run(cmd='rm -rf %s' % path, cwd=cwd)

    def get(self, *args):
        """Transfer files from the remote to this machine.
        The locations of the files should be given in pairs.

        Example:

            ssh.get(
                '/remote/file1', '/local/location1',,
                '/remote/file2', '/local/location2',,
                # ...
                '/remote/fileN', '/local/locationN')
        """

        for i in range(0, len(args), 2):
            remotepath, localpath = args[i:i + 2]
            localpath = os.path.abspath(localpath)
            self.sftp.get(remotepath, localpath)

            statinfo = self.sftp.stat(remotepath)
            os.chmod(localpath, statinfo.st_mode)

    def rm(self, remote_files, force=False):
        """Removes files from the remote.

        Example:

            ssh.remove(['/remote/file1', '/remote/file2'], fource)
        """

        if isinstance(remote_files, basestring):
            remote_files = [remote_files]

        for remote_file in remote_files:
            try:
                self.sftp.remove(remote_file)
            except IOError as e:
                if not force:
                    raise e

    def __enter__(self):
        """Use SSH with the with statement."""
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Use SSH with the with statement."""
        self.close()
