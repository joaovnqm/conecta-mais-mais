from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal

from services.password_reset import password_reset_service
from utils.validations import validation_services
from screens.auth.code_verification_view import CodeVerificationView
from utils.password_toggle import password_toggle_service


AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth_box {
    width: 86;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

Input {
    width: 100%;
    margin-top: 1;
}

Input.invalid {
    border: tall $error;
}

Button {
    width: 100%;
    margin-top: 1;
}

#message {
    width: 100%;
    height: auto;
    min-height: 1;
    margin-top: 1;
    color: $warning;
}

#password-row,
#re-password-row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#password-row Input,
#re-password-row Input {
    width: 1fr;
    margin-top: 0;
}

#toggle_password,
#toggle_re_password {
    width: 12;
    min-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#password-row Button,
#re-password-row Button {
    margin-top: 0;
}
"""


class RegisterView(Screen):
    """
    Classe responsável pela tela de registro de novos usuários.
    """

    CSS = AUTH_CSS

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Conecta++", id="title")
                yield Static("Crie sua conta", classes="subtitle")

                yield Input(placeholder="Digite seu nome...", id="name")
                yield Input(placeholder="Digite seu e-mail...", id="email")
                yield Input(placeholder="Crie seu username. Ex: fulano.dev", id="username")
                yield Input(
                    placeholder="LinkedIn opcional. Ex: https://www.linkedin.com/in/seu-perfil",
                    id="linkedin_url"
                )

                with Horizontal(id="password-row"):
                    yield Input(
                        placeholder="Digite sua senha...",
                        id="password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_password")

                with Horizontal(id="re-password-row"):
                    yield Input(
                        placeholder="Confirme sua senha...",
                        id="re_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_re_password")

                yield Static("", id="message")
                yield Button("Cadastrar", id="button_register", variant="primary")
                yield Button("Voltar", id="button_back", variant="primary")

    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    def _validate_name_field(self) -> None:
        name_input = self.query_one("#name", Input)
        value = name_input.value.strip()

        if not value:
            name_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            name_input,
            not validation_services.valid_name_users(value)
        )

    def _validate_email_field(self) -> None:
        email_input = self.query_one("#email", Input)
        value = email_input.value.strip()

        if not value:
            email_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            email_input,
            not validation_services.valid_email(value)
        )

    def _validate_username_field(self) -> None:
        username_input = self.query_one("#username", Input)
        value = username_input.value.strip()

        if not value:
            username_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            username_input,
            not validation_services.valid_username(value)
        )

    def _validate_linkedin_field(self) -> None:
        linkedin_input = self.query_one("#linkedin_url", Input)
        value = linkedin_input.value.strip()

        if not value:
            linkedin_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            linkedin_input,
            not validation_services.valid_linkedin_url(value)
        )

    def _validate_password_field(self) -> None:
        password_input = self.query_one("#password", Input)
        value = password_input.value

        if not value:
            password_input.remove_class("invalid")
            return

        error_message = validation_services.password_error_message(value)

        self._set_invalid_if_needed(
            password_input,
            error_message is not None
        )

    def _validate_re_password_field(self) -> None:
        password_input = self.query_one("#password", Input)
        re_password_input = self.query_one("#re_password", Input)

        password_value = password_input.value
        re_password_value = re_password_input.value

        if not re_password_value:
            re_password_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            re_password_input,
            re_password_value != password_value
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "name":
            self._validate_name_field()

        elif event.input.id == "email":
            self._validate_email_field()

        elif event.input.id == "username":
            self._validate_username_field()

        elif event.input.id == "linkedin_url":
            self._validate_linkedin_field()

        elif event.input.id == "password":
            self._validate_password_field()
            self._validate_re_password_field()

        elif event.input.id == "re_password":
            self._validate_re_password_field()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Static)

        if event.button.id == "toggle_password":
            password_toggle_service.toggle_password_visibility(
                self,
                "password",
                "toggle_password"
            )
            return

        if event.button.id == "toggle_re_password":
            password_toggle_service.toggle_password_visibility(
                self,
                "re_password",
                "toggle_re_password"
            )
            return

        if event.button.id == "button_register":
            self._handle_register(response)
            return

        if event.button.id == "button_back":
            self.app.pop_screen()
            return

    def _handle_register(self, response: Static) -> None:
        name_input = self.query_one("#name", Input)
        email_input = self.query_one("#email", Input)
        username_input = self.query_one("#username", Input)
        linkedin_input = self.query_one("#linkedin_url", Input)
        password_input = self.query_one("#password", Input)
        re_password_input = self.query_one("#re_password", Input)

        name = name_input.value
        email = email_input.value
        username = username_input.value
        linkedin_url = linkedin_input.value
        password = password_input.value
        re_password = re_password_input.value

        if not validation_services.valid_name_users(name):
            response.update(
                "O nome precisa ter pelo menos 2 caracteres e não pode conter números."
            )
            name_input.add_class("invalid")
            return

        if not validation_services.valid_email(email):
            response.update("Esse e-mail é inválido.")
            email_input.add_class("invalid")
            return

        if not validation_services.valid_username(username):
            response.update(
                "O username é obrigatório e precisa ter entre 3 e 20 caracteres. Use apenas letras, números, ponto ou underline."
            )
            username_input.add_class("invalid")
            return

        if not validation_services.valid_linkedin_url(linkedin_url):
            response.update(
                "O LinkedIn precisa estar no formato https://www.linkedin.com/in/seu-perfil"
            )
            linkedin_input.add_class("invalid")
            return

        password_message = validation_services.password_error_message(password)

        if password_message is not None:
            response.update(password_message)
            password_input.add_class("invalid")
            return

        if password != re_password:
            response.update("As senhas não coincidem.")
            re_password_input.add_class("invalid")
            return

        success, message = password_reset_service.request_registration_code(email)
        response.update(message)

        if success:
            self.app.push_screen(
                CodeVerificationView(
                    mode="register",
                    email=email,
                    pending_name=name,
                    pending_password=password,
                    pending_username=username,
                    pending_linkedin_url=linkedin_url
                )
            )