from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll
from services.events import check_event
from services.users import check_user_name
from services.favorite_events import check_favorite_event, favorite_event

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
# Tela que exibe os detalhes completos de um evento selecionado
class EventDetailsView(Screen):
    CSS = EVENT_DETAILS_VIEW

    # Inicializa a tela com o evento que será exibido
    def __init__(self, user_id: int, event_id: int):
        super().__init__()
        self.user_id = user_id
        self.event_id = event_id

    # Monta a interface com as informações do evento e do criador
    def compose(self) -> ComposeResult:
        event = check_event(self.event_id)
        creator_name = check_user_name(event[6])
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Evento: {event[1]}", id="main_title")
                yield Static(f"Descrição: {event[2]}")
                if event[3] == None:
                    yield Static("O local do evento ainda não está disponível")
                else:
                    yield Static(f"Local: {event[3]}.")
                
                if event[4] == None:
                    yield Static("A data do evento ainda não está disponível")
                else: 
                    yield Static(f"Data: {event[4]}.")

                if event[5] == None:
                    yield Static("A hora do evento ainda não foi divulgada")
                else:
                    yield Static(f"Hora: {event[5]}")

                yield Static(f"Criador do evento: {creator_name}")
                if check_favorite_event(self.user_id, self.event_id):
                    yield Button("Desfavoritar o Evento", id="button_favorite_event", variant="error")

                else:
                    yield Button("Favoritar o evento", id="button_favorite_event", variant="success")
                    
                yield Button("Voltar", id="button_return", variant="error")
    
    # Retorna para a tela anterior
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "button_return":
            self.app.pop_screen()