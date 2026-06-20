from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from database.repositories.friendship_repository import friendship_services
from database.repositories.user_repository import user_services


PUBLIC_PROFILE_CSS = """
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

.profile_label {
    margin-top: 1;
    text-style: bold;
}

.profile_value,
.empty_state {
    color: $text-muted;
    margin-top: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""


class PublicProfileView(Screen):
    """
    Tela de perfil público de outro usuário.
    """

    CSS = PUBLIC_PROFILE_CSS

    def __init__(self, viewer_id: int, profile_user_id: int):
        super().__init__()
        self.viewer_id = int(viewer_id)
        self.profile_user_id = int(profile_user_id)

    def compose(self) -> ComposeResult:
        profile = user_services.get_user_profile(self.profile_user_id)

        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Perfil público", id="main_title")

                yield Static(
                    "Informações públicas do usuário.",
                    classes="subtitle",
                )

                if profile is None:
                    with Vertical(classes="section_card"):
                        yield Static(
                            "Usuário não encontrado.",
                            classes="empty_state",
                        )

                else:
                    with Vertical(classes="section_card"):
                        yield Static("Dados pessoais", classes="section_title")

                        yield Static("Nome:", classes="profile_label")
                        yield Static(profile.name, classes="profile_value")

                        yield Static("E-mail:", classes="profile_label")
                        yield Static(profile.email, classes="profile_value")

                    with Vertical(classes="section_card"):
                        yield Static("Dados sociais", classes="section_title")

                        yield Static("Username:", classes="profile_label")
                        yield Static(
                            profile.username or "Username não informado.",
                            classes="profile_value",
                        )

                        yield Static("LinkedIn:", classes="profile_label")
                        yield Static(
                            self._build_linkedin_text(profile.linkedin_url),
                            classes="profile_value",
                        )

                        yield Static("GitHub:", classes="profile_label")
                        yield Static(
                            self._build_github_text(profile.github_url),
                            classes="profile_value",
                        )

                    if self.viewer_id != self.profile_user_id:
                        yield Button(
                            "Adicionar amigo",
                            id="button_add_friend",
                            variant="success",
                        )

                yield Button("Voltar", id="button_return", variant="primary")

    def _build_linkedin_text(self, linkedin_url: str | None):
        """
        Monta o texto do LinkedIn.
        Se houver link, ele fica clicável em terminais compatíveis.
        """
        if not linkedin_url:
            return "LinkedIn não informado."

        linkedin_text = Text()
        linkedin_text.append(
            linkedin_url,
            style=f"link {linkedin_url} underline",
        )

        return linkedin_text

    def _build_github_text(self, github_url: str | None):
        """
        Monta o texto do GitHub.
        Se houver link, ele fica clicável em terminais compatíveis.
        """
        if not github_url:
            return "GitHub não informado."

        github_text = Text()
        github_text.append(
            github_url,
            style=f"link {github_url} underline",
        )

        return github_text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id == "button_add_friend":
            self.add_friend()
            return

        if button_id == "button_return":
            self.app.pop_screen()
            return

    def add_friend(self) -> None:
        """
        Envia solicitação de amizade para o usuário visualizado.
        """
        success, message = friendship_services.send_friend_request_by_user_id(
            requester_id=self.viewer_id,
            target_id=self.profile_user_id,
        )

        self.app.notify(message)
