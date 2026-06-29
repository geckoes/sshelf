from dataclasses import dataclass, field
import os

KEY_MAP = {
    "hostname": ("hostname", str),
    "user": ("user", str),
    "port": ("port", int),
    "identityfile": ("identity_file", str),
}


@dataclass
class SSHHost:
    host: str
    hostname: str = ""
    user: str = ""
    port: int = 22
    identity_file: str = ""
    extra: dict = field(default_factory=dict)


class SSHConfig:
    def load(self, config_path: str = None) -> list[SSHHost]:
        hosts = []
        current_host = None

        if config_path is None:
            config_path = os.path.expanduser("~/.ssh/config")
        if not os.path.exists(config_path):
            return hosts
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("Host "):
                    if current_host:
                        hosts.append(current_host)
                    current_host = SSHHost(host=line[5:])
                else:
                    if current_host is None:
                        continue
                    key, value = line.split(" ", 1)
                    mapped_key = KEY_MAP.get(key.lower())
                    if mapped_key:
                        field_name, field_type = mapped_key
                        setattr(current_host, field_name, field_type(value))
                    else:
                        current_host.extra[key] = value

        if current_host:
            hosts.append(current_host)

        return hosts

    def save(self, hosts: list[SSHHost], config_path: str = None) -> None:
        if config_path is None:
            config_path = os.path.expanduser("~/.ssh/config")
        temp_config_path = str(config_path) + ".tmp"
        with open(temp_config_path, "w") as f:
            for host in hosts:
                f.write(f"Host {host.host}\n")
                if host.hostname:
                    f.write(f"    Hostname {host.hostname}\n")
                if host.user:
                    f.write(f"    User {host.user}\n")
                if host.port != 22:
                    f.write(f"    Port {host.port}\n")
                if host.identity_file:
                    f.write(f"    IdentityFile {host.identity_file}\n")
                for key, value in host.extra.items():
                    f.write(f"    {key} {value}\n")
                f.write("\n")
        os.replace(temp_config_path, config_path)
    
def find_host(hosts: list[SSHHost], name: str) -> SSHHost | None:
    for host in hosts:
        if host.host == name:
            return host
    return None

def add_host(hosts: list[SSHHost], new_host: SSHHost) -> None:
    existing_host = find_host(hosts, new_host.host)
    if existing_host:
        raise ValueError(f"Host '{new_host.host}' already exists.")
    hosts.append(new_host)

def update_host(hosts: list[SSHHost], name: str, **fields) -> None:
    host = find_host(hosts, name)
    if not host:
        raise ValueError(f"Host '{name}' not found.")
    for key, value in fields.items():
        if hasattr(host, key):
            setattr(host, key, value)
        else:
            host.extra[key] = value

def delete_host(hosts: list[SSHHost], name: str) -> None:
    host = find_host(hosts, name)
    if not host:
        raise ValueError(f"Host '{name}' not found.")
    hosts.remove(host)
