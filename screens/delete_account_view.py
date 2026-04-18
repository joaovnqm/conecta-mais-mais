from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical

from services.users import delete_user_account

"""
Bloco de estilo da tela de confirmação para deletar conta.
Define o alinhamento da tela, aparência da caixa de confirmação, cores, bordas, espaçamentos e estilo dos botões.
"""

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
    # Aplica o CSS definido acima nesta tela
    CSS = AUTH_CSS
    
    """
    Função construtora da tela.
        1. Inicializa a classe Screen
        2. Recebe e armazena o id do usuário que poderá ser deletado
    """
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    """
    Função que monta os componentes visuais da tela.
        1. Cria a caixa central de confirmação
        2. Exibe o título da tela
        3. Exibe a mensagem perguntando se o usuário tem certeza
        4. Adiciona o botão para confirmar exclusão
        5. Adiciona o botão para cancelar e voltar
    """
    
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="confirm_box"):
                # Título principal da tela
                yield Static("Deletar conta", id="title")
                # Mensagem de confirmação para o usuário
                yield Static(
                    "Tem certeza que deseja deletar sua conta?",
                    classes="subtitle"
                )
                # Botão para confirmar a exclusão de conta
                yield Button(
                    "Sim, deletar",
                    id="button_confirm_delete",
                    variant="error"
                )
                # Botão para cancelar a exclusão e voltar
                yield Button(
                    "Não, voltar",
                    id="button_cancel_delete"
                )
    """
    Função que trata os cliques dos botões da tela.
        1. Se o usuário confirmar, chama o serviço para deletar a conta
        2. Se a exclusão der certo, mostra uma notificação e redireciona para a tela de login
        3. Se a nova tela tiver a função reset_form, limpa os campos
        4. Se houver erro, mostra a mensagem retornada
        5. Se o usuário cancelar, volta para a tela anterior
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Se clicou no botão de confirmar exclusão
        if event.button.id == "button_confirm_delete":
            # Chama a função responsável por deletar a conta do usuário
            success, message = delete_user_account(self.user_id)

            # Se a exclusão foi concluída com sucesso
            if success:
                # Mostra a mensagem de sucesso ao usuário
                self.notify(message)
                
                # Importa a tela de login e redireciona o usuário para ela
                from screens.login_view import LoginView
                self.app.push_screen(LoginView())
                
                # Pega a tela atual e verifica se ela possui o método reset_form
                current_screen = self.app.screen
                if hasattr(current_screen, "reset_form"):
                    current_screen.reset_form()
            
            # Se a exclusão falhou, mostrar a mensagem de erro
            else:
                self.notify(message)

        # Se clicou no botão de cancelar, voltar a tela anterior
        elif event.button.id == "button_cancel_delete":
            self.app.pop_screen()
