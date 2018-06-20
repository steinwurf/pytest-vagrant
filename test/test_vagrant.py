import os

def test_version(vagrant):
    assert vagrant.version() is not None

def test_status(vagrant):
    status_output = """default not created (virtualbox)"""
    assert str(vagrant.status) == "running"
    assert vagrant.status.running == True
    assert vagrant.status.not_created == False
    assert vagrant.status.poweroff == False
    assert vagrant.status.aborted == False
    assert vagrant.status.saved == False

def test_port(vagrant):
    assert len(vagrant.port()) != 0

def test_ssh(vagrant):
    ssh = vagrant.ssh()
    with ssh:
        out, _ = ssh.run('ls')
        assert "hello" not in out
        ssh.run('touch hello')
        out, _ = ssh.run('ls')
        assert "hello" in out
        ssh.run('rm hello')
        out, _ = ssh.run('ls')
        assert "hello" not in out

