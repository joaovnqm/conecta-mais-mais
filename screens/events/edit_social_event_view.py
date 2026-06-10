from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, VerticalScroll, Horizontal
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

#button_save_changes {
    width: 100%;
    margin-top: 1;
}

#button_return {
    width: 100%;
    margin-top: 1;
}

.event_buttons{
    content-align: center middle;
    width: 100%;
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
"""


class EditSocialEventView(Screen):
    """
    Tela responsável pela edição do evento criado pelo usuário.
    """

    CSS = EDIT_SOCIAL_EVENT_PAGE_CSS

    def __init__(self, event_id: int):
        """Inicializa a tela de edição de evento social."""
        super().__init__()
        self.event_id = event_id

    def compose(self) -> ComposeResult:
        """Composição da tela de edição de evento social."""
        event = event_services.check_event(self.event_id)

        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static(f"Editar Evento: {event.name}", id="top_title")
                    yield Static("")

                yield Input(value=event.name, placeholder="Nome do evento", id="input_event_name")
                yield Input(value=event.description, placeholder="Descrição do evento", id="input_event_description")

                yield Input(
                    value=event.event_location or "",
                    placeholder="Local do evento",
                    id="input_event_location"
                )

                yield Input(
                    value=event.date or "",
                    placeholder="Data do evento (DD-MM-AAAA)",
                    id="input_event_date"
                )

                yield Input(
                    value=event.hour or "",
                    placeholder="Hora do evento (HH:MM)",
                    id="input_event_hour"
                )

                yield Input(
                    value=event.official_url or "",
                    placeholder="Link oficial do evento. Ex: https://site.com/evento",
                    id="input_official_url"
                )

                yield Label("", id="message")

                yield Button("Salvar Alterações", id="button_save_changes")
                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Trata cliques nos botões da tela."""
        response = self.query_one("#message", Label)

        if event.button.id == "button_save_changes":
            name = self.query_one("#input_event_name", Input).value.strip()
            description = self.query_one(
                "#input_event_description", Input).value.strip()
            event_location = self.query_one(
                "#input_event_location", Input).value.strip()
            date = self.query_one("#input_event_date", Input).value.strip()
            hour = self.query_one("#input_event_hour", Input).value.strip()
            official_url = self.query_one(
                "#input_official_url", Input).value.strip()

            success, message = event_services.edit_event(
                event_id=self.event_id,
                name=name,
                description=description,
                event_location=event_location,
                date=date,
                hour=hour,
                official_url=official_url,
                auto_update_dates=1
            )

            if success:
                self.app.pop_screen()
                self.app.notify(message)
            else:
                response.update(message)

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.pop_screen()
