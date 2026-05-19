from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, VerticalScroll
from database.repositories.event_repository import event_services

EDIT_SOCIAL_EVENT_PAGE_CSS = """
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
}

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

#search_event {
    width: 1fr;
    margin-bottom: 1;
}

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

Input {
    width: 100%;
    margin-top: 1;
}

Input.invalid {
    border: tall $error;
}

#message {
    height: 2;
    margin-top: 1;
    color: $warning;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EditSocialEventView(Screen):
    """
    Classe responsável pela tela de edição do evento criado pelo usuário. Ela exibe as informações do evento selecionado nos inputs
    para que o usuário possa editá-las e opções para salvar as alterações.
    """
    CSS = EDIT_SOCIAL_EVENT_PAGE_CSS

    # Inicializa a tela com o evento que será exibido
    def __init__(self, event_id: int):
        super().__init__()
        self.event_id = event_id

    # Monta a interface com as informações do evento e do criador
    def compose(self) -> ComposeResult:
        event = event_services.check_event(self.event_id)
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Editar Evento: {event.name}", id="main_title")
                yield Input(value=event.name, placeholder="Nome do evento", id="input_event_name")
                yield Input(value=event.description, placeholder="Descrição do evento", id="input_event_description")
                if event.event_location == None:
                    yield Input(placeholder="Local do evento", id="input_event_location")

                else:
                    yield Input(value=event.event_location, placeholder="Local do evento", id="input_event_location")
                
                if event.date == None:
                    yield Input(placeholder="Data do evento (DD-MM-AAAA)", id="input_event_date")
                
                else:
                    yield Input(value=event.date, placeholder="Data do evento (DD-MM-AAAA)", id="input_event_date")
                
                if event.hour == None:
                    yield Input(placeholder="Hora do evento (HH:MM)", id="input_event_hour")
                
                else:
                    yield Input(value=event.hour, placeholder="Hora do evento (HH:MM)", id="input_event_hour")

                yield Label("", id="message")
                yield Button("Salvar Alterações", id="button_save_changes")
                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Label)
        if event.button.id == "button_save_changes":
            input_event_name = self.query_one("#input_event_name", Input)
            input_event_description = self.query_one("#input_event_description", Input)
            input_event_location = self.query_one("#input_event_location", Input)
            input_event_date = self.query_one("#input_event_date", Input)
            input_event_hour = self.query_one("#input_event_hour", Input)

            name = input_event_name.value.strip()
            description = input_event_description.value.strip()
            event_location = input_event_location.value.strip()
            date = input_event_date.value.strip()
            hour = input_event_hour.value.strip()

            success, message = event_services.edit_event(self.event_id, name, description, event_location, date, hour)

            if success:
                self.app.pop_screen()
                self.app.notify(message)
            
            else:
                response.update(message)
        
        elif event.button.id == "button_return":
            self.app.pop_screen()