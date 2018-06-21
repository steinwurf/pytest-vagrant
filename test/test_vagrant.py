import os

def test_vagrantfile(vagrant):
    assert vagrant.vagrant_file() is not None

def test_version(vagrant):
    assert vagrant.version() is not None

def test_status(vagrant):
    status = vagrant.status
    assert str(status) == "running"
    assert status.running == True
    assert status.not_created == False
    assert status.poweroff == False
    assert status.aborted == False
    assert status.saved == False

def test_port(vagrant):
    assert len(vagrant.port()) != 0
    assert False
def test_ssh(vagrant):
    with vagrant.ssh() as ssh:
        out, _ = ssh.run('ls')
        assert "hello" not in out
        ssh.run('touch hello')
        out, _ = ssh.run('ls')
        assert "hello" in out
        ssh.run('rm hello')
        out, _ = ssh.run('ls')
        assert "hello" not in out

