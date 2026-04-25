from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal
from services.users import change_user_password
from services.password_toggle import toggle_password_visibility

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

class ChangePasswordView(Screen):
    """
    Classe responsável pela tela de alteração de senha. Ela é acessada a partir da tela de perfil, e permite que o usuário 
    altere sua senha atual para uma nova senha, seguindo os critérios de segurança definidos. A tela inclui campos para a senha 
    atual, a nova senha e a confirmação da nova senha, além de botões para salvar as alterações ou voltar para a tela anterior. 
    A função on_button_pressed lida com os eventos de clique nos botões, realizando as ações correspondentes e exibindo mensagens 
    de erro ou sucesso conforme necessário.
    """

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
                yield Static("Digite sua senha atual e depois defina a nova senha", classes="subtitle")
                with Horizontal(id="current-password-row"):
                    yield Input(placeholder="Digite sua senha atual...", id="current_password", password=True)
                    yield Button("Mostrar", id="toggle_current_password")

                with Horizontal(id="new-password-row"):
                    yield Input(placeholder="Digite a sua nova senha...", id="new_password", password=True)
                    yield Button("Mostrar", id="toggle_new_password")

                with Horizontal(id="confirm-password-row"):
                    yield Input(placeholder="Confirme a nova senha...", id="confirm_password", password=True)
                    yield Button("Mostrar", id="toggle_confirm_password")

                yield Static("", id="message")
                yield Button("Salvar", id="button_save", classes="action_button")
                yield Button("Voltar", id="button_back", variant="primary", classes="action_button")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado, 
        e executa a ação correspondente:
        - Se for um botão de toggle, ela chama a função toggle_password_visibility para alternar a visibilidade da senha.
        - Se for o botão de salvar, ela coleta os valores dos campos de senha, verifica se a nova senha e a confirmação coincidem,
        e chama a função change_user_password para tentar alterar a senha.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        A função também atualiza a mensagem de resposta com base no resultado da tentativa de alteração de senha, 
        exibindo mensagens de erro específicas para cada tipo de erro, ou uma mensagem de sucesso se a alteração for bem-sucedida.
        """
        response = self.query_one("#message", Static)
        
        if event.button.id == "toggle_current_password":
            toggle_password_visibility(self, "current_password", "toggle_current_password")
            return

        if event.button.id == "toggle_new_password":
            toggle_password_visibility(self, "new_password", "toggle_new_password")
            return

        if event.button.id == "toggle_confirm_password":
            toggle_password_visibility(self, "confirm_password", "toggle_confirm_password")
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
