import os

from pytest_vagrant import Vagrant


def test_vagrant_fixture(vagrant):
    # We don't do anything just check that the fixture is available
    pass


def test_vagrant_from_box(testdirectory):

    vagrant = Vagrant(project="pytest_vagrant",
                      machines_dir=testdirectory.path())

    vagrant.from_box(box="ubuntu/eoan64", name="pytest_vagrant")

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
