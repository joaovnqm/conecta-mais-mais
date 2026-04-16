from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll

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
    content-allign: center middle;
    color: 
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
        return super().compose()