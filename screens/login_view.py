from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical, Horizontal

from services.users import login
from services.validations import valid_email, valid_password, password_error_message
from screens.register_view import RegisterView
from screens.main_page_view import MainPageView
from screens.forgot_password_view import ForgotPasswordView
from screens.password_toggle import toggle_password_visibility


AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth-box {
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
    height: 2;
    margin-top: 1;
    color: $warning;
}

#password-row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#password-row Input {
    width: 1fr;
    margin-top: 0;
}

#toggle_password {
    width: 12;
    min-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#password-row Button {
    margin-top: 0;
}
"""

# Tela de autenticação do sistema
class LoginView(Screen):
    CSS = AUTH_CSS

    # Monta a interface de login com campos de e-mail e senha
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth-box"):
                yield Static("Conecta++", id="title")
                yield Static("Faça login para continuar", classes="subtitle")

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

                yield Label("", id="message")

                yield Button("Entrar", id="button_login", variant="primary")
                yield Button("Esqueci minha senha", id="button_forgot_password")
                yield Button("Cadastrar", id="button_register_view")

    # Limpa os campos do formulário e remove estados visuais de erro
    def reset_form(self) -> None:
        email_input = self.query_one("#email", Input)
        password_input = self.query_one("#password", Input)
        message_label = self.query_one("#message", Label)

        email_input.value = ""
        password_input.value = ""

        email_input.remove_class("invalid")
        password_input.remove_class("invalid")

        message_label.update("")
        email_input.focus()    

    # Aplica ou remove a classe visual do campo inválido
    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    # Valida o campo de senha em tempo real
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

    # Dispara a validação adequada sempre que um campo é alterado
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "email":
            self._validate_email_field()
        elif event.input.id == "password":
            self._validate_password_field()

    # Trata as ações de tela de login, incluindo autenticação e navegação
    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Label)

        if event.button.id == "toggle_password":
            toggle_password_visibility(self, "password", "toggle_password")
            return

        if event.button.id == "button_login":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value

            success, message, name, user_id = login(email, password)

            if success:
                self.app.push_screen(MainPageView(user_id, name))
            else:
                response.update(message)

        elif event.button.id == "button_forgot_password":
            self.app.push_screen(ForgotPasswordView())

        elif event.button.id == "button_register_view":
            self.app.push_screen(RegisterView())