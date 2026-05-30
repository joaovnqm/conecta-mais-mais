from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll, Vertical

from database.repositories.user_repository import user_services
from utils.validations import validation_services


EDIT_PROFILE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#edit_box {
    width: 90;
    height: 40;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#title {
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

.section_hint {
    color: $text-muted;
    margin-bottom: 1;
}

.field_label {
    margin-top: 1;
    text-style: bold;
}

Input {
    width: 100%;
    margin-top: 1;
}

Input.invalid {
    border: tall $error;
}

#message {
    width: 100%;
    min-height: 1;
    height: auto;
    color: $warning;
    margin-top: 1;
    content-align: center middle;
}

.action_button {
    width: 100%;
    margin-top: 1;
}

#button_back {
    width: 100%;
    margin-top: 1;
}
"""


class EditNameView(Screen):
    """
    Tela responsável por atualizar dados básicos do perfil:
    - nome;
    - username;
    - LinkedIn.
    - GitHub.
    """

    CSS = EDIT_PROFILE_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        profile = user_services.get_user_profile(self.user_id)

        name = ""
        username = ""
        linkedin_url = ""
        github_url = ""
        if profile is not None:
            name = profile.name or ""
            username = profile.username or ""
            linkedin_url = profile.linkedin_url or ""
            github_url = profile.github_url or ""

        with Center():
            with VerticalScroll(id="edit_box"):
                yield Static("Atualizar dados do perfil", id="title")
                yield Static(
                    "Edite seu nome, username e link do LinkedIn.",
                    id="subtitle"
                )

                with Vertical(classes="section_card"):
                    yield Static("Dados pessoais", classes="section_title")
                    yield Static(
                        "Essas informações ajudam outros usuários a reconhecerem você.",
                        classes="section_hint"
                    )

                    yield Static("Nome:", classes="field_label")
                    yield Input(
                        placeholder="Digite o seu nome...",
                        id="new_name",
                        value=name
                    )

                with Vertical(classes="section_card"):
                    yield Static("Dados sociais", classes="section_title")
                    yield Static(
                        "O username é usado para adicionar amigos no Conecta++.",
                        classes="section_hint"
                    )

                    yield Static("Username:", classes="field_label")
                    yield Input(
                        placeholder="Exemplo: wellison.dev",
                        id="username",
                        value=username
                    )

                    yield Static("LinkedIn:", classes="field_label")
                    yield Input(
                        placeholder="Exemplo: https://www.linkedin.com/in/seu-perfil",
                        id="linkedin_url",
                        value=linkedin_url
                    )

                    yield Static("GitHub:", classes="field_label")
                    yield Input(
                        placeholder="Exemplo: https://github.com/seu-username",
                        id="github_url",
                        value=github_url
                    )

                yield Static("", id="message")
                yield Button(
                    "Salvar alterações",
                    id="button_save",
                    variant="primary",
                    classes="action_button"
                )

                yield Button(
                    "Voltar",
                    id="button_back",
                    variant="primary",
                    classes="action_button"
                )

    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "new_name":
            value = event.input.value.strip()

            if not value:
                event.input.remove_class("invalid")
                return

            self._set_invalid_if_needed(
                event.input,
                not validation_services.valid_name_users(value)
            )

        elif event.input.id == "username":
            value = event.input.value.strip()

            if not value:
                event.input.remove_class("invalid")
                return

            self._set_invalid_if_needed(
                event.input,
                not validation_services.valid_username(value)
            )

        elif event.input.id == "linkedin_url":
            value = event.input.value.strip()

            if not value:
                event.input.remove_class("invalid")
                return

            self._set_invalid_if_needed(
                event.input,
                not validation_services.valid_linkedin_url(value)
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Static)

        if event.button.id == "button_save":
            self._handle_save(response)
            return

        if event.button.id == "button_back":
            self.app.pop_screen()
            return

    def _handle_save(self, response: Static) -> None:
        name_input = self.query_one("#new_name", Input)
        username_input = self.query_one("#username", Input)
        linkedin_input = self.query_one("#linkedin_url", Input)
        github_input = self.query_one("#github_url", Input)

        new_name = name_input.value
        username = username_input.value
        linkedin_url = linkedin_input.value
        github_url = github_input.value

        if not validation_services.valid_name_users(new_name):
            name_input.add_class("invalid")
            response.update(
                "O nome precisa ter pelo menos 2 caracteres, no máximo 50 caracteres e não pode conter números."
            )
            return

        if not validation_services.valid_username(username):
            username_input.add_class("invalid")
            response.update(
                "O username é obrigatório e precisa ter entre 3 e 20 caracteres. Use apenas letras, números, ponto ou underline."
            )
            return

        if not validation_services.valid_linkedin_url(linkedin_url):
            linkedin_input.add_class("invalid")
            response.update(
                "O LinkedIn precisa estar no formato https://www.linkedin.com/in/seu-perfil"
            )
            return
        
        if not validation_services.valid_github_url(github_url):
            github_input.add_class("invalid")
            response.update(
                "O GitHub precisa estar no formato https://github.com/seu-username"
            )
            return

        success_name, message_name = user_services.update_user_name(
            self.user_id,
            new_name
        )

        if not success_name:
            name_input.add_class("invalid")
            response.update(message_name)
            return

        success_username, message_username = user_services.update_username(
            self.user_id,
            username
        )

        if not success_username:
            username_input.add_class("invalid")
            response.update(message_username)
            return

        success_linkedin, message_linkedin = user_services.update_linkedin_url(
            self.user_id,
            linkedin_url
        )

        if not success_linkedin:
            linkedin_input.add_class("invalid")
            response.update(message_linkedin)
            return

        success_github, message_github = user_services.update_github_url(
            self.user_id,
            github_url
        )

        if not success_github:
            github_input.add_class("invalid")
            response.update(message_github)
            return

        self.notify("Dados do perfil atualizados com sucesso.")
        self.app.pop_screen()

        current_screen = self.app.screen
        if hasattr(current_screen, "reload_profile"):
            current_screen.reload_profile()