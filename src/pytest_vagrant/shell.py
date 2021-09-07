import subprocess


class Shell(object):
    """A shell object for running commands"""

    def run(self, cmd, cwd):
        """Run a command.

        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """
        return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True)
