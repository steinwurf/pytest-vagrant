import subprocess


class Shell(object):

    def run(self, cmd, cwd):
        return subprocess.check_output(cmd, shell=True, cwd=cwd)
