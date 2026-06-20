from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from database.repositories.forum_repository import forum_service


FORUM_REPORT_DETAILS_CSS = """
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

.info_label {
    margin-top: 1;
    text-style: bold;
}

.info_value,
.empty_state {
    color: $text-muted;
    margin-top: 1;
    height: auto;
}

Input,
Button {
    width: 100%;
    height: 3;
    margin-top: 1;
}

#button_accept_report {
    margin-top: 2;
}
"""


class ForumReportDetailsView(Screen):
    """
    Tela de detalhes de denúncia.
    """

    CSS = FORUM_REPORT_DETAILS_CSS

    def __init__(self, admin_id: int, report_id: int):
        super().__init__()
        self.admin_id = int(admin_id)
        self.report_id = int(report_id)

    def compose(self) -> ComposeResult:
        report = forum_service.get_report_details(self.report_id)

        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Detalhes da Denúncia", id="main_title")

                yield Static("Revise o conteúdo denunciado antes de tomar uma decisão.", classes="subtitle")

                if report is None:
                    with Vertical(classes="section_card"):
                        yield Static("Denúncia não encontrada.", classes="empty_state")

                    yield Button("Voltar", id="button_return", variant="primary")
                    return

                with Vertical(classes="section_card"):
                    yield Static("Tópico denunciado", classes="section_title")

                    yield Static("Título:", classes="info_label")
                    yield Static(report["topic_title"], classes="info_value")

                    yield Static("Descrição:", classes="info_label")
                    yield Static(report["topic_description"], classes="info_value")

                    yield Static("Status do tópico:", classes="info_label")
                    yield Static(report["topic_status"], classes="info_value")

                    yield Static("Autor do tópico:", classes="info_label")

                    topic_author_username = (
                        report["topic_author_username"] or "sem_username")

                    yield Static(f"{report['topic_author_name']} - @{topic_author_username}", classes="info_value")

                with Vertical(classes="section_card"):
                    yield Static("Dados da denúncia", classes="section_title")

                    reporter_username = report["reporter_username"] or "sem_username"

                    yield Static("Denunciante:", classes="info_label")
                    yield Static(
                        f"{report['reporter_name']} - @{reporter_username}",
                        classes="info_value",
                    )

                    yield Static("Motivo:", classes="info_label")
                    yield Static(report["reason"], classes="info_value")

                    yield Static("Status da denúncia:", classes="info_label")
                    yield Static(report["status"], classes="info_value")

                    yield Static("Criada em:", classes="info_label")
                    yield Static(report["created_at"], classes="info_value")

                if report["status"] == "pending":
                    with Vertical(classes="section_card"):
                        yield Static("Decisão administrativa", classes="section_title")

                        yield Static("Observação do admin:", classes="info_label")
                        yield Input(id="input_admin_note", placeholder="Opcional: explique a decisão tomada.")

                        yield Button("Aceitar denúncia e remover tópico", id="button_accept_report", variant="error")

                        yield Button("Rejeitar denúncia e manter tópico", id="button_reject_report", variant="success")

                else:
                    with Vertical(classes="section_card"):
                        yield Static("Denúncia já analisada", classes="section_title")

                        yield Static("Observação administrativa:", classes="info_label")
                        yield Static(report["admin_note"] or "Sem observação.", classes="info_value")

                        yield Static("Analisada em:", classes="info_label")
                        yield Static(report["reviewed_at"] or "Data não registrada.", classes="info_value")

                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_accept_report":
            self.accept_report()
            return

        if button_id == "button_reject_report":
            self.reject_report()
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

    def _get_admin_note(self) -> str:
        """
        Retorna a observação administrativa, se o input existir.
        """
        try:
            return self.query_one("#input_admin_note", Input).value
        except Exception:
            return ""

    def accept_report(self) -> None:
        """
        Aceita a denúncia e remove o tópico da listagem pública.
        """
        success, message = forum_service.accept_report(
            report_id=self.report_id,
            admin_id=self.admin_id,
            admin_note=self._get_admin_note(),
        )

        self.app.notify(message)

        if success:
            self.app.pop_screen()

    def reject_report(self) -> None:
        """
        Rejeita a denúncia e mantém o tópico ativo.
        """
        success, message = forum_service.reject_report(
            report_id=self.report_id,
            admin_id=self.admin_id,
            admin_note=self._get_admin_note(),
        )

        self.app.notify(message)

        if success:
            self.app.pop_screen()
