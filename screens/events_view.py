from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Select
from textual.containers import Center, VerticalScroll
from services.events import check_events_with_interests
from services.interests import check_interests_name
from screens.event_details_view import EventDetailsView

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

.event_buttons{
    content-align: center middle;
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
        events = check_events_with_interests(self.user_id)
        interests = check_interests_name(self.user_id)
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Filtrar por interesse:")
                yield Select((interest, interest) for interest in interests)
                yield Static("Clique em algum evento abaixo para saber mais.", id="main_title")
                if events:
                    for event in events:
                        yield Button(event[1], id=f"event_{event[0]}", classes="event_buttons")

                else:
                    yield Static("Nenhum evento encontrado.", classes="main_subtitle")

                yield Button("Voltar", id="button_return", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("event_buttons"):
            button_id = event.button.id
            numero_do_evento = str(button_id.split("_")[1])
            self.app.push_screen(EventDetailsView(numero_do_evento))

        elif event.button.id == "button_return":
            self.app.pop_screen()