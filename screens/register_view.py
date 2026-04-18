from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal

from services.password_reset import request_registration_code
from services.validations import (
    valid_name_users,
    valid_email,
    password_error_message,
)
from screens.code_verification_view import CodeVerificationView


AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth_box {
    width: 52;
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

# Tela de cadastro de novos usuários
class RegisterView(Screen):
    CSS = AUTH_CSS

    # Monta a interface de cadastro com validação dos dados de entrada
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Conecta++", id="title")
                yield Static("Crie sua conta", classes="subtitle")

                yield Input(
                    placeholder="Digite seu nome...",
                    id="name"
                )

                yield Input(
                    placeholder="Digite seu e-mail...",
                    id="email"
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
                yield Button("Voltar", id="button_back")

    # Aplica ou remove a classe visual de campo inválido
    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    # Valida o campo de nome em tempo real
    def _validate_name_field(self) -> None:
        name_input = self.query_one("#name", Input)
        value = name_input.value.strip()

        if not value:
            name_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(name_input, not valid_name_users(value))
    
    # Valida o campo de e-mail em tempo real
    def _validate_email_field(self) -> None:
        email_input = self.query_one("#email", Input)
        value = email_input.value.strip()

        if not value:
            email_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(email_input, not valid_email(value))
    
    # Valida o campo de senha em tempo real
    def _validate_password_field(self) -> None:
        password_input = self.query_one("#password", Input)
        value = password_input.value

        if not value:
            password_input.remove_class("invalid")
            return

        error_message = password_error_message(value)
        self._set_invalid_if_needed(password_input, error_message is not None)
    
    # Valida o campo de confirmação de senha em tempo real
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
    # Alterna a visibilidade do campo de senha
    def _toggle_password_visibility(self) -> None:
        password_input = self.query_one("#password", Input)
        toggle_button = self.query_one("#toggle_password", Button)

        password_input.password = not password_input.password
        toggle_button.label = "Mostrar" if password_input.password else "Ocultar"
    # Alterna a visibilidade da confirmação de campo de senha
    def _toggle_re_password_visibility(self) -> None:
        re_password_input = self.query_one("#re_password", Input)
        toggle_button = self.query_one("#toggle_re_password", Button)

        re_password_input.password = not re_password_input.password
        toggle_button.label = "Mostrar" if re_password_input.password else "Ocultar"
        
    # Dispara a validação apropriada conforme o campo alterado
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "name":
            self._validate_name_field()

        elif event.input.id == "email":
            self._validate_email_field()

        elif event.input.id == "password":
            self._validate_password_field()
            self._validate_re_password_field()

        elif event.input.id == "re_password":
            self._validate_re_password_field()

    # Trata o fluxo de cadastro, incluindo validações e envio do código de verificação
    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Static)

        if event.button.id == "toggle_password":
            self._toggle_password_visibility()
            return

        if event.button.id == "toggle_re_password":
            self._toggle_re_password_visibility()
            return

        if event.button.id == "button_register":
            name = self.query_one("#name", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            re_password = self.query_one("#re_password", Input).value

            if not valid_name_users(name):
                response.update("O nome precisa ter pelo menos 2 caracteres e não pode conter números.")
                self.query_one("#name", Input).add_class("invalid")
                return

            if not valid_email(email):
                response.update("Esse e-mail é inválido!")
                self.query_one("#email", Input).add_class("invalid")
                return

            password_message = password_error_message(password)
            if password_message is not None:
                response.update(password_message)
                self.query_one("#password", Input).add_class("invalid")
                return

            if password != re_password:
                response.update("As senhas não coincidem.")
                self.query_one("#re_password", Input).add_class("invalid")
                return

            success, message = request_registration_code(email)
            response.update(message)

            if success:
                self.app.push_screen(
                    CodeVerificationView(
                        mode="register",
                        email=email,
                        pending_name=name,
                        pending_password=password
                    )
                )

        elif event.button.id == "button_back":
            self.app.pop_screen()