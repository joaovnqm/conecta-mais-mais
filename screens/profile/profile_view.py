from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll, Vertical

from database.repositories.user_repository import user_services
from screens.profile.edit_name_view import EditNameView
from screens.profile.change_password_view import ChangePasswordView
from screens.profile.delete_account_view import DeleteAccountView
from screens.profile.change_interests_view import ChangeInterestView


PROFILE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#profile_box {
    width: 90;
    height: 40;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#profile_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

#subtitle {
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

.profile_value {
    color: $text-muted;
    margin-bottom: 1;
}

.profile_action {
    width: 100%;
    margin-top: 1;
}

#button_delete_account {
    width: 100%;
    margin-top: 1;
}

#button_back {
    width: 100%;
    margin-top: 1;
}

.empty_state {
    color: $text-muted;
    margin-top: 1;
}
"""


class ProfileView(Screen):
    """
    Tela responsável por exibir e gerenciar os dados do perfil do usuário.
    """

    CSS = PROFILE_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        profile = user_services.get_user_profile(self.user_id)

        with Center():
            with VerticalScroll(id="profile_box"):
                yield Static("Meu perfil", id="profile_title")
                yield Static(
                    "Gerencie seus dados pessoais, sociais e preferências.",
                    id="subtitle"
                )

                if profile is None:
                    with Vertical(classes="section_card"):
                        yield Static(
                            "Usuário não encontrado.",
                            id="name_value",
                            classes="empty_state"
                        )

                else:
                    with Vertical(classes="section_card"):
                        yield Static("Dados pessoais", classes="section_title")
                        yield Static("Nome:", classes="profile_label")
                        yield Static(profile.name, id="name_value", classes="profile_value")
                        yield Static("E-mail:", classes="profile_label")
                        yield Static(profile.email,id="email_value", classes="profile_value")

                    with Vertical(classes="section_card"):
                        yield Static("Dados sociais", classes="section_title")
                        yield Static("Username:", classes="profile_label")
                        yield Static(profile.username or "Username não informado.", id="username_value", classes="profile_value")
                        yield Static("LinkedIn:", classes="profile_label")
                        yield Static(self._build_linkedin_text(profile.linkedin_url), id="linkedin_value", classes="profile_value")
                        yield Static("GitHub:", classes="profile_label")
                        yield Static(self._build_github_text(profile.github_url), id="github_value", classes="profile_value")

                    with Vertical(classes="section_card"):
                        yield Static("Ações do perfil", classes="section_title")
                        yield Button(
                            "👤 Atualizar dados do perfil",
                            id="button_edit_name",
                            classes="profile_action",
                            variant="primary"
                        )

                        yield Button(
                            "🔐 Atualizar senha",
                            id="button_change_password",
                            classes="profile_action",
                            variant="warning"
                        )

                        yield Button(
                            "⭐ Alterar interesses",
                            id="button_change_interests",
                            classes="profile_action",
                            variant="success"
                        )

                        yield Button(
                            "Deletar conta",
                            id="button_delete_account",
                            variant="error",
                            classes="profile_action"
                        )

                yield Button("Voltar", id="button_back", variant="primary")

    def _build_linkedin_text(self, linkedin_url: str | None):
        """
        Monta o texto do LinkedIn.
        Quando o terminal suporta links, o endereço fica clicável.
        """
        if not linkedin_url:
            return "LinkedIn não informado."

        linkedin_text = Text()
        linkedin_text.append(
            linkedin_url,
            style=f"link {linkedin_url} underline"
        )

        return linkedin_text

    def _build_github_text(self, github_url: str | None):
        """
        Monta o texto do GitHub.
        Quando o terminal suporta links, o endereço fica clicável.
        """
        if not github_url:
            return "GitHub não informado."

        github_text = Text()
        github_text.append(
            github_url,
            style=f"link {github_url} underline"
        )

        return github_text

    def reload_profile(self) -> None:
        """
        Recarrega os dados do perfil após alterações feitas em outras telas.
        """
        profile = user_services.get_user_profile(self.user_id)

        if profile is None:
            return

        self.query_one("#name_value", Static).update(profile.name)
        self.query_one("#email_value", Static).update(profile.email)

        self.query_one("#username_value", Static).update(
            profile.username or "Username não informado."
        )

        self.query_one("#linkedin_value", Static).update(
            self._build_linkedin_text(profile.linkedin_url)
        )

        self.query_one("#github_value", Static).update(
            self._build_github_text(profile.github_url)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_edit_name":
            self.app.push_screen(EditNameView(self.user_id))

        elif event.button.id == "button_change_password":
            self.app.push_screen(ChangePasswordView(self.user_id))

        elif event.button.id == "button_change_interests":
            self.app.push_screen(ChangeInterestView(self.user_id))

        elif event.button.id == "button_delete_account":
            self.app.push_screen(DeleteAccountView(self.user_id))

        elif event.button.id == "button_back":
            self.app.pop_screen()