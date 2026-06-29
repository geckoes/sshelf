from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Input

from sshelf.parser import SSHConfig

class SShelfApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
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
    

if __name__ == "__main__":
    app = SShelfApp()
    app.run()