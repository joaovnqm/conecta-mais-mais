from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static
from database.repositories.forum_repository import forum_service
from database.repositories.friendship_repository import friendship_services
from screens.forum.report_forum_topic_view import ReportForumTopicView
from screens.profile.public_profile_view import PublicProfileView

FORUM_TOPIC_DETAILS_CSS = """
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

#top_bar {
    width: 100%;
    height: 4;
    layout: grid;
    grid-size: 3;
    grid-columns: 12 1fr 8;
    margin-bottom: 1;
}

#home_button {
    width: 8;
    height: 3;
    margin-right: 2;
}

#top_title {
    content-align: left middle;
    height: 3;
    text-style: bold;
    margin-left: 2;
}

.section_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}

.comments_card {
    width: 100%;
    height: auto;
    min-height: 7;
    margin-top: 1;
    margin-bottom: 2;
}

.section_title {
    text-style: bold;
    margin-bottom: 1;
}

.info_label {
    margin-top: 1;
    text-style: bold;
}

.info_value,
.social_text,
.empty_state {
    color: $text-muted;
    margin-top: 1;
    height: auto;
}

#actions_container {
    width: 100%;
    height: auto;
    margin: 0;
    padding: 0;
}

.action_row {
    width: 100%;
    height: 5;
    margin: 0;
    padding: 0;
}

.action_row Button {
    width: 1fr;
    height: 3;
    margin: 1;
}

#button_report_topic {
    width: 100%;
    height: 3;
    margin-top: 1;
}

#comments_container {
    width: 100%;
    height: auto;
    min-height: 3;
    margin: 0;
    padding: 0;
}

.comment_item {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#input_comment,
#button_add_comment {
    width: 100%;
    margin-top: 1;
}

#button_return {
    width: 100%;
    height: 3;
    margin-top: 2;
}
"""


class ForumTopicDetailsView(Screen):
    """
    Tela de detalhes do tópico do fórum.
    """

    CSS = FORUM_TOPIC_DETAILS_CSS

    def __init__(self, user_id: int, topic_id: int):
        super().__init__()
        self.user_id = int(user_id)
        self.topic_id = int(topic_id)

    def compose(self) -> ComposeResult:
        topic = forum_service.get_topic(self.topic_id)

        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Tópico do Fórum", id="top_title")
                    yield Static("")

                if topic is None:
                    with Vertical(classes="section_card"):
                        yield Static(
                            "Tópico não encontrado.",
                            classes="empty_state",
                        )

                    yield Button("Voltar", id="button_return", variant="primary")
                    return

                author_username = topic["author_username"] or "sem_username"

                with Vertical(classes="section_card"):
                    yield Static(topic["title"], classes="section_title")

                    yield Static("Descrição", classes="info_label")
                    yield Static(topic["description"], classes="info_value")

                    yield Static("Autor:", classes="info_label")
                    yield Static(f"{topic['author_name']} - @{author_username}", classes="info_value")

                    yield Static("Criado em", classes="info_label")
                    yield Static(topic["created_at"], classes="info_value")

                with Vertical(classes="section_card"):
                    yield Static("Resumo", classes="section_title")
                    yield Static("Carregando resumo...", id="topic_summary", classes="social_text")

                with Vertical(classes="section_card"):
                    yield Static("Ações", classes="section_title")
                    yield Vertical(id="actions_container")

                with Vertical(classes="section_card"):
                    yield Static("Comentar", classes="section_title")

                    yield Input(id="input_comment", placeholder="Escreva seu comentário...")

                    yield Button("Comentar", id="button_add_comment", variant="success")

                with Vertical(classes="section_card comments_card"):
                    yield Static("Comentários", classes="section_title")
                    yield Vertical(id="comments_container")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        await self.reload_topic_data()

    async def on_screen_resume(self) -> None:
        await self.reload_topic_data()

    async def reload_topic_data(self) -> None:
        await self.reload_summary()
        await self.reload_actions()
        await self.reload_comments()

    async def reload_summary(self) -> None:
        """
        Atualiza os contadores do tópico.
        """
        try:
            summary_widget = self.query_one("#topic_summary", Static)
        except Exception:
            return

        counts = forum_service.get_topic_counts(self.topic_id)

        summary_widget.update(
            f"Likes: {counts['total_likes']}\n"
            f"Comentários: {counts['total_comments']}\n"
            f"Salvos: {counts['total_saves']}"
        )

    async def reload_actions(self) -> None:
        """
        Atualiza os botões de ação do tópico.
        """
        try:
            container = self.query_one("#actions_container")
        except Exception:
            return

        topic = forum_service.get_topic(self.topic_id)

        await container.remove_children()

        if topic is None:
            return

        liked = forum_service.user_liked_topic(self.topic_id, self.user_id)
        saved = forum_service.user_saved_topic(self.topic_id, self.user_id)
        reported = forum_service.user_reported_topic(
            self.topic_id, self.user_id)
        is_author = topic["author_id"] == self.user_id

        profile_row = Horizontal(classes="action_row")
        await container.mount(profile_row)

        await profile_row.mount(
            Button("Ver perfil", id="button_view_profile", variant="primary"),
            Button("Adicionar amigo", id="button_add_friend", variant="success", disabled=is_author))

        social_row = Horizontal(classes="action_row")
        await container.mount(social_row)

        await social_row.mount(
            Button("Remover curtida" if liked else "Curtir",
                   id="button_toggle_like", variant="default" if liked else "success"),
            Button("Remover dos salvos" if saved else "Salvar", id="button_toggle_save", variant="default" if saved else "warning"))

        await container.mount(
            Button("Denúncia enviada" if reported else "Denunciar", id="button_report_topic", variant="default" if reported else "error", disabled=reported or is_author))

    async def reload_comments(self) -> None:
        """
        Atualiza a lista de comentários do tópico.
        """
        try:
            container = self.query_one("#comments_container")
        except Exception:
            return

        comments = forum_service.list_comments(self.topic_id)

        await container.remove_children()

        if not comments:
            await container.mount(
                Static("Nenhum comentário neste tópico.", classes="empty_state comment_item"))
            return

        for comment in comments:
            username = comment["author_username"] or "sem_username"

            await container.mount(
                Static(
                    f"{comment['author_name']} - @{username}\n"
                    f"{comment['content']}",
                    classes="social_text comment_item",
                )
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_view_profile":
            await self.open_public_profile()
            return

        if button_id == "button_add_friend":
            await self.add_friend()
            return

        if button_id == "button_add_comment":
            await self.add_comment()
            return

        if button_id == "button_toggle_like":
            await self.toggle_like()
            return

        if button_id == "button_toggle_save":
            await self.toggle_save()
            return

        if button_id == "button_report_topic":
            self.app.push_screen(
                ReportForumTopicView(
                    user_id=self.user_id,
                    topic_id=self.topic_id,
                )
            )
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

        if button_id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()
            return

    async def open_public_profile(self) -> None:
        """
        Abre o perfil público do autor do tópico.
        """
        topic = forum_service.get_topic(self.topic_id)

        if topic is None:
            self.app.notify("Tópico não encontrado.", severity="error")
            return

        self.app.push_screen(PublicProfileView(
            viewer_id=self.user_id, profile_user_id=topic["author_id"]))

    async def add_friend(self) -> None:
        """
        Envia solicitação de amizade para o autor do tópico.
        """
        topic = forum_service.get_topic(self.topic_id)

        if topic is None:
            self.app.notify("Tópico não encontrado.", severity="error")
            return

        success, message = friendship_services.send_friend_request_by_user_id(requester_id=self.user_id,
                                                                              target_id=topic["author_id"],
                                                                              )

        self.app.notify(message)

        if success:
            await self.reload_actions()

    async def toggle_like(self) -> None:
        """
        Curte ou remove curtida do tópico.
        """
        success, message = forum_service.toggle_like(
            topic_id=self.topic_id,
            user_id=self.user_id,
        )

        self.app.notify(message)

        if success:
            await self.reload_summary()
            await self.reload_actions()

    async def toggle_save(self) -> None:
        """
        Salva ou remove o tópico dos salvos.
        """
        success, message = forum_service.toggle_save(
            topic_id=self.topic_id,
            user_id=self.user_id,
        )

        self.app.notify(message)

        if success:
            await self.reload_summary()
            await self.reload_actions()

    async def add_comment(self) -> None:
        """
        Publica um comentário no tópico e atualiza a tela imediatamente.
        """
        comment_input = self.query_one("#input_comment", Input)

        success, message = forum_service.add_comment(
            topic_id=self.topic_id,
            author_id=self.user_id,
            content=comment_input.value,
        )

        self.app.notify(message)

        if not success:
            return

        comment_input.value = ""

        await self.reload_summary()
        await self.reload_comments()
