import os
import jinja2


# Vagrant uses the Vagrantfile as configuration file. You can read more
# about it here:
# https://www.vagrantup.com/docs/vagrantfile/
VAGRANTFILE_TEMPLATE = r"""
Vagrant.configure("2") do |config|
  config.vm.box = "{{box}}"

  {% if box_version %}
  config.vm.box_version="{{box_version}}"
  {% endif %}

  # We use SSH not shared folders to talk with the VM
  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.provider "virtualbox" do |v|

    {% if 'ubuntu' in box %}
    # Log file was removed in newer version of ubuntu cloud images
    # so we have to disconnect the uart otherwise boot is very slow
    # https://bugs.launchpad.net/cloud-images/+bug/1829625
    v.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    {% endif %}
    v.name = "{{name}}"
  end
end
""".strip()


class Vagrantfile(object):
    """ Vagrantfile can write a vagrant file for a specific machine"""

    def write(self, box, box_version, name, cwd):
        """ Create a machine from the specified box.

        :param box: The Vagrant box to use as a string
        :param box_version: The version of the box to use
        :param name: The name chosen for this machine as a string.
        :param cwd: The working directory where the Vagrant file should be
            written
        """

        vagrantfile = os.path.join(cwd, 'Vagrantfile')

        template = jinja2.Template(VAGRANTFILE_TEMPLATE)

        variables = {
            'box': box,
            'box_version': box_version,
            'name': name
        }

        template.stream(**variables).dump(vagrantfile)
