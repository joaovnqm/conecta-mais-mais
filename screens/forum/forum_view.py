from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static
from database.repositories.forum_repository import forum_service
from screens.forum.create_forum_topic_view import CreateForumTopicView
from screens.forum.forum_topic_details_view import ForumTopicDetailsView

FORUM_VIEW_CSS = """
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

.section_title {
    text-style: bold;
    margin-bottom: 1;
}

.topic_text,
.empty_state {
    color: $text-muted;
    margin-top: 1;
}

#topics_container {
    width: 100%;
    height: auto;
    margin: 0;
    padding: 0;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""


class ForumView(Screen):
    """
    Tela principal do fórum
    """
    CSS = FORUM_VIEW_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = int(user_id)

    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Fórum", id="main_title")
                yield Static("Encontre pessoas para pesquisar, projetos e colaboração acadêmica", classes="subtitle")
                yield Button("Criar tópico", id="button_create_topic", variant="success")

                with Vertical(classes="section_card"):
                    yield Static("Tópicos disponíveis", classes="section_title")
                    yield Vertical(id="topics_container")
                    yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        await self.reload_topics()

    async def on_screen_resume(self) -> None:
        await self.reload_topics()

    async def reload_topics(self) -> None:
        """
        Recarrega os tópicos do fórum
        """
        container = self.query_one("#topics_container")
        topics = forum_service.list_topics()

        await container.remove_children()

        if not topics:
            await container.mount(
                Static(
                    "Nenhum tópico criado ainda. Seja o primeiro a iniciar uma colaboração", classes="empty_state")
            )
            return

        for topic in topics:
            username = topic["author_username"] or "sem_username"

            await container.mount(
                Static(
                    f"{topic['title']}\n"
                    f"Autor: {topic['author_name']} - @{username}\n"
                    f"Likes: {topic['total_likes']} | Comentários: {topic['total_comments']}",
                    classes="topic_text",
                )
            )

            await container.mount(
                Button(
                    f"Abrir tópico #{topic['topic_id']}",
                    id=f"button_open_topic_{topic['topic_id']}",
                )
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_create_topic":
            self.app.push_screen(CreateForumTopicView(self.user_id))

        elif button_id.startswith("button_open_topic_"):
            topic_id = int(button_id.replace("button_open_topic_", ""))
            self.app.push_screen(ForumTopicDetailsView(
                user_id=self.user_id, topic_id=topic_id))

        elif button_id == "button_return":
            self.app.pop_screen()
