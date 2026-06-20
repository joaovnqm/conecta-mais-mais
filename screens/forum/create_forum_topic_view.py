from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from database.repositories.forum_repository import forum_service


CREATE_FORUM_TOPIC_CSS = """
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


class CreateForumTopicView(Screen):
    """
    Tela responsável pela criação de tópicos no fórum.

    A tela apenas coleta os dados do formulário e chama o ForumService.
    A regra de negócio fica em database/repositories/forum_repository.py.
    """

    CSS = CREATE_FORUM_TOPIC_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = int(user_id)

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Criar tópico", id="main_title")

                yield Static(
                    "Descreva sua ideia e encontre pessoas para colaborar.",
                    classes="subtitle",
                )

                with Vertical(classes="section_card"):
                    yield Static("Título:", classes="info_label")

                    yield Input(
                        id="input_title",
                        placeholder="Ex.: Inteligência Artificial",
                    )

                    yield Static("Descrição:", classes="info_label")

                    yield Input(
                        id="input_description",
                        placeholder="Explique a pesquisa, projeto ou perfil de colaboração que procura.",
                    )

                    yield Button(
                        "Criar tópico",
                        id="button_save_topic",
                        variant="success",
                    )

                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_save_topic":
            self.create_topic()
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

    def create_topic(self) -> None:
        """
        Cria um tópico usando o ForumService.
        """
        title = self.query_one("#input_title", Input).value
        description = self.query_one("#input_description", Input).value

        success, message, _topic_id = forum_service.create_topic(
            author_id=self.user_id,
            title=title,
            description=description,
        )

        self.app.notify(message)

        if success:
            self.app.pop_screen()
