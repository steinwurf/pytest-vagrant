from __future__ import print_function

import os
import sys
import re

from paramiko import SSHClient, AutoAddPolicy

class SSH(object):
    """An SSH Connection
    """
    def __init__(self, ssh_config):
        self.hostname = re.search(r'HostName (.*)', ssh_config).group(1)
        self.username = re.search(r'User (.*)', ssh_config).group(1)
        self.port = re.search(r'Port (.*)', ssh_config).group(1)
        self.key_filename = re.search(r'IdentityFile (.*)', ssh_config).group(1)

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)
        self.sftp = None

    def open(self):
        """Open the ssh connection."""
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)

    def close(self):
        """Close the ssh connection."""
        if self.sftp:
            self.sftp.close()
        self.client.close()

    def run(self, cmd):
        """Run command on remote."""
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

    def put(self, *args):
        """Transfer files from this machine to the remote.
        The locations of the files should be given in pairs.

        Example:

            ssh.put(
                '/local/file1', '/remote/location1',
                '/local/file2', '/remote/location2',
                # ...
                '/local/fileN', '/remote/locationN')
        """
        if self.sftp is None:
            self.sftp = self.client.open_sftp()

        for i in range(0, len(args), 2):
            localpath, remotepath = args[i:i + 2]
            localpath = os.path.abspath(localpath)
            self.sftp.put(localpath, remotepath)

            statinfo = os.stat(localpath)
            self.sftp.chmod(remotepath, statinfo.st_mode)

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
        if self.sftp is None:
            self.sftp = self.client.open_sftp()

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
        if self.sftp is None:
            self.sftp = self.client.open_sftp()

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
