from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static
from database.repositories.forum_repository import forum_service
from screens.forum.forum_report_details_view import ForumReportDetailsView


FORUM_MODERATION_CSS = """
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

.report_text,
.empty_state {
    color: $text-muted;
    margin-top: 1;
    height: auto;
}

#reports_container {
    width: 100%;
    height: auto;
    min-height: 3;
    margin: 0;
    padding: 0;
}

.report_item {
    width: 100%;
    height: auto;
    margin-top: 1;
}

Button {
    width: 100%;
    height: 3;
    margin-top: 1;
}
"""


class ForumModerationView(Screen):
    """
    Tela de moderação do fórum.
    """

    CSS = FORUM_MODERATION_CSS

    def __init__(self, admin_id: int):
        super().__init__()
        self.admin_id = int(admin_id)

    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Moderação do Fórum", id="main_title")

                yield Static("Analise denúncias pendentes enviadas pelos usuários.", classes="subtitle")

                with Vertical(classes="section_card"):
                    yield Static("Denúncias pendentes", classes="section_title")
                    yield Vertical(id="reports_container")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        await self.reload_reports()

    async def on_screen_resume(self) -> None:
        await self.reload_reports()

    async def reload_reports(self) -> None:
        """
        Atualiza a lista de denúncias pendentes.
        """
        container = self.query_one("#reports_container")
        reports = forum_service.list_pending_reports()

        await container.remove_children()

        if not reports:
            await container.mount(
                Static(
                    "Nenhuma denúncia pendente no momento.", classes="empty_state report_item"))
            return

        for report in reports:
            reporter_username = report["reporter_username"] or "sem_username"
            author_username = report["topic_author_username"] or "sem_username"

            await container.mount(
                Static(
                    f"Tópico: {report['topic_title']}\n"
                    f"Autor: {report['topic_author_name']} - @{author_username}\n"
                    f"Denunciante: {report['reporter_name']} - @{reporter_username}\n"
                    f"Motivo: {report['reason']}\n"
                    f"Data: {report['created_at']}",
                    classes="report_text report_item",
                )
            )

            await container.mount(
                Button(
                    f"Abrir denúncia #{report['report_id']}",
                    id=f"button_open_report_{report['report_id']}",
                    variant="primary",
                )
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id.startswith("button_open_report_"):
            report_id = int(button_id.replace("button_open_report_", ""))

            self.app.push_screen(ForumReportDetailsView(
                admin_id=self.admin_id, report_id=report_id))
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return
