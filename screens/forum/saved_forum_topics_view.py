from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static
from database.repositories.forum_repository import forum_service
from screens.forum.forum_topic_details_view import ForumTopicDetailsView

SAVED_FORUM_TOPICS_CSS = """
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

#saved_topics_container {
    width: 100%;
    height: auto;
    min-height: 3;
    margin: 0;
    padding: 0;
}

.topic_item {
    width: 100%;
    height: auto;
    margin-top: 1;
}

.topic_text,
.empty_state {
    color: $text-muted;
    margin-top: 1;
    height: auto;
}

Button {
    width: 100%;
    height: 3;
    margin-top: 1;
}

#button_return {
    margin-top: 2;
}
"""

class SavedForumTopicsView(Screen):
    """
    Tela responsável por listar os tópicos salvos pelo usuário.
    """

    CSS = SAVED_FORUM_TOPICS_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = int(user_id)

    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Tópicos Salvos", id="main_title")

                yield Static("Veja os tópicos que você salvou para consultar depois.",classes="subtitle")

                with Vertical(classes="section_card"):
                    yield Static("Meus tópicos salvos", classes="section_title")
                    yield Vertical(id="saved_topics_container")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        await self.reload_saved_topics()

    async def on_screen_resume(self) -> None:
        await self.reload_saved_topics()

    async def reload_saved_topics(self) -> None:
        """
        Recarrega os tópicos salvos do usuário.
        """
        try:
            container = self.query_one("#saved_topics_container")
        except Exception:
            return

        saved_topics = forum_service.list_saved_topics(self.user_id)

        await container.remove_children()

        if not saved_topics:
            await container.mount(
                Static("Você ainda não salvou nenhum tópico.",classes="empty_state topic_item"))
            return

        for topic in saved_topics:
            author_username = topic["author_username"] or "sem_username"

            await container.mount(
                Static(
                    f"{topic['title']}\n"
                    f"Autor: {topic['author_name']} - @{author_username}\n"
                    f"Likes: {topic['total_likes']} | "
                    f"Comentários: {topic['total_comments']} | "
                    f"Salvos: {topic['total_saves']}\n"
                    f"Salvo em: {topic['saved_at']}",
                    classes="topic_text topic_item"))

            await container.mount(
                Button(f"Abrir tópico #{topic['topic_id']}",
                    id=f"button_open_saved_topic_{topic['topic_id']}",
                    variant="primary"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id.startswith("button_open_saved_topic_"):
            topic_id = int(
                button_id.replace("button_open_saved_topic_", "")
            )

            self.app.push_screen(
                ForumTopicDetailsView(
                    user_id=self.user_id,
                    topic_id=topic_id,
                )
            )
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return