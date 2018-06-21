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
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename)
        self.sftp = self.client.open_sftp()

    def close(self):
        self.sftp.close()
        self.client.close()

    def run(self, cmd):
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
        for i in range(0, len(args), 2):
            localpath, remotepath = args[i:i + 2]
            localpath = os.path.abspath(localpath)
            self.sftp.put(localpath, remotepath)

            statinfo = os.stat(localpath)
            self.sftp.chmod(remotepath, statinfo.st_mode)

    def get(self, *args):
        for i in range(0, len(args), 2):
            remotepath, localpath = args[i:i + 2]
            localpath = os.path.abspath(localpath)
            self.sftp.get(remotepath, localpath)

            statinfo = self.sftp.stat(remotepath)
            os.chmod(localpath, statinfo.st_mode)

    def rm(self, *args):
        for remotepath in args:
            self.sftp.remove(remotepath)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()
