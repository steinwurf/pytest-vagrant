import os
import sys
import subprocess


class Shell(object):
    """ A shell object for running commands """

    def __init__(self, log):
        """ Constructor

        :param log: A logging object
        """
        self.log = log

    def run(self, cmd, cwd=None):
        """ Run a command.

        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run.
        """

        self.log.info(cmd)

        # Modified from: https://stackoverflow.com/a/4418193/246759
        with subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as process:

            stdout = []

            # Poll process for new output until finished
            while True:
                nextline = process.stdout.readline().decode(sys.stdout.encoding)

                if nextline == '' and process.poll() is not None:
                    break

                self.log.debug(nextline)

                stdout.append(nextline)

            _, error = process.communicate()

            output = ''.join(stdout)
            error = error.decode('utf-8')

            if (process.returncode == 0):
                return output
            else:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode, cmd=cmd,
                    output=str({'stdout': output, 'stderr': error}))
