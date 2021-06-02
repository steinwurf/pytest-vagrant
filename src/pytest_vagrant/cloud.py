import os
import json

from . import ssh_connection
from . import run_result
from . import errors


class Cloud(object):
    """Vagrant Cloud access
    """

    def __init__(self, token, shell):
        """ Create a new Cloud object

        :param token: The token use to authenticate with Vagrant Cloud
        :param shell: The Shell object to run commands
        """
        self.token = token
        self.shell = shell

    def login(self):
        """ Login to the Vagrant Cloud. """

        if not self.token:
            # No token was passed try to get one from the
            # .vagrantcloud file
            with open(os.path.join(os.path.expanduser('~'), '.vagrantcloud')) as json_file:
                auth = json.load(json_file)
                token = auth['token']
        else:
            token = self.token

        self.shell.run(cmd='vagrant login --token {}'.format(token))

    def logout(self):
        """ Logout from the Vagrant Cloud """

        self.shell.run(cmd='vagrant login --logout')

    def publish_box(self, box_tag, box_version, provider, box_file):
        """ Publishes a box on the vagrant cloud """

        self.shell.run(
            cmd='vagrant cloud publish {box_tag} {box_version}'
            ' {provider} {box_file} --release --force'.format(
                box_tag=box_tag, box_version=box_version,
                provider=provider, box_file=box_file))

    def __enter__(self):
        """Use cloud with the with statement."""
        self.login()
        return self

    def __exit__(self, type, value, traceback):
        """Use cloud with the with statement."""
        self.logout()