from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from database.repositories.ranking_repository import RankingRepository


class RankingView(Screen):
    """
    Tela de ranking dos usuários com base na participação em eventos.
    """

    CSS = """
    RankingView {
        align: center middle;
    }

    #ranking-container {
        width: 90%;
        height: 90%;
        border: solid $primary;
        padding: 1 2;
    }

    #ranking-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #ranking-subtitle {
        text-align: center;
        margin-bottom: 1;
    }

    #ranking-table {
        height: 1fr;
        margin-top: 1;
        margin-bottom: 1;
    }

    #ranking-actions {
        align: center middle;
        height: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.repository = RankingRepository()

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="ranking-container"):
            yield Static("🏆 Ranking de Eventos", id="ranking-title")
            yield Static(
                "Pontuação baseada em presença, certificados e apresentações.",
                id="ranking-subtitle",
            )

            yield DataTable(id="ranking-table")

            with Horizontal(id="ranking-actions"):
                yield Button("Voltar", id="back_button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        self.load_ranking()

    def load_ranking(self) -> None:
        table = self.query_one("#ranking-table", DataTable)

        table.clear(columns=True)

        table.add_columns(
            "Posição",
            "Usuário",
            "Nível",
            "Pontos",
            "Eventos",
            "Certificados",
            "Apresentações",
        )

        ranking = self.repository.get_ranking()

        if not ranking:
            table.add_row(
                "-",
                "Nenhum usuário ranqueado ainda",
                "-",
                "0",
                "0",
                "0",
                "0",
            )
            return

        for user in ranking:
            table.add_row(
                str(user["position"]),
                user["name"],
                user["current_level"],
                str(user["total_points"]),
                str(user["events_attended"]),
                str(user["certificates_received"]),
                str(user["presentations_done"]),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()
