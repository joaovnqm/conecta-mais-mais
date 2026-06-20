from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from database.repositories.event_feedback_repository import event_feedback_service
from database.repositories.event_participation import event_participation_service
from database.repositories.event_repository import event_services
from utils.event_feedback_format import format_feedback_summary, format_stars


EVENT_FEEDBACK_VIEW = """
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

.subtitle {
    width: 100%;
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

.info_label {
    margin-top: 1;
    text-style: bold;
}

.social_text,
.empty_state {
    color: $text-muted;
    margin-top: 1;
}

#feedbacks_container {
    width: 100%;
    height: auto;
    margin: 0;
    padding: 0;
}

#rating_buttons {
    width: 100%;
    height: auto;
    layout: grid;
    grid-size: 5;
    grid-columns: 1fr 1fr 1fr 1fr 1fr;
    margin-top: 1;
}

.rating_button {
    width: 100%;
    margin-right: 1;
    content-align: center middle;
}

#feedback_comment,
#button_save_feedback,
#button_delete_feedback,
#button_return {
    width: 100%;
    margin-top: 1;
}
"""


class EventFeedbackView(Screen):
    """
    Tela de feedback do evento.
    """

    CSS = EVENT_FEEDBACK_VIEW

    def __init__(self, user_id: int, event_id: int):
        super().__init__()
        self.user_id = int(user_id)
        self.event_id = int(event_id)
        self.selected_rating: int | None = None

    def compose(self) -> ComposeResult:
        event = event_services.check_event(self.event_id)

        user_feedback = event_feedback_service.get_user_feedback(
            self.user_id,
            self.event_id,
        )

        has_presence = event_participation_service.check_presence(
            self.user_id,
            self.event_id,
        )

        feedback_summary = event_feedback_service.get_feedback_summary(
            self.event_id
        )

        if user_feedback:
            self.selected_rating = user_feedback["rating"]

        with Center():
            with VerticalScroll(id="main_box"):
                yield Button("🏠", id="home_button", variant="primary")
                yield Static("Feedback do Evento", id="top_title")
                yield Static(
                    f"Avalie sua experiência em: {event.name}",
                    classes="subtitle",
                )

                with Vertical(classes="section_card"):
                    if not has_presence:
                        yield Static(
                            "Você precisa confirmar presença neste evento antes de avaliar.",
                            classes="empty_state",
                        )
                    else:
                        yield Static(
                            self._get_rating_label(),
                            id="rating_label",
                            classes="social_text",
                        )

                        yield Static("", id="rating_buttons")

                        yield Static("Comentário:", classes="info_label")
                        yield Input(
                            (user_feedback or {}).get("comment", ""),
                            id="feedback_comment",
                            placeholder="Opinião, sugestão, destaques ou pontos de melhoria...",
                        )

                        yield Button(
                            "Salvar feedback",
                            id="button_save_feedback",
                            variant="success",
                        )

                        yield Button(
                            "Remover feedback",
                            id="button_delete_feedback",
                            variant="error",
                        )

                with Vertical(classes="section_card"):
                    yield Static("Resumo das avaliações", classes="section_title")
                    yield Static(
                        format_feedback_summary(feedback_summary),
                        id="feedback_summary",
                        classes="social_text",
                    )

                with Vertical(classes="section_card"):
                    yield Static("Comentários do evento", classes="section_title")
                    yield Vertical(id="feedbacks_container")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        await self.reload_rating_buttons()
        await self.reload_feedbacks()

    def _get_rating_label(self) -> str:
        if self.selected_rating is None:
            return "Sua nota: ☆ ☆ ☆ ☆ ☆"

        filled = "★ " * self.selected_rating
        empty = "☆ " * (5 - self.selected_rating)
        return f"Sua nota: {(filled + empty).strip()}"

    async def reload_rating_buttons(self) -> None:
        try:
            container = self.query_one("#rating_buttons")
        except Exception:
            return

        await container.remove_children()

        for rating in range(1, 6):
            is_selected = self.selected_rating == rating

            await container.mount(
                Button(
                    "★",
                    id=f"rating_{rating}",
                    variant="success" if is_selected else "default",
                    classes="rating_button",
                )
            )

        self.query_one("#rating_label", Static).update(
            self._get_rating_label()
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id.startswith("rating_"):
            self.selected_rating = int(button_id.split("_", 1)[1])
            await self.reload_rating_buttons()
            return

        if button_id == "button_save_feedback":
            await self.save_feedback()
            return

        if button_id == "button_delete_feedback":
            await self.delete_feedback()
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

        if button_id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()

    async def save_feedback(self) -> None:
        comment = self.query_one("#feedback_comment", Input).value

        success, message = event_feedback_service.save_feedback(
            self.user_id,
            self.event_id,
            self.selected_rating,
            comment,
        )

        self.app.notify(message)

        if success:
            await self.reload_summary()
            await self.reload_feedbacks()
            await self.reload_rating_buttons()

    async def delete_feedback(self) -> None:
        success, message = event_feedback_service.delete_feedback(
            self.user_id,
            self.event_id,
        )

        self.app.notify(message)

        if success:
            self.selected_rating = None
            self.query_one("#feedback_comment", Input).value = ""
            await self.reload_rating_buttons()
            await self.reload_summary()
            await self.reload_feedbacks()

    async def reload_summary(self) -> None:
        summary = event_feedback_service.get_feedback_summary(self.event_id)
        self.query_one("#feedback_summary", Static).update(
            format_feedback_summary(summary)
        )

    async def reload_feedbacks(self) -> None:
        container = self.query_one("#feedbacks_container")
        await container.remove_children()

        feedbacks = event_feedback_service.list_event_feedbacks(self.event_id)

        if not feedbacks:
            await container.mount(
                Static(
                    "Nenhum comentário registrado para este evento.",
                    classes="empty_state",
                )
            )
            return

        for feedback in feedbacks:
            comment = feedback["comment"] or "Sem comentário textual."
            username = feedback["username"] or "sem_username"

            await container.mount(
                Static(
                    f"{format_stars(feedback['rating'])} · "
                    f"{feedback['user_name']} - @{username}\n"
                    f"{comment}",
                    classes="social_text",
                )
            )
