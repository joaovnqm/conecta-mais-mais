from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical

from services.users import delete_user_account

AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#confirm_box {
    width: 56;
    height: auto;
    border: round $error;
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

Button {
    width: 100%;
    margin-top: 1;
}
"""

"""
Classe responsável pela tela de confirmação de exclusão da conta.
Ela exibe uma mensagem perguntando se o usuário realmente deseja deletar a conta, com opções para confirmar ou cancelar.
"""
class DeleteAccountView(Screen):
    CSS = AUTH_CSS
    
    # Inicializa a tela com usuário que poderá ser removido
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
    
    # Monta a interface de confirmação da exclusão
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="confirm_box"):
                yield Static("Deletar conta", id="title")
                yield Static(
                    "Tem certeza que deseja deletar sua conta?",
                    classes="subtitle"
                )
                yield Button(
                    "Sim, deletar",
                    id="button_confirm_delete",
                    variant="error"
                )
                yield Button(
                    "Não, voltar",
                    id="button_cancel_delete"
                )

    # Trata a confirmação ou cancelamento da exclusão de conta
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_confirm_delete":
            success, message = delete_user_account(self.user_id)

            if success:
                self.notify(message)
                
                from screens.login_view import LoginView
                self.app.push_screen(LoginView())
                
                current_screen = self.app.screen
                if hasattr(current_screen, "reset_form"):
                    current_screen.reset_form()
            else:
                self.notify(message)
                
        elif event.button.id == "button_cancel_delete":
            self.app.pop_screen()
