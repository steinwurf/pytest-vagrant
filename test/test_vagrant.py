import os
import mock
import pytest

import pytest_vagrant


def test_vagrant_fixture(vagrant):
    # We don't do anything just check that the fixture is available
    pass


def _test_vagrant_from_box(testdirectory):
    class FactoryMock(mock.Mock):
        def build(self, box, name):

            machine = mock.Mock()

            machine.box = box
            machine.name = name
            machine.slug = "slug"
            machine.cwd = os.path.join(testdirectory.path(), name)

            machine.status.not_created = True
            machine.status.poweroff = False

            machine.snapshot_list.return_value = []

            return machine

    machine_factory = FactoryMock()

    vagrant = pytest_vagrant.Vagrant(machine_factory=machine_factory)

    machine = vagrant.from_box(box="ubuntu/eoan64", name="pytest_vagrant")

    print(str(machine.mock_calls))


SNAPSHOT_NOT_CREATED = r"""
1583404006,default,metadata,provider,virtualbox
1583404006,default,ui,info,==> default: VM not created. Moving on...
""".strip()

SNAPSHOT_NONE = r"""
1583406501,default,metadata,provider,virtualbox
1583406503,default,ui,output,==> default: No snapshots have been taken yet!
1583406503,default,ui,detail,    default: You can take a snapshot using `vagrant snapshot save`. Note that\n    default: not all providers support this yet. Once a snapshot is taken%!(VAGRANT_COMMA) you\n    default: can list them using this command%!(VAGRANT_COMMA) and use commands such as\n    default: `vagrant snapshot restore` to go back to a certain snapshot.
""".strip()

# Output from Vagrant 2.2.7
SNAPSHOT_LIST_2_2_7 = r"""
1583406926,default,metadata,provider,virtualbox
1583406926,default,ui,output,==> default:
1583406926,default,ui,detail,reset
1583406926,default,ui,detail,reset2
""".strip()

# Output from Vagrant 2.2.3
SNAPSHOT_LIST_2_2_3 = r"""
1583439756,default,metadata,provider,virtualbox
1583439756,default,ui,output,reset
""".strip()


def test_machine_snapshot_list():

    result = pytest_vagrant.parse.to_snapshot_list(SNAPSHOT_NOT_CREATED)
    assert result == []

    result = pytest_vagrant.parse.to_snapshot_list(SNAPSHOT_NONE)
    assert result == []

    result = pytest_vagrant.parse.to_snapshot_list(SNAPSHOT_LIST_2_2_7)
    assert result == ["reset", "reset2"]

    result = pytest_vagrant.parse.to_snapshot_list(SNAPSHOT_LIST_2_2_3)
    assert result == ["reset"]


STATUS = r"""
1583408799,default,metadata,provider,virtualbox
1583408799,default,provider-name,virtualbox
1583408799,default,state,running
1583408799,default,state-human-short,running
1583408799,default,state-human-long,The VM is running. To stop this VM%!(VAGRANT_COMMA) you can run `vagrant halt` to\nshut it down forcefully%!(VAGRANT_COMMA) or you can run `vagrant suspend` to simply\nsuspend the virtual machine. In either case%!(VAGRANT_COMMA) to restart it again%!(VAGRANT_COMMA)\nsimply run `vagrant up`.
1583408799,,ui,info,Current machine states:\n\ndefault                   running (virtualbox)\n\nThe VM is running. To stop this VM%!(VAGRANT_COMMA) you can run `vagrant halt` to\nshut it down forcefully%!(VAGRANT_COMMA) or you can run `vagrant suspend` to simply\nsuspend the virtual machine. In either case%!(VAGRANT_COMMA) to restart it again%!(VAGRANT_COMMA)\nsimply run `vagrant up`.
""".strip()


def test_parse_status():
    result = pytest_vagrant.parse.to_status(output=STATUS)
    assert result.status == "running"


def test_run(vagrant, testdirectory):
    machine = vagrant.from_box(
        box="hashicorp/bionic64", name="pytest_vagrant", reset=False
    )

    with machine.ssh() as ssh:
        cwd = ssh.getcwd()
        assert cwd == "/home/vagrant"

        ssh.chdir("/home")
        cwd = ssh.getcwd()
        assert cwd == "/home"

        ssh.chdir("vagrant")
        cwd = ssh.getcwd()
        assert cwd == "/home/vagrant"

        ssh.chdir("~")
        cwd = ssh.getcwd()
        assert cwd == "/home/vagrant"

        assert ssh.is_dir("/home/vagrant") == True
        assert ssh.is_dir("/home") == True
        assert ssh.is_dir("~") == False
        assert ssh.is_dir("/blabal/vagrant") == False

        ssh.chdir("/home")
        assert ssh.is_dir("vagrant") == True
        ssh.chdir("~")

        assert ssh.is_file("/home/vagrant/.profile") == True
        assert ssh.is_file(".profile") == True
        assert ssh.is_file("blabal") == False

        file_path = testdirectory.write_text(
            "test.txt", data=u"hello", encoding="utf-8"
        )

        ssh.put_file(local_file=file_path)
        assert ssh.is_file("test.txt") == True

        ssh.run('echo " vagrant" >> test.txt')

        ssh.get_file("test.txt", testdirectory.path(), rename_as="back.txt")
        assert testdirectory.contains_file("back.txt")

        ssh.unlink("test.txt")
        assert ssh.is_file("test.txt") == False


def test_run_fail(vagrant):
    machine = vagrant.from_box(
        box="hashicorp/bionic64", name="pytest_vagrant", reset=False
    )

    with machine.ssh() as ssh:
        with pytest.raises(pytest_vagrant.RunResultError):
            ssh.run("some_nonexisting_cmd")


UBUNTU_TWEAK = """
v.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
""".strip()


def test_run_ubuntu(vagrant):
    machine = vagrant.from_box(box="ubuntu/eoan64", name="pytest_vagrant", reset=False)

    vagrantfile = os.path.join(machine.cwd, "Vagrantfile")

    # Check that we our Ubuntu Vagrantfile template
    with open(vagrantfile) as f:
        assert UBUNTU_TWEAK in f.read()


OUTPUT_SSHCONFIG = r"""
Host default
  HostName 127.0.0.1
  User vagrant
  Port 2222
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  PasswordAuthentication no
  IdentityFile /home/mvp/.pytest_vagrant/private_key
  IdentitiesOnly yes
  LogLevel FATAL
""".strip()


def test_parse_ssh_config():

    result = pytest_vagrant.parse.to_ssh_config(output=OUTPUT_SSHCONFIG)

    assert result.hostname == "127.0.0.1"
    assert result.username == "vagrant"
    assert result.port == 2222
    assert result.identityfile == "/home/mvp/.pytest_vagrant/private_key"


VERSION_SPECIFICATION = """
config.vm.box_version = 
""".strip()


def test_box_version(vagrant):
    unversioned_machine = vagrant.from_box(
        box="debian/buster64",
        name="pytest_vagrant",
        reset=False,
    )

    unversioned_vagrantfile = os.path.join(unversioned_machine.cwd, "Vagrantfile")

    # Check that version is not in Vagrantfile template
    with open(unversioned_vagrantfile) as f:
        assert VERSION_SPECIFICATION not in f.read()

    versioned_machine = vagrant.from_box(
        box="debian/buster64",
        name="pytest_vagrant",
        box_version="10.20210409.1",
        reset=False,
    )

    versioned_vagrantfile = os.path.join(versioned_machine.cwd, "Vagrantfile")

    # Check that version is in Vagrantfile template
    with open(versioned_vagrantfile) as f:
        assert VERSION_SPECIFICATION in f.read()
