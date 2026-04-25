from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal

from services.password_reset import (
    request_registration_code,
    request_password_reset,
    verify_code,
    finalize_password_reset,
)
from services.users import register
from screens.interests_view import InterestsView
from services.password_toggle import toggle_password_visibility

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
    content-align: left middle;
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
    min-width: 20;
    margin-top: 0;
}

#toggle_password,
#toggle_confirm_password {
    width: 12;
    min-width: 12;
    max-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#password-row Button,
#confirm-password-row Button {
    width: 12;
    min-width: 12;
    max-width: 12;
    margin-top: 0;
}
"""



class CodeVerificationView(Screen):
    """
    Classe responsável pela tela de verificação de código. Ela é usada em dois fluxos: verificação de e-mail no cadastrado e verificação de código para redefinir senha
    """
    CSS = AUTH_CSS

    # Inicializa a tela de verificação.
    def __init__(self, mode: str, email: str, pending_name: str | None = None, pending_password: str | None = None, verified: bool = False,):
        super().__init__()
        self.mode = mode
        self.email = email.strip().lower()
        self.pending_name = pending_name
        self.pending_password = pending_password
        self.verified = verified
    
    # Monta a interface de acordo com estado atual do fluxo
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                if self.mode == "register":
                    yield Static("Verificar e-mail", id="title")
                    yield Static(f"Digite o código enviado para {self.email}.", classes="subtitle")
                elif self.verified:
                    yield Static("Nova senha", id="title")
                    yield Static(f"Código validado para {self.email}. Agora defina sua nova senha.", classes="subtitle")
                else:
                    yield Static("Verificar código", id="title")
                    yield Static(f"Digite o código enviado para {self.email}.", classes="subtitle")
                if not self.verified:
                    yield Input(placeholder="Digite o código recebido...", id="code")
                    yield Static("", id="message")
                    yield Button("Validar código", id="button_verify_code", variant="primary")
                    yield Button("Reenviar código", id="button_resend_code")
                    yield Button("Voltar", id="button_back")
                else:
                    with Horizontal(id="password-row"):
                        yield Input(placeholder="Digite a nova senha...", id="new_password", password=True)
                        yield Button("Mostrar", id="toggle_password")

                    with Horizontal(id="confirm-password-row"):
                        yield Input(placeholder="Confirme a nova senha...", id="confirm_password", password=True)
                        yield Button("Mostrar", id="toggle_confirm_password")

                    yield Static("", id="message")
                    yield Button("Alterar senha", id="button_change_password", variant="primary")
                    yield Button("Voltar", id="button_back", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado, 
        e executa a ação correspondente:
        - Se for um botão de toggle, ela chama a função toggle_password_visibility para alternar a visibilidade da senha.
        - Se for o botão de validar código, ela coleta o código digitado, verifica se ele é válido para o e-mail e a finalidade 
        (registro ou redefinição de senha), e atualiza a interface de acordo com o resultado da verificação.
        - Se for o botão de reenviar código, ela chama a função correspondente para solicitar um novo código, 
        e atualiza a mensagem de resposta.
        - Se for o botão de alterar senha, ela coleta os valores dos campos de nova senha e confirmação, verifica se coincidem,
        e chama a função finalize_password_reset para tentar alterar a senha, atualizando a mensagem de resposta com o resultado.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        response = self.query_one("#message", Static)

        if event.button.id == "toggle_password":
            toggle_password_visibility(self, "new_password", "toggle_password")
            return

        if event.button.id == "toggle_confirm_password":
            toggle_password_visibility(self, "confirm_password", "toggle_confirm_password")
            return

        if event.button.id == "button_resend_code":
            if self.mode == "register":
                success, message = request_registration_code(self.email)
            else:
                success, message = request_password_reset(self.email)
            response.update(message)
            return

        if event.button.id == "button_verify_code":
            code = self.query_one("#code", Input).value

            if not code.strip():
                response.update("Digite o código recebido.")
                return

            purpose = "register" if self.mode == "register" else "reset_password"

            success, message = verify_code(self.email, code, purpose)
            response.update(message)

            if success:
                if self.mode == "register":
                    success_register, register_message, user_id = register(
                        self.pending_name or "",
                        self.email,
                        self.pending_password or ""
                    )
                    response.update(register_message)

                    if success_register:
                        self.notify("E-mail verificado com sucesso.")
                        self.app.push_screen(
                            InterestsView(user_id, self.pending_name or "")
                        )
                else:
                    self.app.push_screen(
                        CodeVerificationView(
                            mode="reset_password",
                            email=self.email,
                            verified=True
                        )
                    )
            return

        if event.button.id == "button_change_password":
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value

            if new_password != confirm_password:
                response.update("As senhas não coincidem.")
                return

            success, message = finalize_password_reset(
                self.email, new_password)
            response.update(message)

            if success:
                self.notify("Senha alterada com sucesso. Faça login.")

                for _ in range(3):
                    self.app.pop_screen()

                current_screen = self.app.screen
                if hasattr(current_screen, "reset_form"):
                    current_screen.reset_form()
            return
        
        if event.button.id == "button_back":
            self.app.pop_screen()