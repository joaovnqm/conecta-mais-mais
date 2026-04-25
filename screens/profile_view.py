from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical

from services.users import get_user_profile
from screens.edit_name_view import EditNameView
from screens.change_password_view import ChangePasswordView
from screens.delete_account_view import DeleteAccountView

PROFILE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#profile_box {
    width: 60;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#profile_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.profile_label {
    margin-top: 1;
    text-style: bold;
}

.profile_value {
    color: $text-muted;
    margin-bottom: 1;
}

.profile_action {
    width: 22;
    margin-top: 1;
}

#button_delete_account {
    width: 100%;
    margin-top: 2;
}

#button_back {
    width: 100%;
    margin-top: 1;
}
"""

class ProfileView(Screen):
    """
    Classe responsável pela tela de perfil do usuário. Ela exibe as informações do perfil, como nome e e-mail, e oferece opções para
    atualizar o nome, atualizar a senha, deletar a conta ou voltar para a tela anterior. 
    """
    CSS = PROFILE_CSS

    # Inicializa a tela com o usuário que terá o perfil exibido
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com os dados do perfil e as ações disponíveis
    def compose(self) -> ComposeResult:
        profile = get_user_profile(self.user_id)

        with Center():
            with Vertical(id="profile_box"):
                yield Static("Meu perfil", id="profile_title")

                if profile is None:
                    yield Static("Usuário não encontrado.", id="name_value", classes="profile_value")
                else:
                    yield Static("Nome:", classes="profile_label")
                    yield Static(profile["name"], id="name_value", classes="profile_value")
                    yield Button("Atualizar nome", id="button_edit_name", classes="profile_action")

                    yield Static("Senha:", classes="profile_label")
                    yield Button("Atualizar senha", id="button_change_password", classes="profile_action")

                    yield Static("E-mail:", classes="profile_label")
                    yield Static(profile["email"], id="email_value", classes="profile_value")

                    yield Button(
                        "Deletar conta",
                        id="button_delete_account",
                        variant="error"
                    )

                yield Button("Voltar", id="button_back", variant="error")

    def reload_profile(self) -> None:
        """
        Função para recarregar os dados do perfil na interface. Ela é chamada após ações que podem alterar as informações do perfil, como
        atualizar o nome ou a senha, para garantir que as informações exibidas estejam sempre atualizadas.
        """
        profile = get_user_profile(self.user_id)
        if profile is None:
            return

        self.query_one("#name_value", Static).update(profile["name"])
        self.query_one("#email_value", Static).update(profile["email"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela de perfil. Ela verifica qual botão foi clicado, e executa a ação
        correspondente:
        - Se for o botão de atualizar nome, ela navega para a tela de edição de nome.
        - Se for o botão de atualizar senha, ela navega para a tela de alteração de senha.
        - Se for o botão de deletar conta, ela navega para a tela de confirmação de exclusão de conta.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        if event.button.id == "button_edit_name":
            self.app.push_screen(EditNameView(self.user_id))

        elif event.button.id == "button_change_password":
            self.app.push_screen(ChangePasswordView(self.user_id))

        elif event.button.id == "button_delete_account":
            self.app.push_screen(DeleteAccountView(self.user_id))

        elif event.button.id == "button_back":
            self.app.pop_screen()
