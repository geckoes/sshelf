from sshelf.parser import SSHConfig, SSHHost


def test_load_emptyfile(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("")
    ssh_config = SSHConfig().load(config_path=config_file)
    assert ssh_config == []


def test_load_single_host(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("""
Host myserver
	Hostname myserver.example.com
	User myuser
	Port 2222
	IdentityFile ~/.ssh/id_rsa
""")
    ssh_config = SSHConfig().load(config_path=config_file)
    assert len(ssh_config) == 1
    host = ssh_config[0]
    assert host.host == "myserver"
    assert host.hostname == "myserver.example.com"
    assert host.user == "myuser"
    assert host.port == 2222
    assert host.identity_file == "~/.ssh/id_rsa"


def test_load_multiple_hosts(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("""
Host server1
	Hostname server1.example.com
	User user1
	Port 2222
	IdentityFile ~/.ssh/id_rsa
Host server2
	Hostname server2.example.com
	User user2
	Port 2200
	IdentityFile ~/.ssh/id_ed25519
""")
    ssh_config = SSHConfig().load(config_path=config_file)
    assert len(ssh_config) == 2
    host1 = ssh_config[0]
    assert host1.host == "server1"
    assert host1.hostname == "server1.example.com"
    assert host1.user == "user1"
    assert host1.port == 2222
    assert host1.identity_file == "~/.ssh/id_rsa"
    host2 = ssh_config[1]
    assert host2.host == "server2"
    assert host2.hostname == "server2.example.com"
    assert host2.user == "user2"
    assert host2.port == 2200
    assert host2.identity_file == "~/.ssh/id_ed25519"


def test_load_nonexistent_file(tmp_path):
    config_file = tmp_path / "nonexistent_config"
    ssh_config = SSHConfig().load(config_path=config_file)
    assert ssh_config == []


def test_load_with_comments(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("""
# This is a comment
Host server1
	Hostname server1.example.com
	User user1
	Port 2222
	IdentityFile ~/.ssh/id_rsa
# Another comment
Host server2
	Hostname server2.example.com
	User user2
	Port 2200
	IdentityFile ~/.ssh/id_ed25519
""")
    ssh_config = SSHConfig().load(config_path=config_file)
    assert len(ssh_config) == 2
    host1 = ssh_config[0]
    assert host1.host == "server1"
    assert host1.hostname == "server1.example.com"
    assert host1.user == "user1"
    assert host1.port == 2222
    assert host1.identity_file == "~/.ssh/id_rsa"
    host2 = ssh_config[1]
    assert host2.host == "server2"
    assert host2.hostname == "server2.example.com"
    assert host2.user == "user2"
    assert host2.port == 2200
    assert host2.identity_file == "~/.ssh/id_ed25519"


def test_save_and_load(tmp_path):
    config_file = tmp_path / "config"
    hosts = [
        SSHHost(
            host="server1",
            hostname="server1.example.com",
            user="user1",
            port=2222,
            identity_file="~/.ssh/id_rsa",
        ),
        SSHHost(
            host="server2",
            hostname="server2.example.com",
            user="user2",
            port=2200,
            identity_file="~/.ssh/id_ed25519",
        ),
    ]
    SSHConfig().save(hosts, config_path=config_file)
    loaded_hosts = SSHConfig().load(config_path=config_file)
    assert len(loaded_hosts) == 2

    assert loaded_hosts[0].host == "server1"
    assert loaded_hosts[0].hostname == "server1.example.com"
    assert loaded_hosts[0].user == "user1"
    assert loaded_hosts[0].port == 2222
    assert loaded_hosts[0].identity_file == "~/.ssh/id_rsa"

    assert loaded_hosts[1].host == "server2"
    assert loaded_hosts[1].hostname == "server2.example.com"
    assert loaded_hosts[1].user == "user2"
    assert loaded_hosts[1].port == 2200
    assert loaded_hosts[1].identity_file == "~/.ssh/id_ed25519"
