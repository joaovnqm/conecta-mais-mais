from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll

MAIN_PAGE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 60;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EventsView(Screen):
    CSS = MAIN_PAGE_CSS

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_name = user_name
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Eventos", id="main_title")
                yield Button("Voltar", id="button_return", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_return":
            self.app.pop_screen()