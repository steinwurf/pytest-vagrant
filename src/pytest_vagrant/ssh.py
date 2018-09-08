from __future__ import print_function

import os
import sys
import re
import stat

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

    # def run(self, cmd, cwd=None):
    #     """Run command on remote."""

    #     if cwd:
    #         cmd = "cd " + cwd + ";" + cmd

    #     _, stdout, stderr = self.client.exec_command(cmd)
    #     status_code = stdout.channel.recv_exit_status()
    #     stdout = ''.join(stdout.readlines())
    #     stderr = ''.join(stderr.readlines())
    #     print('\nrunning \'{cmd}\''.format(cmd=cmd))
    #     if stdout:
    #         print("stdout:\n%s" % stdout)
    #     if stderr:
    #         print("stderr:\n%s" % stderr, file=sys.stderr)
    #     if status_code != 0:
    #         raise RuntimeError('Command "{}" returned {}.\nstdout: {}\nstderr:{}\n'.format(
    #             cmd,
    #             status_code,
    #             stdout,
    #             stderr,
    #         ))
    #     return stdout, stderr

    # def put(self, local_path, remote_path):
    #     """Transfer files from this machine to the remote.

    #     This command will create any directories as needed.

    #     Example:

    #         ssh.put(local_path='local/file1',
    #                 remote_path='/remote/location1')

    #     """

    #     if not os.path.isfile(local_path):
    #         raise RuntimeError("Not a valid file {}".format(local_path))

    #     # Save this location so that we can go back here once
    #     # we've transferred the file
    #     cwd = self.sftp.getcwd()

    #     remote_dirs, remote_file = pytest_vagrant.utils.path_split(
    #         remote_path)

    #     for path in remote_dirs:

    #         try:
    #             # http://docs.paramiko.org/en/2.4/api/sftp.html
    #             self.sftp.chdir(path=path)
    #         except IOError:
    #             self.sftp.mkdir(path=path)
    #             self.sftp.chdir(path=path)

    #     self.sftp.put(localpath=local_path,
    #                   remotepath=remote_file, confirm=True)

    #     statinfo = os.stat(local_path)
    #     self.sftp.chmod(path=remote_file, mode=statinfo.st_mode)

    #     self.sftp.chdir(path=cwd)

    # def listdir(self, path='.'):
    #     """ Return a list of files in the directory """
    #     return self.sftp.listdir(path=path)

    # def isdir(self, path):
    #     """ Return true if path is a directory """
    #     try:
    #         mode = self.sftp.stat(path=path).st_mode
    #     except IOError:
    #         return False

    #     return stat.S_ISDIR(mode)

    # def pwd(self, cwd):
    #     """ Run pwd in the machine """
    #     stdout, _ = self.run(cmd='pwd', cwd=cwd)
    #     return stdout.strip()

    # def isfile(self, path):
    #     """ Return true if path is a file """
    #     try:
    #         mode = self.sftp.stat(path=path).st_mode
    #     except IOError:
    #         return False

    #     return stat.S_ISREG(mode)

    # def mkdir(self, path, cwd=None):
    #     """ Create a new directory """
    #     self.run(cmd='mkdir -p %s' % path, cwd=cwd)

    # def rmdir(self, path, cwd=None):
    #     """ Remove the directory """

    #     # Paramiko has a rmdir function.. but for some reason
    #     # it fails to work..

    #     self.run(cmd='rm -rf %s' % path, cwd=cwd)

    # def get(self, local_path, remote_path):
    #     """Transfer files from the remote to this machine.
    #     The locations of the files should be given in pairs.

    #     Example:

    #         ssh.get(local_path='/local/file1',
    #                 remote_path='/remote/location1')
    #     """

    #     self.sftp.get(remotepath=remote_path, localpath=local_path)

    #     statinfo = self.sftp.stat(remote_path)
    #     os.chmod(local_path, statinfo.st_mode)

    # def rm(self, remote_files, force=False):
    #     """Removes files from the remote.

    #     Example:

    #         ssh.remove(['/remote/file1', '/remote/file2'], fource)
    #     """

    #     if isinstance(remote_files, basestring):
    #         remote_files = [remote_files]

    #     for remote_file in remote_files:
    #         try:
    #             self.sftp.remove(remote_file)
    #         except IOError as e:
    #             if not force:
    #                 raise e
