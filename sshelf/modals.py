from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, TextArea
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll

from sshelf.parser import SSHHost

class HostFormScreen(ModalScreen):
    CSS = """
    HostFormScreen { align: center middle; }
    #dialog {
        width: 60; height: auto; max-height: 90%;
        padding: 1 2; background: $surface; border: thick $primary;
    }
    #fields { height: 1fr; }
    #dialog Input { margin-bottom: 1; }
    #buttons { height: auto; align: right middle; }
    #buttons Button { margin-left: 2; }
    #extra { height: 6;}
    """

    def __init__(self, existing_aliases=None, host=None, form_title="Add Host:"):
        super().__init__()
        self.existing_aliases = set(existing_aliases or [])
        self.host = host
        self.form_title = form_title

    def compose(self):
        with Vertical(id="dialog"):
            yield Label(self.form_title)
            with VerticalScroll(id="fields"):
                yield Input(placeholder="Host (alias)", id="host")
                yield Input(placeholder="Hostname", id="hostname")
                yield Input(placeholder="User", id="user")
                yield Input(placeholder="Port", id="port")
                yield Input(placeholder="Identity File", id="identity_file")
                yield Label("Advanced Options: (one 'Keyword Value' per line):")
                yield TextArea(placeholder="Extra Options", id="extra")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        alias = self.query_one("#host", Input).value.strip()
        if not alias:
            self.notify("Host alias is required.", severity="error")
            return
        if alias in self.existing_aliases:
            self.notify(f"Host '{alias}' already exists.", severity="error")
            return
        port_raw = self.query_one("#port", Input).value.strip()
        if port_raw and not port_raw.isdigit():
            self.notify("Port must be a number.", severity="error")
            return
        MODELED = {"host", "hostname", "user", "port", "identityfile"}
        for raw in self.query_one("#extra", TextArea).text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                self.notify(f"Advanced option '{line}' needs a value.", severity="error")
                return
            if parts[0].lower() in MODELED:
                self.notify(f"Use the dedicated field for '{parts[0]}'.", severity="error")
                return
        self.dismiss(self._build_host())

    def _build_host(self) -> SSHHost:
        port_raw = self.query_one("#port", Input).value.strip()
        return SSHHost(
            host=self.query_one("#host", Input).value.strip(),
            hostname=self.query_one("#hostname", Input).value.strip(),
            user=self.query_one("#user", Input).value.strip(),
            port=int(port_raw) if port_raw else 22,
            identity_file=self.query_one("#identity_file", Input).value.strip(),
            extra=self._parse_extra_options(self.query_one("#extra", TextArea).text)
        )

    def _parse_extra_options(self, text: str) -> dict:
        extra = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " " not in line:
                continue
            key, value = line.split(None, 1)
            extra[key] = value
        return extra
    
    def on_mount(self) -> None:
        if self.host is not None:
            self.query_one("#host", Input).value = self.host.host
            self.query_one("#hostname", Input).value = self.host.hostname
            self.query_one("#user", Input).value = self.host.user
            self.query_one("#port", Input).value = str(self.host.port)
            self.query_one("#identity_file", Input).value = self.host.identity_file
            extra_text = "\n".join(f"{k} {v}" for k, v in self.host.extra.items())
            self.query_one("#extra", TextArea).text = extra_text
        self.query_one("#host", Input).focus()

class ConfirmScreen(ModalScreen):
    CSS = """
    ConfirmScreen { align: center middle; }
    #confirm-dialog {
        width: 50; height: auto; padding: 1 2;
        background: $surface; border: thick $error;
    }
    #confirm-buttons { height: auto; align: right middle; }
    #confirm-buttons Button { margin-left: 2; }
    """

    def __init__(self, message, confirm_label="Delete"):
        super().__init__()
        self.message = message
        self.confirm_label = confirm_label

    def compose(self):
        with Vertical(id="confirm-dialog"):
            yield Label(self.message)
            with Horizontal(id="confirm-buttons"):
                yield Button(self.confirm_label, variant="error", id="confirm")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")
