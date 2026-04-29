from dataclasses import dataclass, field
import os

KEY_MAP = {
    "Hostname": ("hostname", str),
    "User": ("user", str),
    "Port": ("port", int),
    "IdentityFile": ("identity_file", str),
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
    def load(self) -> list[SSHHost]:
        hosts = []
        current_host = None

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
                    key, value = line.split(" ", 1)
                    mapped_key = KEY_MAP.get(key)
                    if mapped_key:
                        field_name, field_type = mapped_key
                        setattr(current_host, field_name, field_type(value))
                    else:
                        current_host.extra[key] = value

        if current_host:
            hosts.append(current_host)

        return hosts

    def save(self, hosts: list[SSHHost]) -> None:
        pass
