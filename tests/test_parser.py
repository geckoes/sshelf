import pytest

from sshelf.parser import (
    SSHConfig,
    SSHHost,
    add_host,
    delete_host,
    find_host,
    update_host,
)


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


def test_load_with_global_options_before_first_host(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("""
ServerAliveInterval 15
Host server1
	Hostname server1.example.com
	User user1
	ForwardAgent yes
""")
    ssh_config = SSHConfig().load(config_path=config_file)
    assert len(ssh_config) == 1
    host = ssh_config[0]
    assert host.host == "server1"
    assert host.hostname == "server1.example.com"
    assert host.user == "user1"
    # global option before the first Host is skipped (no host to attach to)...
    assert "ServerAliveInterval" not in host.extra
    # ...while a non-mapped option inside the host still lands in extra
    assert host.extra == {"ForwardAgent": "yes"}


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


def test_save_creates_backup_of_existing_file(tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("ServerAliveInterval 15\nHost old\n\tUser olduser\n")

    SSHConfig().save([SSHHost(host="new", user="newuser")], config_path=config_file)

    backup = tmp_path / "config.bak"
    assert backup.exists()
    # the backup keeps the ORIGINAL content, including the global directive
    # that the regeneration drops
    backup_text = backup.read_text()
    assert "ServerAliveInterval 15" in backup_text
    assert "Host old" in backup_text
    # the active file is the regenerated one
    active_text = config_file.read_text()
    assert "Host new" in active_text
    assert "ServerAliveInterval" not in active_text


def test_save_no_backup_when_file_absent(tmp_path):
    config_file = tmp_path / "config"  # does not exist yet
    SSHConfig().save([SSHHost(host="new")], config_path=config_file)
    assert not (tmp_path / "config.bak").exists()
    assert config_file.exists()


# find_host


def test_find_host_found():
    hosts = [SSHHost(host="server1"), SSHHost(host="server2")]
    found = find_host(hosts, "server2")
    assert found is hosts[1]


def test_find_host_not_found():
    hosts = [SSHHost(host="server1")]
    assert find_host(hosts, "missing") is None


# add_host


def test_add_host():
    hosts = [SSHHost(host="server1")]
    add_host(hosts, SSHHost(host="server2", hostname="server2.example.com"))
    assert len(hosts) == 2
    assert hosts[1].host == "server2"
    assert hosts[1].hostname == "server2.example.com"


def test_add_host_duplicate_raises():
    hosts = [SSHHost(host="server1")]
    with pytest.raises(ValueError):
        add_host(hosts, SSHHost(host="server1"))
    assert len(hosts) == 1


# update_host


def test_update_host():
    hosts = [SSHHost(host="server1", user="user1", port=22)]
    update_host(hosts, "server1", user="root", port=2222)
    assert hosts[0].user == "root"
    assert hosts[0].port == 2222


def test_update_host_not_found_raises():
    hosts = [SSHHost(host="server1")]
    with pytest.raises(ValueError):
        update_host(hosts, "missing", user="root")


def test_update_host_unknown_field_goes_to_extra():
    hosts = [SSHHost(host="server1")]
    update_host(hosts, "server1", ForwardAgent="yes")
    assert hosts[0].extra == {"ForwardAgent": "yes"}


# delete_host


def test_delete_host():
    hosts = [SSHHost(host="server1"), SSHHost(host="server2")]
    delete_host(hosts, "server1")
    assert len(hosts) == 1
    assert hosts[0].host == "server2"


def test_delete_host_not_found_raises():
    hosts = [SSHHost(host="server1")]
    with pytest.raises(ValueError):
        delete_host(hosts, "missing")
    assert len(hosts) == 1


# round-trip: CRUD then persist


def test_add_then_save_and_load(tmp_path):
    config_file = tmp_path / "config"
    hosts = [SSHHost(host="server1", hostname="server1.example.com")]
    add_host(hosts, SSHHost(host="server2", hostname="server2.example.com"))
    SSHConfig().save(hosts, config_path=config_file)

    loaded_hosts = SSHConfig().load(config_path=config_file)
    assert find_host(loaded_hosts, "server2") is not None
    assert len(loaded_hosts) == 2
