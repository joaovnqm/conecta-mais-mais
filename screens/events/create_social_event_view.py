from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll, Horizontal
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

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

#top_bar {
    width: 100%;
    height: auto;
    layout: grid;
    grid-size: 3;
    grid-columns: 6 1fr 6;
    margin-bottom: 1;
}

#home_button {
    width: 8;
    height: 3;
}

#top_title {
    content-align: center middle;
    height: 3;
    text-style: bold;
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

#button_create_event {
    width: 100%;
    margin-top: 1;
}

#button_return {
    width: 100%;
    margin-top: 1;
}
"""


class CreateSocialEventView(Screen):
    """
    Tela responsável pela criação de eventos sociais.
    """

    CSS = CREATE_SOCIAL_EVENT_PAGE_CSS

    def __init__(self, user_id: int):
        """Inicializa a tela de criação de eventos sociais, recebendo o ID do usuário logado para associar o evento criado a ele."""
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        """Função que compõe a interface da tela de criação de eventos sociais. Ela cria os campos de entrada para as informações do 
        evento, os botões para criar o evento e voltar, e um campo para exibir mensagens de erro ou sucesso."""
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Criar Evento Social", id="top_title")
                    yield Static("")

                yield Static("Preencha as informações do evento que você deseja criar:")
                yield Input(placeholder="Insira o nome do evento...", id="event_name")
                yield Input(placeholder="Insira a descrição do evento...", id="event_description")
                yield Input(placeholder="Insira o local do evento (opcional)...", id="event_location")
                yield Input(placeholder="Insira a data do evento (opcional, formato DD-MM-AAAA)...", id="event_date")
                yield Input(placeholder="Insira a hora do evento (opcional, formato HH:MM)...", id="event_hour")
                yield Input(
                    placeholder="Link oficial do evento (opcional). Ex: https://site.com/evento",
                    id="event_official_url"
                )

                yield Static("", id="message")

                yield Button("Criar Evento", id="button_create_event", variant="primary")
                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado, coleta os dados dos campos 
        de entrada e chama o serviço de criação de evento social."""
        if event.button.id == "button_create_event":
            event_name = self.query_one("#event_name", Input).value
            event_description = self.query_one(
                "#event_description", Input).value
            event_location = self.query_one("#event_location", Input).value
            event_date = self.query_one("#event_date", Input).value
            event_hour = self.query_one("#event_hour", Input).value
            event_official_url = self.query_one(
                "#event_official_url", Input).value

            success, message = event_services.create_event(
                name=event_name,
                description=event_description,
                event_location=event_location,
                date=event_date,
                hour=event_hour,
                creator_id=self.user_id,
                interest="Social",
                official_url=event_official_url,
                auto_update_dates=1
            )

            if success:
                self.app.notify(message)
                self.app.pop_screen()
            else:
                self.query_one("#message", Static).update(message)

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            self.app.pop_screen()
            self.app.pop_screen()
