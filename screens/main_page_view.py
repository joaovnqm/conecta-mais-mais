from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical

MAIN_PAGE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 60;
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

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""


class MainPageView(Screen):
    CSS = MAIN_PAGE_CSS

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_name = user_name
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Main Page", id="main_title")
                yield Static(
                    f"Bem-vindo(a), {self.user_name}!",
                    classes="main_subtitle"
                )

                yield Button("Meu perfil", id="button_profile")
                yield Button("Meus eventos", id="button_events")
                yield Button("Meus amigos", id="button_friends")
                yield Button("Logout", id="button_logout", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        from screens.login_view import LoginView
        if event.button.id == "button_profile":
            self.notify("TELA DE PERFIL EM CONSTRUÇÃO")

        elif event.button.id == "button_events":
            self.notify("TELA DE MEUS EVENTOS EM CONSTRUÇÃO")

        elif event.button.id == "button_friends":
            self.notify("TELA DE MEUS AMIGOS EM CONSTRUÇÃO")

        elif event.button.id == "button_logout":
            self.app.push_screen(LoginView())

            current_screen = self.app.screen
            if hasattr(current_screen, "reset_form"):
                current_screen.reset_form()
