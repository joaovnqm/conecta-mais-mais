from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from database.repositories.forum_repository import forum_service


REPORT_FORUM_TOPIC_CSS = """
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

.subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

.section_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}

.info_label {
    margin-top: 1;
    text-style: bold;
}

Input,
Button {
    width: 100%;
    margin-top: 1;
}
"""


class ReportForumTopicView(Screen):
    """
    Tela responsável por registrar denúncia de tópico.

    A denúncia não remove o tópico automaticamente.
    Ela apenas registra o motivo no banco para análise futura.
    """

    CSS = REPORT_FORUM_TOPIC_CSS

    def __init__(self, user_id: int, topic_id: int):
        super().__init__()
        self.user_id = int(user_id)
        self.topic_id = int(topic_id)

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Denunciar tópico", id="main_title")

                yield Static(
                    "Informe o motivo da denúncia. Ela será registrada para análise.",
                    classes="subtitle",
                )

                with Vertical(classes="section_card"):
                    yield Static("Motivo:", classes="info_label")

                    yield Input(
                        id="input_reason",
                        placeholder="Explique por que este tópico deve ser analisado.",
                    )

                    yield Button(
                        "Enviar denúncia",
                        id="button_send_report",
                        variant="error",
                    )

                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_send_report":
            self.send_report()
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

    def send_report(self) -> None:
        """
        Envia a denúncia para o ForumService.
        """
        reason = self.query_one("#input_reason", Input).value

        success, message = forum_service.report_topic(
            topic_id=self.topic_id,
            reporter_id=self.user_id,
            reason=reason,
        )

        self.app.notify(message)

        if success:
            self.app.pop_screen()
