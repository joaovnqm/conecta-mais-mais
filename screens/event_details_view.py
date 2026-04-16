from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll
from services.events import check_event
from services.users import check_user_name

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
    align: center top;
}

#main_title {
    content-align: center middle;
    text-style: bold;
    color: black;
    border: solid white;
    padding: 1 2;
    margin: 1;
}

#button_return {
    width: 100%;
    content-align: center middle;
    margin: 1;
}
"""

class EventDetailsView(Screen):
    CSS = EVENT_DETAILS_VIEW

    def __init__(self, event_id: int):
        super().__init__()
        self.event_id = event_id

    def compose(self) -> ComposeResult:
        event = check_event(self.event_id)
        creator_name = check_user_name(event[5])
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Evento: {event[1]}.", id="main_title")
                if event[2] == None:
                    yield Static("O local do evento ainda não está disponível.")
                else:
                    yield Static(f"Local: {event[2]}.")
                
                if event[3] == None:
                    yield Static("A data do evento ainda não está disponível.")
                else: 
                    yield Static(f"Data: {event[3]}.")

                if event[4] == None:
                    yield Static("A hora do evento ainda não foi divulgada.")
                else:
                    yield Static(f"Hora: {event[4]}.")
                    
                yield Static(f"Criador do evento: {creator_name}.")
                yield Button("Voltar", id="button_return", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "button_return":
            self.app.pop_screen()