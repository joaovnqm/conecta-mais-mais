from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical
from screens.events_view import EventsView
from screens.profile_view import ProfileView
from screens.favorite_events_list_view import FavoriteEventsList
from services.validations import normalize_name
from services.users import get_user_profile

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
    """
    Classe responsável pela tela principal do aplicativo. Ela é exibida após o login bem-sucedido, e oferece opções de navegação para
    o perfil do usuário, a lista de eventos disponíveis, a lista de eventos favoritados, e a opção de logout.
    """
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
                yield Static(f"Bem-vindo(a), {self.user_name}!", classes="main_subtitle", id="name")

                yield Button("Meu perfil", id="button_profile")
                yield Button("Eventos", id="button_events")
                yield Button("Eventos Favoritados", id="button_favorite_events")
                yield Button("Logout", id="button_logout", variant="error")

    def on_screen_resume(self) -> None:
            user_data = get_user_profile(self.user_id)
            name = user_data.get("name", self.user_name) 
            self.user_name = normalize_name(name)
            welcome_message = self.query_one("#name", Static)
            welcome_message.update(f"Bem-vindo(a), {self.user_name}!")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela principal. Ela verifica qual botão foi clicado, e executa a ação 
        correspondente:
        - Se for o botão de perfil, ela navega para a tela de perfil do usuário.
        - Se for o botão de eventos, ela navega para a tela de listagem de eventos disponíveis.
        - Se for o botão de eventos favoritados, ela navega para a tela de listagem de eventos favoritados pelo usuário.
        - Se for o botão de logout, ela navega para a tela de login e reseta os campos do formulário de login para 
        facilitar uma nova tentativa de login.
        """
        from screens.login_view import LoginView
        
        if event.button.id == "button_profile":
            self.app.push_screen(ProfileView(self.user_id))

        elif event.button.id == "button_events":
            self.app.push_screen(EventsView(self.user_id, self.user_name))

        elif event.button.id == "button_favorite_events":
            self.app.push_screen(FavoriteEventsList(self.user_id))

        elif event.button.id == "button_logout":
            self.app.push_screen(LoginView())

            current_screen = self.app.screen
            if hasattr(current_screen, "reset_form"):
                current_screen.reset_form()