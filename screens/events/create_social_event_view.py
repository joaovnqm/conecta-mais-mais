from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Button, Input
from textual.containers import Center, VerticalScroll
from database.repositories.event_repository import event_services

CREATE_SOCIAL_EVENT_PAGE_CSS = """
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

class CreateSocialEventView(Screen):
    """
    Classe responsável pela criação de eventos sociais. Ela exibe um formulário para o usuário preencher os dados do evento, e um botão para criar o evento.
    """
    CSS = CREATE_SOCIAL_EVENT_PAGE_CSS

    # Inicializa a tela com os dados básicos do usuário autenticado
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com filtros por interesse e listagem de eventos
    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Criar Evento Social", id="main_title")
                yield Static("Preencha as informações do evento abaixo.")
                yield Input(placeholder="Insira o nome do evento...", id="event_name")
                yield Input(placeholder="Insira a descrição do evento...", id="event_description")
                yield Input(placeholder="Insira o local do evento (opcional)...", id="event_location")
                yield Input(placeholder="Insira a data do evento (opcional, formato DD-MM-AAAA)...", id="event_date")
                yield Input(placeholder="Insira a hora do evento (opcional, formato HH:MM)...", id="event_hour")
                yield Label("", id="message")
                yield Button("Criar Evento", id="button_create_event", variant="primary")
                yield Button("Voltar", id="button_return", variant="primary")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
        e executa a ação correspondente:
        - Se for um botão de evento, ela extrai o ID do evento a partir do ID do botão e navega para a tela de detalhes do evento.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        if event.button.id == "button_create_event":
            event_name = self.query_one("#event_name", Input).value
            event_description = self.query_one("#event_description", Input).value
            event_location = self.query_one("#event_location", Input).value
            event_date = self.query_one("#event_date", Input).value
            event_hour = self.query_one("#event_hour", Input).value

            message = event_services.create_event(event_name, event_description, event_location, event_date, event_hour, self.user_id)[1]
            self.query_one("#message", Label).update(message)

        elif event.button.id == "button_return":
            self.app.pop_screen()