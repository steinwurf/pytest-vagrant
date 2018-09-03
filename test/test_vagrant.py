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


def test_ssh(vagrant):
    with vagrant.ssh() as ssh:
        ssh.rm('hello', force=True)
        out, _ = ssh.run('ls')
        assert "hello" not in out
        ssh.run('touch hello')
        out, _ = ssh.run('ls')
        assert "hello" in out
        ssh.rm('hello')
        out, _ = ssh.run('ls')
        assert "hello" not in out
        ssh.rm('waf', force=True)
        ssh.put('../waf', 'waf')
        out, _ = ssh.run('python waf --version')
        assert "waf" in out
        ssh.rm('waf')

        ssh.rm('woop_file', force=True)
        ssh.run('echo woop >> woop_file')
        ssh.get('woop_file', 'woop_file')
        with open('woop_file', 'r') as f:
            woop_local = f.read()
            woop_remote, _ = ssh.run('cat woop_file')
            assert woop_local == woop_remote
