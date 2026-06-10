from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Center, VerticalScroll, Horizontal, Vertical
from textual.widgets import Static, Button

from services.badges_services import BADGES, get_user_badges


BADGES_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box {
    width: 90;
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

#button_return {
    width: 100%;
    margin-top: 2;
}

.badge_row {
    width: 100%;
    height: 6;
    border: round $primary;
    padding: 1;
    margin-top: 1;
    background: $surface;
}

.badge_icon {
    width: 10%;
    content-align: left middle;
}

.badge_text {
    width: 70%;
    margin-left: 1;
    content-align: center middle;
}

.badge_unlocked {
    color: green;
    text-style: bold;
}

.badge_locked {
    color: $text-muted;
}
"""


class BadgesView(Screen):
    """Tela que exibe todas as badges desbloqueáveis e marca as já conquistadas."""

    CSS = BADGES_CSS

    def __init__(self, user_id: int):
        """Inicializa a tela de badges para um usuário específico."""
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        """Componha a interface da tela de badges, listando todas as badges e indicando quais estão desbloqueadas para o usuário."""
        unlocked = get_user_badges(self.user_id)
        unlocked_ids = {b.id for b in unlocked}
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Conquistas (Badges)", id="top_title")
                    yield Static("")

                yield Static("Aqui estão todas as badges disponíveis para serem desbloqueadas.", classes="subtitle")
                for badge in BADGES:
                    is_unlocked = badge["id"] in unlocked_ids
                    status_text = "✔ Desbloqueada" if is_unlocked else "🔒 Trancada"
                    status_class = "badge_unlocked" if is_unlocked else "badge_locked"
                    with Horizontal(classes="badge_row"):
                        yield Static(badge.get("icon", ""), classes="badge_icon")
                        with Vertical(classes="badge_text"):
                            yield Static(badge.get("name", ""))
                            yield Static(badge.get("description", ""), classes="info_value")
                        yield Static(status_text, classes=status_class)

                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os eventos de clique nos botões, permitindo a navegação de volta ou para a tela inicial."""
        if event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()
