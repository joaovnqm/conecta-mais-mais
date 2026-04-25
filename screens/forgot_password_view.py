from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical

from services.password_reset import request_password_reset
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
"""

class ForgotPasswordView(Screen):
    """
    Classe responsável pela tela de recuperação de senha. Ela é acessada a partir da tela de login, e permite que o usuário
    solicite o envio de um código de recuperação para o e-mail associado à sua conta.
    """
    CSS = AUTH_CSS
    
    # Monta a interface para envio do código de recuperação por e-mail
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Recuperar senha", id="title")
                yield Static("Digite seu e-mail para receber o código.", classes="subtitle")

                yield Input(
                    placeholder="Digite seu e-mail...",
                    id="email"
                )

                yield Label("", id="message")

                yield Button("Enviar código", id="button_send_code", variant="primary")
                yield Button("Voltar", id="button_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
        e executa a ação correspondente:
        - Se for o botão de enviar código, ela coleta o e-mail digitado, chama a função de solicitação de recuperação de senha,
          e exibe a mensagem de resposta. Se a solicitação for bem-sucedida, ela navega para a tela de verificação de código.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        response = self.query_one("#message", Label)

        if event.button.id == "button_send_code":
            email = self.query_one("#email", Input).value

            success, message = request_password_reset(email)
            response.update(message)

            if success:
                self.app.push_screen(
                    CodeVerificationView(
                        mode="reset_password",
                        email=email
                    )
                )

        elif event.button.id == "button_back":
            self.app.pop_screen()