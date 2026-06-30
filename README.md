![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Tests](https://github.com/geckoes/sshelf/actions/workflows/tests.yml/badge.svg)

# sshelf

A lightweight TUI to manage SSH config easily.

## Features

You can:

- **see** hosts configured in your ssh config
- **add** a new host (Host, HostName, User, port, IdentityFile)
- **modify** an existing host
- **delete** a host
- **look for** a host by its name

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/geckoes/sshelf.git
cd sshelf
uv sync
```

## Usage

```bash
uv run sshelf
```

### Keybindings

| Key | Action |
|-----|--------|
| `a` | Add a new host |
| `e` | Edit the selected host |
| `d` | Delete the selected host (asks for confirmation) |
| `/` | Search/filter by host, hostname or user |
| `s` | Save changes to `~/.ssh/config` |
| `q` | Quit (warns if there are unsaved changes) |

Each host's advanced SSH options (e.g. `ProxyJump`, `SetEnv`, `LocalForward`)
can be viewed and edited in the **Advanced Options** field of the add/edit form,
one `Keyword Value` per line.

Changes are kept in memory until you press `s`. On save, sshelf writes a backup
of your current config to `~/.ssh/config.bak` and sets the file permissions to `600`.

> **Note:** on save, sshelf rewrites `~/.ssh/config` from the hosts it manages.
> Global directives, comments and `Match` blocks are **not** preserved in the
> rewritten file — your original is always kept at `~/.ssh/config.bak`.

## Roadmap

- manage all kind of SSH host connection from TUI or CLI
- import/export hosts configurations
- cross-platform support (Linux, macOS, Windows)

## Contributing

See CONTRIBUTING.md file.

## License

MIT
