from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical
from services.users import login
from services.validations import valid_email, valid_password
from screens.register_view import RegisterView
from screens.main_page_view import MainPageView


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
"""


class LoginView(Screen):
    CSS = AUTH_CSS

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth-box"):
                yield Static("Conecta++", id="title")
                yield Static("Faça login para continuar", classes="subtitle")

                yield Input(
                    placeholder="Digite seu e-mail...",
                    id="email"
                )

                yield Input(
                    placeholder="Digite sua senha...",
                    id="password",
                    password=True
                )

                yield Label("", id="message")

                yield Button("Entrar", id="button_login", variant="primary")
                yield Button("Cadastrar", id="button_register_view")

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

    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    def _validate_email_field(self) -> None:
        email_input = self.query_one("#email", Input)
        value = email_input.value.strip()

        if not value:
            email_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(email_input, not valid_email(value))

    def _validate_password_field(self) -> None:
        password_input = self.query_one("#password", Input)
        value = password_input.value

        if not value:
            password_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(password_input, not valid_password(value))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "email":
            self._validate_email_field()
        elif event.input.id == "password":
            self._validate_password_field()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Label)

        if event.button.id == "button_login":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value

            success, message, name, user_id = login(email, password)

            if success:
                self.app.push_screen(MainPageView(user_id, name))
            else:
                response.update(message)

        elif event.button.id == "button_register_view":
            self.app.push_screen(RegisterView())