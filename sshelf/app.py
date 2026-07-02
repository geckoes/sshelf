from functools import partial

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Input

from sshelf.modals import ConfirmScreen, HostFormScreen
from sshelf.parser import SSHConfig, SSHHost, add_host, find_host, update_host, delete_host

class SShelfApp(App):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("a", "add_host", "Add Host"),
        ("e", "edit_host", "Edit Host"),
        ("d", "delete_host", "Delete Host"),
        ("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search hosts...", id="search")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.hosts = SSHConfig().load()
        self.query_one(DataTable).add_columns("Host", "Hostname", "User", "Port", "IdentityFile")
        self.populate_table(self.hosts)
        self.query_one(DataTable).focus()
        self.modified = False
    
    def populate_table(self, hosts: list):
        table = self.query_one(DataTable)
        table.clear()
        for host in hosts:
            table.add_row(
                host.host,
                host.hostname or "",
                host.user or "",
                str(host.port) if host.port != 22 else "",
                host.identity_file or ""
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search":
            return
        search_term = event.value.strip().lower()
        if not search_term:
            self.populate_table(self.hosts)
            return
        filtered_hosts = [
            host for host in self.hosts
            if search_term in host.host.lower() or
               search_term in host.hostname.lower() or
               search_term in host.user.lower()
        ]
        self.populate_table(filtered_hosts)
    
    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()
    
    def action_add_host(self) -> None:
        existing = [host.host for host in self.hosts]
        self.push_screen(
            HostFormScreen(existing_aliases=existing, form_title="Add Host:"),
            self.on_host_added,
        )

    def on_host_added(self, new_host: SSHHost) -> None:
        if new_host is None:
            return
        try:
            add_host(self.hosts, new_host)
        except ValueError as e:
            self.notify(str(e), severity="error")
            return
        self.populate_table(self.hosts)
        self._set_modified(True)

    def _selected_alias(self) -> str | None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return None
        return table.get_row_at(table.cursor_row)[0]

    def action_edit_host(self) -> None:
        alias = self._selected_alias()
        if alias is None:
            return
        host = find_host(self.hosts, alias)
        others = [h.host for h in self.hosts if h.host != alias]
        self.push_screen(
            HostFormScreen(existing_aliases=others, host=host, form_title="Edit Host:"),
            partial(self.on_host_edited, alias)
        )

    def on_host_edited(self, original_alias: str, updated_host: SSHHost) -> None:
        if updated_host is None:
            return
        update_host(
            self.hosts,
            original_alias,
            host=updated_host.host,
            hostname=updated_host.hostname,
            user=updated_host.user,
            port=updated_host.port,
            identity_file=updated_host.identity_file,
            extra=updated_host.extra
        )
        self.populate_table(self.hosts)
        self._set_modified(True)

    def action_delete_host(self) -> None:
        alias = self._selected_alias()
        if alias is None:
            return
        self.push_screen(
            ConfirmScreen(f"Are you sure you want to delete '{alias}'?"),
            partial(self.on_delete_confirmed, alias)
        )

    def on_delete_confirmed(self, alias: str, confirmed: bool) -> None:
        if not confirmed:
            return
        delete_host(self.hosts, alias)
        self.populate_table(self.hosts)
        self._set_modified(True)

    def action_save(self) -> None:
        try:
            SSHConfig().save(self.hosts)
            self._set_modified(False)
            self.notify("Configuration saved.", severity="info")
        except OSError as e:
            self.notify(f"Error saving configuration: {e}", severity="error")

    def _set_modified(self, value: bool) -> None:
        self.modified = value
        self.sub_title = "Unsaved Changes" if value else ""

    def action_request_quit(self) -> None:
        if self.modified:
            self.push_screen(
                ConfirmScreen("Unsaved changes. Quit without saving?", confirm_label="Quit"),
                self._on_quit_confirmed
            )
        else:
            self.exit()

    def _on_quit_confirmed(self, confirmed: bool) -> None:
        if confirmed:
            self.exit()


def main():
    SShelfApp().run()


if __name__ == "__main__":
    main()