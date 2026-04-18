from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical
from screens.events_view import EventsView
from screens.profile_view import ProfileView
from services.validations import normalize_name

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

# Tela principal exibida após a autenticação do usuário
class MainPageView(Screen):
    CSS = MAIN_PAGE_CSS
    
    # Inicializa a tela principal com os dados do usuário autenticado
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_name = normalize_name(user_name)
        self.user_id = user_id
    
    # Monta a tela principal após o login
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Main Page", id="main_title")
                yield Static(
                    f"Bem-vindo(a), {self.user_name}!",
                    classes="main_subtitle"
                )

                yield Button("Meu perfil", id="button_profile")
                yield Button("Eventos", id="button_events")
                yield Button("Meus amigos", id="button_friends")
                yield Button("Logout", id="button_logout", variant="error")
    
    # Trata a navegação para perfil, eventos, amigos ou logout
    def on_button_pressed(self, event: Button.Pressed) -> None:
        from screens.login_view import LoginView
        
        if event.button.id == "button_profile":
            self.app.push_screen(ProfileView(self.user_id))

        elif event.button.id == "button_events":
            self.app.push_screen(EventsView(self.user_id, self.user_name))

        elif event.button.id == "button_friends":
            self.notify("TELA DE MEUS AMIGOS EM CONSTRUÇÃO")

        elif event.button.id == "button_logout":
            self.app.push_screen(LoginView())

            current_screen = self.app.screen
            if hasattr(current_screen, "reset_form"):
                current_screen.reset_form()
