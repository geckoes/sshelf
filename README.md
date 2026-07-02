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

Changes are kept in memory until you press `s`. The first time sshelf saves, it
copies your original config to `~/.ssh/config.bak` (once — later saves never
overwrite it, so the pristine original is always kept) and sets the file
permissions to `600`.

## Known limitations

On save, sshelf **rewrites** `~/.ssh/config` from scratch using only the hosts it
models. Anything outside that model is therefore **dropped from the rewritten file**:

- comments (`# ...`)
- global directives placed before the first `Host` block (e.g. `ServerAliveInterval`)
- `Match` blocks
- original ordering, blank lines and formatting

Your original file is copied to `~/.ssh/config.bak` on the first save and never
overwritten afterwards, so the pristine original is always recoverable — but if
you hand-curate your config (comments, `Match` rules, global options), be aware
that the active file will be flattened after a save.

Preserving these parts in the active file is planned for a future release.

## Roadmap

- named, on-demand backups (choose the file, confirm overwrite)
- preserve comments, global directives and `Match` blocks when saving
- manage all kind of SSH host connection from TUI or CLI
- import/export hosts configurations
- cross-platform support (Linux, macOS, Windows)

## Contributing

See CONTRIBUTING.md file.

## License

MIT
