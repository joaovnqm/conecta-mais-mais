from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Static
from database.repositories.ranking_repository import RankingRepository

RANKING_PAGE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box {
    width: 100;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
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

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.main_subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

#levels_container {
    border: round $primary-background-lighten-1;
    padding: 1;
    margin-bottom: 1;
    height: 10;
}

.level_column {
    width: 1fr;
}

.level_line {
    height: auto;
    content-align: center middle;
}

#ranking_table {
    width: 100%;
    height: 20;
    margin-top: 1;
    margin-bottom: 1;
}

#button_return {
    width: 100%;
    margin-top: 1;
}
"""


class RankingView(Screen):
    """
    Tela de ranking dos usuários baseada na participação
    em eventos, certificados e apresentações.
    """

    CSS = RANKING_PAGE_CSS

    def __init__(self) -> None:
        """Inicializa a tela de ranking, criando uma instância do repositório de ranking para acessar os dados necessários para exibir o ranking dos usuários."""
        super().__init__()
        self.repository = RankingRepository()

    def compose(self) -> ComposeResult:
        """Define a estrutura da tela de ranking, incluindo o título, descrição, níveis de progressão e a tabela de ranking dos usuários."""
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("🏆 Ranking de Participação", id="top_title")
                    yield Static("")

                yield Static("Pontuação baseada em presença em eventos, certificados recebidos e apresentações realizadas.", classes="main_subtitle")
                yield Static("Níveis de Progressão", classes="main_subtitle")
                with Horizontal(id="levels_container"):
                    with Vertical(classes="level_column"):
                        yield Static("Nível 1 • Recém-chegado", classes="level_line")
                        yield Static("Nível 2 • Participante", classes="level_line")
                        yield Static("Nível 3 • Explorador", classes="level_line")
                        yield Static("Nível 4 • Engajado", classes="level_line")
                        yield Static("Nível 5 • Experiente", classes="level_line")

                    with Vertical(classes="level_column"):
                        yield Static("Nível 6 • Influente", classes="level_line")
                        yield Static("Nível 7 • Referência", classes="level_line")
                        yield Static("Nível 8 • Elite", classes="level_line")
                        yield Static("Nível 9 • Mestre", classes="level_line")
                        yield Static("Nível 10 • Lendário", classes="level_line")

                yield DataTable(id="ranking_table")

                yield Button("Voltar", id="button_return", variant="primary")

    def on_mount(self) -> None:
        """Carrega os dados do ranking quando a tela é montada."""
        self.load_ranking()

    def load_ranking(self) -> None:
        """
        Carrega os dados do ranking.
        """
        table = self.query_one("#ranking_table", DataTable)
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
            table.add_row("-", "Nenhum usuário ranqueado", "-", "0", "0", "0", "0")
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
        """
        Trata os cliques dos botões.
        """

        if event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            self.app.pop_screen()