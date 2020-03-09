
import re
import os
import stat
import paramiko

from . import ssh_connection
from . import runresult
from . import errors


class SSH(object):
    """An SSH Connection
    """

    def __init__(self, ssh_config):
        self.ssh_config = ssh_config
        self.connection = None

    def open(self):
        """Open the SSH connection."""

        assert self.connection is None

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=self.ssh_config.hostname,
            port=self.ssh_config.port,
            username=self.ssh_config.username,
            key_filename=self.ssh_config.identityfile)

        sftp = ssh_client.open_sftp()

        # Get home dir
        _, stdout, _ = ssh_client.exec_command("cd ~;pwd")
        cwd = stdout.readline().strip()

        self.connection = ssh_connection.SSHConnection(
            ssh_client=ssh_client, sftp=sftp, cwd=cwd)

    def close(self):
        """Close the SSH connection."""
        self.connection.sftp.close()
        self.connection.ssh_client.close()

        self.connection = None

    def getcwd(self):
        """ Return the current working directory (cwd).

        All commands will be relative to this location.

        :return: The current working directory
        """
        return self.connection.cwd

    def run(self, command, cwd=None):
        """Run command on remote."""

        if cwd is None:
            cwd = self.connection.cwd

        # Make sure we are in the right directory
        command = "cd " + cwd + ";" + command

        _, stdout, stderr = self.connection.ssh_client.exec_command(
            command)

        return_code = stdout.channel.recv_exit_status()
        stdout = ''.join(stdout.readlines())
        stderr = ''.join(stderr.readlines())

        result = runresult.RunResult(
            command=command, cwd=cwd,
            stdout=stdout, stderr=stderr, returncode=return_code)

        if result.returncode:
            raise errors.RunResultError(runresult=result)

        return result

    def chdir(self, path):
        """Change current working directory """

        path = self._resolve_path(path)

        self.connection.cwd = self.run(
            command='pwd', cwd=path).stdout.strip()

    def put_file(self, local_file, rename_as=""):
        """Transfer files from this machine to the remote.
        """
        if not os.path.isfile(local_file):
            raise RuntimeError("Not a valid file {}".format(local_file))

        if rename_as:
            remote_file = os.path.join(self.connection.cwd, rename_as)
        else:
            filename = os.path.basename(local_file)
            remote_file = os.path.join(self.connection.cwd, filename)

        self.connection.sftp.put(localpath=local_file, remotepath=remote_file,
                                 confirm=True)

        statinfo = os.stat(local_file)
        self.connection.sftp.chmod(path=remote_file, mode=statinfo.st_mode)

    def get_file(self, remote_file, local_directory, rename_as=""):
        """Transfer files from the remote to this machine.
        """
        if not os.path.isdir(local_directory):
            raise RuntimeError(
                "Not a valid directory {}".format(local_directory))

        remote_file = self._resolve_path(remote_file)

        if rename_as:
            local_file = os.path.join(local_directory, rename_as)
        else:
            filename = os.path.basename(remote_file)
            local_file = os.path.join(local_directory, filename)

        self.connection.sftp.get(remotepath=remote_file, localpath=local_file)

        statinfo = self.connection.sftp.stat(remote_file)
        os.chmod(local_file, statinfo.st_mode)

    def is_dir(self, path):
        """ Return true if path is a directory """

        # The path is can be absolute or relative to the current
        # working directory
        path = self._resolve_path(path)

        try:
            mode = self.connection.sftp.stat(path=path).st_mode
        except IOError:
            return False

        return stat.S_ISDIR(mode)

    def is_file(self, path):
        """ Return true if path is a file """

        path = self._resolve_path(path)

        try:
            mode = self.connection.sftp.stat(path=path).st_mode
        except IOError:
            return False

        return stat.S_ISREG(mode)

    def unlink(self, path):
        """ Removes a file or sybolic link """
        path = self._resolve_path(path)
        self.run(command='rm {}'.format(path))

    def _resolve_path(self, path):
        # The path is can be absolute or relative to the current
        # working directory
        if path[0] == '/' or path[0] == '~':
            return path
        else:
            return os.path.join(self.connection.cwd, path)

    def __enter__(self):
        """Use SSH with the with statement."""
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Use SSH with the with statement."""
        self.close()
