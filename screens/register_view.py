from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical
from database import register
from validations import valid_name, valid_email, valid_password, valid_recovery_word

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


class RegisterView(Screen):
    CSS = AUTH_CSS

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth-box"):
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

                yield Input(
                    placeholder="Digite sua senha...",
                    id="password",
                    password=True
                )

                yield Input(
                    placeholder="Confirme sua senha...",
                    id="re_password",
                    password=True
                )

                yield Input(
                    placeholder="Digite sua palavra de recuperação...",
                    id="recovery_word"
                )

                yield Label("", id="message")

                yield Button("Cadastrar", id="button_register", variant="primary")
                yield Button("Voltar", id="button_back")

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

        self._set_invalid_if_needed(name_input, len(value) < 3)

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

    def _validate_recovery_word_field(self) -> None:
        recovery_word_input = self.query_one("#recovery_word", Input)
        value = recovery_word_input.value.strip()

        if not value:
            recovery_word_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(
            recovery_word_input,
            not valid_recovery_word(value)
        )

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

        elif event.input.id == "recovery_word":
            self._validate_recovery_word_field()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Label)

        if event.button.id == "button_register":
            name = self.query_one("#name", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            re_password = self.query_one("#re_password", Input).value
            recovery_word = self.query_one("#recovery_word", Input).value

            if password != re_password:
                response.update("As senhas não coincidem.")
                self.query_one("#re_password", Input).add_class("invalid")
                return

            success, message = register(name, email, password, recovery_word)
            response.update(message)

            if success:
                self.app.pop_screen()

        elif event.button.id == "button_back":
            self.app.pop_screen()
