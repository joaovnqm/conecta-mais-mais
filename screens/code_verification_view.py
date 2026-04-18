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

"""
Bloco de estilo da tela de verificação de código.
Define o alinhamento da tela, aparência da caixa central, campos de entrada, botões, mensagens e linhas de senha.
"""
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

"""
Classe responsável pela tela de verificação de código. Ela é usada em dois fluxos: verificação de e-mail no cadastrado e verificação de código para redefinir senha
"""


class CodeVerificationView(Screen):
    # Aplica o CSS acima nesta tela
    CSS = AUTH_CSS

    """
    Função construtora da tela.
        1. Recebe o modo de uso da tela 'register' ou 'reset_password'
        2. Recebe e padroniza o e-mail
        3. Guarda os dados temporariamente do cadastro
        4. Define se o código já foi validado ou não
    """

    def __init__(
        self,
        mode: str,
        email: str,
        pending_name: str | None = None,
        pending_password: str | None = None,
        verified: bool = False,
    ):
        super().__init__()
        self.mode = mode
        self.email = email.strip().lower()
        self.pending_name = pending_name
        self.pending_password = pending_password
        self.verified = verified

    """
    Função que monta os componentes visuais da tela.
        1. Exibe o título e subtítulo conforme o modo da tela
        2. Se o código ainda não foi validado, mostra o campo para digitar o código
        3. Exibe botões para validar, reenviar o código e voltar
        4. Se o código foi validado, mostra campos para nova senha e confirmar a senha
        5. Exibe o botão par alterar a senha e botão para voltar
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):

                # Tela de cadastro
                if self.mode == "register":
                    yield Static("Verificar e-mail", id="title")
                    yield Static(
                        f"Digite o código enviado para {self.email}.",
                        classes="subtitle"
                    )

                # Tela de nova senha e confirmação
                elif self.verified:
                    yield Static("Nova senha", id="title")
                    yield Static(
                        f"Código validado para {self.email}. Agora defina sua nova senha.",
                        classes="subtitle"
                    )

                # Tela para verificar o código
                else:
                    yield Static("Verificar código", id="title")
                    yield Static(
                        f"Digite o código enviado para {self.email}.",
                        classes="subtitle"
                    )

                # Se o código não foi validado, mostra os componentes de verificação
                if not self.verified:
                    yield Input(
                        placeholder="Digite o código recebido...",
                        id="code"
                    )
                    # Área para mensagens de erro ou sucesso
                    yield Static("", id="message")

                    # Botões de ação para o código
                    yield Button("Validar código", id="button_verify_code", variant="primary")
                    yield Button("Reenviar código", id="button_resend_code")
                    yield Button("Voltar", id="button_back")

                # Se o código já foi validado, mostra os campos para alterar a senha
                else:
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

                    # Área para mensagens de erro ou sucesso
                    yield Static("", id="message")

                    # Botões de ação para alteração de senha
                    yield Button("Alterar senha", id="button_change_password", variant="primary")
                    yield Button("Voltar", id="button_back")

    """
    Função auxiliadora para mostrar ou ocultar senha.
        1. Localiza o campo input pelo id
        2. Localiza o botão correspondente pelo id
        3. Alterna entre ocultar e exibir a senha
        4. Atualiza o texto do botão
    """

    def _toggle_password_visibility(self, input_id: str, button_id: str) -> None:
        # Campo de senha
        password_input = self.query_one(f"#{input_id}", Input)

        # Botão que controla a visibilidade
        toggle_button = self.query_one(f"#{button_id}", Button)

        # Inverte o estado de exibição da senha
        password_input.password = not password_input.password

        # Atualiza o texto do botão
        toggle_button.label = "Mostrar" if password_input.password else "Ocultar"

    """
    Função auxiliadora para mostrar ou ocultar a confirmação da senha
        1. campo de confirmação da senha
        2. alterna entre ocultar e exibir senha
        3. Atualiza o texto do botão
    """

    def _toggle_confirm_password_visibility(self) -> None:
        # Campo de confirmação da senha
        confirm_input = self.query_one("#confirm_password", Input)

        # Botão que controla a visibilidade da confirmação
        toggle_button = self.query_one("#toggle_confirm_password", Button)

        # Inverte o estado de exibição da senha
        confirm_input.password = not confirm_input.password

        # Atualiza o texto do botão
        toggle_button.label = "Mostrar" if confirm_input.password else "Ocultar"

    """
    Função que trata os cliques dos botões da tela.
        1. Alterna visibilidade das senhas, se necessário
        2. Reenvia o código de verificação, se solicitado
        3. Valida o código digitado
        4. Se for cadastro, finaliza o registro do usuário
        5. Se for redefinição de senha, abre a tela para digitar a nova senha
        6. Altera a senha quando o usuário confirmar a nova senha
        7. Volta para a tela anterior quando clicar em voltar
    """

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Mostra a mensagem ao usuário
        response = self.query_one("#message", Static)

        # Alterna a visibilidade do campo da nova senha
        if event.button.id == "toggle_password":
            self._toggle_password_visibility("new_password", "toggle_password")
            return

        # Alterna a visibilidade do campo de confirmação da senha
        if event.button.id == "toggle_confirm_password":
            self._toggle_confirm_password_visibility(
                "confirm_password", "toggle_confirm_password")
            return

        # Reenvia o código de verificação
        if event.button.id == "button_resend_code":

            # Se for fluxo de cadastro, solicita novo código
            if self.mode == "register":
                success, message = request_registration_code(self.email)
            # Caso contrário, solicita novo código de redefinição de senha
            else:
                success, message = request_password_reset(self.email)
            response.update(message)
            return

        # Valida o código digitado pelo usuário
        if event.button.id == "button_verify_code":
            # Salva o valor digitado no campo de código
            code = self.query_one("#code", Input).value

            # Verifica se o campo está vazio
            if not code.strip():
                response.update("Digite o código recebido.")
                return

            # Define a finalidade do código, dependendo da tela
            purpose = "register" if self.mode == "register" else "reset_password"

            # Chama a função de verificação do código
            success, message = verify_code(self.email, code, purpose)
            response.update(message)

            # Se o código estiver correto
            if success:
                if self.mode == "register":
                    success_register, register_message, user_id = register(
                        self.pending_name or "",
                        self.email,
                        self.pending_password or ""
                    )
                    response.update(register_message)

                    # Se o cadastro for concluído com sucesso, vai para a tela de interesses
                    if success_register:
                        self.notify("E-mail verificado com sucesso.")
                        self.app.push_screen(
                            InterestsView(user_id, self.pending_name or "")
                        )
                # Se for fluxo de redefinição, abre a próxima etapa para criar nova senha
                else:
                    self.app.push_screen(
                        CodeVerificationView(
                            mode="reset_password",
                            email=self.email,
                            verified=True
                        )
                    )
            return

        # Altera a senha após o código já ter sido validado
        if event.button.id == "button_change_password":
            # Salva os valores digitados
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value

            # Verifica se a nova senha e a confirmação de senha estão iguais
            if new_password != confirm_password:
                response.update("As senhas não coincidem.")
                return

            # Finaliza a redefinição de senha
            success, message = finalize_password_reset(
                self.email, new_password)
            response.update(message)

            # Se a alteração de certo
            if success:
                self.notify("Senha alterada com sucesso. Faça login.")

                # Fecha as telas empilhadas até retornar o login
                for _ in range(3):
                    self.app.pop_screen()

                # Verifica se a tela atual possui método para limpar os campos
                current_screen = self.app.screen
                if hasattr(current_screen, "reset_form"):
                    current_screen.reset_form()
            return

        # Voltar para a tela anterior.
        if event.button.id == "button_back":
            self.app.pop_screen()
