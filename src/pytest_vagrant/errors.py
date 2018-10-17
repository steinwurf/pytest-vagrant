# -*- coding: utf-8 -*-


class RunResultError(Exception):
    """Exception for SSHDirctory::run"""

    def __init__(self, runresult):
        super(RunResultError, self).__init__(str(runresult))
        self.runresult = runresult


class MatchError(Exception):
    """Exception for output match errors"""

    def __init__(self, match, output):

        message = "Could not match " + match

        message += " in:\n" + output

        super(MatchError, self).__init__(message)
