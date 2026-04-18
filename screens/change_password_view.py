from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal

from services.users import change_user_password

AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth_box {
    width: 58;
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

#message {
    width: 100%;
    height: auto;
    min-height: 1;
    margin-top: 1;
    color: $warning;
}

#current-password-row,
#new-password-row,
#confirm-password-row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#current-password-row Input,
#new-password-row Input,
#confirm-password-row Input {
    width: 1fr;
    margin-top: 0;
}

#toggle_current_password,
#toggle_new_password,
#toggle_confirm_password {
    width: 12;
    min-width: 12;
    max-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#current-password-row Button,
#new-password-row Button,
#confirm-password-row Button {
    width: 12;
    min-width: 12;
    max-width: 12;
    margin-top: 0;
}

.action_button {
    width: 100%;
    margin-top: 1;
}

#button_back {
    margin-top: 0;
}
"""

# Tela responsável pela alteração da senha do usuário
class ChangePasswordView(Screen):

    CSS = AUTH_CSS
    
    # Inicializa a tela com identificador do usuário autenticado.
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface da tela de alteração da senha
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Atualizar senha", id="title")
                yield Static(
                    "Digite sua senha atual e depois defina a nova senha",
                    classes="subtitle"
                )
                with Horizontal(id="current-password-row"):
                    yield Input(
                        placeholder="Digite sua senha atual...",
                        id="current_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_current_password")
                with Horizontal(id="new-password-row"):
                    yield Input(
                        placeholder="Digite a sua nova senha...",
                        id="new_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_new_password")
                with Horizontal(id="confirm-password-row"):
                    yield Input(
                        placeholder="Confirme a nova senha...",
                        id="confirm_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_confirm_password")
                yield Static("", id="message")
                yield Button(
                    "Salvar",
                    id="button_save",
                    variant="primary",
                    classes="action_button"
                )
                yield Button(
                    "Voltar",
                    id="button_back",
                    variant="error",
                    classes="action_button"
                )
                
    # Alterna a visiblidade do campo da senha e atualiza o texto do botão
    def _toggle_visibility(self, input_id: str, button_id: str) -> None:
        password_input = self.query_one(f"#{input_id}", Input)
        toggle_button = self.query_one(f"#{button_id}", Button)

        password_input.password = not password_input.password
        toggle_button.label = "Mostrar" if password_input.password else "Ocultar"

    """
        Trata os cliques dos botões da tela
        - Alternar a visibilidade dos campos da senha;
        - Validar a confirmação da nova senha;
        - Solicitar a alteração da senha;
        - Retorna para a tela anterior quando necessário.    
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:
        response = self.query_one("#message", Static)
        
        if event.button.id == "toggle_current_password":
            self._toggle_visibility(
                "current_password", "toggle_current_password")
            return

        if event.button.id == "toggle_new_password":
            self._toggle_visibility("new_password", "toggle_new_password")
            return

        if event.button.id == "toggle_confirm_password":
            self._toggle_visibility(
                "confirm_password", "toggle_confirm_password")
            return

        if event.button.id == "button_save":
            current_password = self.query_one("#current_password", Input).value
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value

            if new_password != confirm_password:
                response.update("As senhas não coincidem.")
                return

            success, message = change_user_password(
                self.user_id,
                current_password,
                new_password
            )
            response.update(message)

            if success:
                self.notify("Senha alterada com sucesso.")
                self.app.pop_screen()

        elif event.button.id == "button_back":
            self.app.pop_screen()
