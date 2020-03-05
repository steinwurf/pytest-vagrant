import os
import mock
import csv
import re

import pytest_vagrant


def test_vagrant_fixture(vagrant):
    # We don't do anything just check that the fixture is available
    pass


def test_vagrant_from_box(testdirectory):

    class FactoryMock(mock.Mock):
        def build(self, box, name):

            machine = mock.Mock()

            machine.box = box
            machine.name = name
            machine.slug = 'slug'
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

SNAPSHOT_LIST = r"""
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

    result = pytest_vagrant.vagrant.parse_snapshot_list(SNAPSHOT_NOT_CREATED)
    assert result == []

    result = pytest_vagrant.vagrant.parse_snapshot_list(SNAPSHOT_NONE)
    assert result == []

    result = pytest_vagrant.vagrant.parse_snapshot_list(SNAPSHOT_LIST)
    assert result == ['reset', 'reset2']

    result = pytest_vagrant.vagrant.parse_snapshot_list(SNAPSHOT_LIST_2_2_3)
    assert result == ['reset']


STATUS = r"""
1583408799,default,metadata,provider,virtualbox
1583408799,default,provider-name,virtualbox
1583408799,default,state,running
1583408799,default,state-human-short,running
1583408799,default,state-human-long,The VM is running. To stop this VM%!(VAGRANT_COMMA) you can run `vagrant halt` to\nshut it down forcefully%!(VAGRANT_COMMA) or you can run `vagrant suspend` to simply\nsuspend the virtual machine. In either case%!(VAGRANT_COMMA) to restart it again%!(VAGRANT_COMMA)\nsimply run `vagrant up`.
1583408799,,ui,info,Current machine states:\n\ndefault                   running (virtualbox)\n\nThe VM is running. To stop this VM%!(VAGRANT_COMMA) you can run `vagrant halt` to\nshut it down forcefully%!(VAGRANT_COMMA) or you can run `vagrant suspend` to simply\nsuspend the virtual machine. In either case%!(VAGRANT_COMMA) to restart it again%!(VAGRANT_COMMA)\nsimply run `vagrant up`.
""".strip()


def test_parse_status():
    result = pytest_vagrant.vagrant.parse_status(output=STATUS)
    assert result == "running"


def test_run(vagrant):
    machine = vagrant.from_box(
        box="hashicorp/bionic64", name="pytest_vagrant", reset=False)

    with machine.ssh() as ssh:
        cwd = ssh.getcwd()
        print(cwd)

        ssh.chdir('/tmp')
        cwd = ssh.getcwd()
        print(cwd)

        ssh.chdir('~')
        cwd = ssh.getcwd()
        print(cwd)

    assert 0

    #     ssh.put_file()
    #     ssh.get_file()
    #     ssh.run()
    #     ssh.chdir()
    #     ssh.rmdir()
    #     ssh.mkdir()
    #     ssh.contains_dir()
    #     ssh.contains_file()


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

    result = pytest_vagrant.vagrant.parse_ssh_config(output=OUTPUT_SSHCONFIG)

    assert result.hostname == '127.0.0.1'
    assert result.username == 'vagrant'
    assert result.port == 2222
    assert result.identityfile == '/home/mvp/.pytest_vagrant/private_key'

    # mo

    # vagrant = Vagrant(project="pytest_vagrant",
    #                   machines_dir=testdirectory.path())

    # vagrant.from_box(box="ubuntu/eoan64", name="pytest_vagrant")

    # def test_vagrantfile(vagrant):
    #     assert vagrant.vagrant_file() is not None

    # def test_version(vagrant):
    #     assert vagrant.version() is not None

    # def test_status(vagrant):
    #     status = vagrant.status
    #     assert str(status) == "running"
    #     assert status.running == True
    #     assert status.not_created == False
    #     assert status.poweroff == False
    #     assert status.aborted == False
    #     assert status.saved == False

    # def test_port(vagrant):
    #     assert len(vagrant.port()) != 0

    # def test_sshdirectory_path(sshdirectory):

    #     # All subdirectories are create in the ~/pytest_temp and the
    #     # subdirectories are named after the test-cast e.g. in this
    #     # case test_sshdirectory_path

    #     assert sshdirectory.getcwd() == '/home/vagrant/pytest_temp/test_sshdirectory_path'

    # def test_sshdirectory_put_file(testdirectory, sshdirectory):

    #     file_path = testdirectory.write_text(
    #         "test.txt", data=u"hello", encoding="utf-8")

    #     sshdirectory.put_file(local_file=file_path)
    #     assert sshdirectory.contains_file("test.txt")

    #     sshdirectory.put_file(local_file=file_path, rename_as="ok.txt")
    #     assert sshdirectory.contains_file("ok.txt")

    # def test_sshdirectory_get_file(testdirectory, sshdirectory):
    #     test_dir = sshdirectory.mkdir('testdir')
    #     test_dir.run('touch hello_world.txt')

    #     assert test_dir.contains_file("hello_world.txt")

    #     test_dir.get_file(remote_file="hello_world.txt",
    #                       local_directory=testdirectory.path())

    #     testdirectory.contains_file("hello_world.txt")

    # def test_sshdirectory_run(sshdirectory):
    #     test_dir = sshdirectory.mkdir('testdir')
    #     test_dir.run('touch hello_world.txt')

    #     assert test_dir.contains_file("hello_world.txt")

    #     res = test_dir.run('ls -la')
    #     res.match(stdout="*hello_world.txt*")

    # def test_sshdirectory_from_path(sshdirectory):
    #     tmp_dir = sshdirectory.from_path('/tmp')
    #     assert tmp_dir.getcwd() == '/tmp'

    # def test_sshdirectory_mkdir_rmdir(sshdirectory):
    #     test_dir = sshdirectory.mkdir('testdir')
    #     test_dir.run('touch hello')

    #     assert sshdirectory.contains_dir('testdir')

    #     sshdirectory.rmdir('testdir')

    #     assert not sshdirectory.contains_dir('testdir')

    # def test_sshdirectory_rmfile(sshdirectory):
    #     test_dir = sshdirectory.mkdir('testdir')
    #     test_dir.run('touch hello_world.txt')

    #     assert test_dir.contains_file("hello_world.txt")

    #     test_dir.rmfile("hello_world.txt")

    #     assert not test_dir.contains_file("hello_world.txt")
