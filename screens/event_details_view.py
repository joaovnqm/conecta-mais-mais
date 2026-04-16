from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll
from services.events import check_event

EVENT_DETAILS_VIEW = """
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

.event_buttons{
    content-align: center middle;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EventDetailsView(Screen):
    CSS = EVENT_DETAILS_VIEW

    def __init__(self, event_id: int):
        super().__init__()
        self.event_id = event_id

    def compose(self) -> ComposeResult:
        event = check_event(self.event_id)
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Clique em algum evento abaixo para saber mais.", id="main_title")
                yield Button("Voltar", id="button_return", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "button_return":
            self.app.pop_screen()