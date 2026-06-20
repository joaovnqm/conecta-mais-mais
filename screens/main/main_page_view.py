from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static
from database.repositories.user_repository import user_services
from screens.events.events_general_view import EventsGeneralView
from screens.forum.forum_view import ForumView
from screens.profile.profile_view import ProfileView
from screens.social.chats_view import ChatsView
from screens.social.friends_view import FriendsView
from utils.validations import validation_services

MAIN_PAGE_CSS = """
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
}

Button {
    width: 100%;
    margin-top: 1;
}
"""


class MainPageView(Screen):
    """
    Tela principal exibida após o login.
    """

    CSS = MAIN_PAGE_CSS

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = int(user_id)
        self.user_name = validation_services.normalize_name(user_name)

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Main Page", id="main_title")

                yield Static(f"Bem-vindo(a), {self.user_name}!", classes="main_subtitle", id="name")

                yield Button("Meu perfil", id="button_profile")
                yield Button("Eventos", id="button_events")
                yield Button("Fórum", id="button_forum")
                yield Button("Amigos", id="button_friends")
                yield Button("Chat", id="button_chat")
                yield Button("Logout", id="button_logout", variant="error")

    def on_screen_resume(self) -> None:
        user_data = user_services.get_user_profile(self.user_id)

        if user_data is None:
            return

        self.user_name = validation_services.normalize_name(user_data.name)

        self.query_one("#name", Static).update(
            f"Bem-vindo(a), {self.user_name}!")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        from screens.auth.login_view import LoginView

        if event.button.id == "button_profile":
            self.app.push_screen(ProfileView(self.user_id))

        elif event.button.id == "button_events":
            self.app.push_screen(EventsGeneralView(
                self.user_id, self.user_name))

        elif event.button.id == "button_forum":
            self.app.push_screen(ForumView(self.user_id))

        elif event.button.id == "button_friends":
            self.app.push_screen(FriendsView(self.user_id))

        elif event.button.id == "button_chat":
            self.app.push_screen(ChatsView(self.user_id))

        elif event.button.id == "button_logout":
            self.app.push_screen(LoginView())

            current_screen = self.app.screen

            if hasattr(current_screen, "reset_form"):
                current_screen.reset_form()
