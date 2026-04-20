from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical, Horizontal

from services.password_reset import reset_password
from screens.password_toggle import toggle_password_visibility


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
#confirm-password-row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#password-row Input,
#confirm-password-row Input {
    width: 1fr;
    margin-top: 0;
}

#toggle_password,
#toggle_confirm_password {
    width: 12;
    min-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#password-row Button,
#confirm-password-row Button {
    margin-top: 0;
}
"""

# Tela de redefinição de senha a partir do código enviado por e-mail
class ResetPasswordView(Screen):
    CSS = AUTH_CSS

    # Inicializa a tela com um e-mail opcionalmente preenchido
    def __init__(self, email: str = ""):
        super().__init__()
        self.initial_email = email

    # Monta a interface de redefinição de senha com o código e nova credencial
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Redefinir senha", id="title")
                yield Static(
                    "Digite o código recebido e a nova senha.",
                    classes="subtitle"
                )

                yield Input(
                    placeholder="Digite seu e-mail...",
                    id="email",
                    value=self.initial_email
                )

                yield Input(
                    placeholder="Digite o código recebido...",
                    id="code"
                )

                with Horizontal(id="password-row"):
                    yield Input(
                        placeholder="Digite a nova senha...",
                        id="new_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_password")

                with Horizontal(id="confirm-password-row"):
                    yield Input(
                        placeholder="Confirme a nova senha...",
                        id="confirm_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_confirm_password")

                yield Label("", id="message")

                yield Button(
                    "Alterar senha",
                    id="button_reset_password",
                    variant="primary"
                )
                yield Button("Voltar", id="button_back")
    
    # Processa redefinição de senha e controla a navegação de tela
    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Label)

        if event.button.id == "toggle_password":
            toggle_password_visibility(self, "new_password", "toggle_password")
            return

        if event.button.id == "toggle_confirm_password":
            toggle_password_visibility(self, "confirm_password", "toggle_confirm_password")
            return

        if event.button.id == "button_reset_password":
            email = self.query_one("#email", Input).value
            code = self.query_one("#code", Input).value
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value

            if new_password != confirm_password:
                response.update("As senhas não coincidem.")
                return

            success, message = reset_password(email, code, new_password)
            response.update(message)

            if success:
                self.notify("Senha alterada com sucesso. Faça login.")
                self.app.pop_screen()
                self.app.pop_screen()

                current_screen = self.app.screen
                if hasattr(current_screen, "reset_form"):
                    current_screen.reset_form()

        elif event.button.id == "button_back":
            self.app.pop_screen()