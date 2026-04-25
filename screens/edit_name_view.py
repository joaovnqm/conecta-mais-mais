from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical

from services.users import get_user_profile, update_user_name

AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth_box {
    width: 56;
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

#message {
    width: 100%;
    height: auto;
    min-height: 1;
    margin-top: 1;
    color: $warning;
}

.action_button {
    width: 100%;
    margin-top: 1;
}
"""

class EditNameView(Screen):
    """
    Classe responsável pela tela de edição de nome. Ela é acessada a partir da tela de perfil, e permite que o usuário 
    altere seu nome atual para um novo nome. A tela inclui um campo para o novo nome, que é pré-preenchido com o nome 
    atual do usuário, além de botões para salvar as alterações ou voltar para a tela anterior.
    """
    CSS = AUTH_CSS
    
    # Inicializa a tela com o identificador do usuário
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        
    # Monta a interface de edição de nome com valor atual preenchido, quando disponível
    def compose(self) -> ComposeResult:
        profile = get_user_profile(self.user_id)
        current_name = profile["name"] if profile else ""
        
        with Center():
            with Vertical(id="auth_box"):
                yield Static("Atualizar nome", id="title")
                yield Static("Digite seu novo nome", classes="subtitle")
                
                yield Input (
                    placeholder="Digite o seu novo nome...",
                    id="new_name",
                    value=current_name
                )
                
                yield Static("", id="message")
                
                yield Button("Salvar", id="button_save", classes="action_button")
                yield Button("Voltar", id="button_back", variant="primary", classes="action_button")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado, 
        e executa a ação correspondente:
        - Se for o botão de salvar, ela coleta o novo nome digitado e chama a função update_user_name para tentar atualizar o nome, 
        e atualiza a mensagem de resposta com o resultado.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        response = self.query_one("#message", Static)
        
        if event.button.id == "button_save":
            new_name = self.query_one("#new_name", Input).value
            
            sucess, message = update_user_name(self.user_id, new_name)
            response.update(message)
            
            if sucess:
                self.notify("Nome alterado com sucesso")
                self.app.pop_screen()
                
                current_screen = self.app.screen
                if hasattr(current_screen, "reload_profile"):
                    current_screen.reload_profile()

        elif event.button.id == "button_back":
            self.app.pop_screen() 