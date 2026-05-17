from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll
from database.repositories.event_repository import event_services

MY_EVENT_DETAILS_VIEW = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 86;
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

class MyEventDetailsView(Screen):
    """
    Classe responsável pela tela de detalhes do evento criado pelo usuário. Ela exibe as informações do evento selecionado, como nome, descrição, local, 
    data, hora e opções para editar ou excluir o evento.
    """
    CSS = MY_EVENT_DETAILS_VIEW

    # Inicializa a tela com o evento que será exibido
    def __init__(self, user_id: int, event_id: int):
        super().__init__()
        self.user_id = user_id
        self.event_id = event_id

    # Monta a interface com as informações do evento e do criador
    def compose(self) -> ComposeResult:
        event = event_services.check_event(self.event_id)
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Evento: {event.name}", id="main_title")
                yield Static(f"Descrição: {event.description}")
                if event.event_location == None:
                    yield Static("O local do evento ainda não está disponível")

                else:
                    yield Static(f"Local: {event.event_location}.")
                
                if event.date == None:
                    yield Static("A data do evento ainda não está disponível")

                else: 
                    yield Static(f"Data: {event.date}.")

                if event.hour == None:
                    yield Static("A hora do evento ainda não foi divulgada")
                    
                else:
                    yield Static(f"Hora: {event.hour}")

                yield Button("Editar Evento", id="button_edit_event")
                yield Button("Excluir Evento", id="button_delete_event", variant="error")
                yield Button("Voltar", id="button_return", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_edit_event":
            # Lógica para editar o evento (a ser implementada)
            pass
        
        elif event.button.id == "button_delete_event":
            # Lógica para excluir o evento (a ser implementada)
            pass

        elif event.button.id == "button_return":
            self.app.pop_screen()