from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, Vertical, Horizontal

from services.users import change_user_password

"""
Bloco de estilização de tela de autenticação/alteração de senha.
Define o alinhamento da tela, cores, tamanhos, espaçamentos, bordas e aparência dos campos e botões.
"""

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

"""
Classe responsável pela tela de alteração de senha do usuário. 
Ela exibe os campos para senha atual, nova senha e confirmação, além dos botões para salvar ou voltar
"""
class ChangePasswordView(Screen):
    # Aplica o CSS definido acima nessa tela.
    CSS = AUTH_CSS

    """
    Função construtora de tela.
        1. Inicializa a classe Screen
        2. Recebe e armazena o id do usuário que terá a senha alterada
    """
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    """
    Função que monta os componentes visuais da tela
        1. Cria a caixa central da interface
        2. Exibe o título e subtítulo
        3. Cria os campos de senha atual, nova senha e confirmação
        4. Adiciona botões para mostrar/ocultar senha
        5. Adiciona área de mensagem e botões de ação
    """
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth_box"):
                # Título principal da tela
                yield Static("Atualizar senha", id="title")
                
                # Texto auxiliar explicando o que o usuário deve fazer
                yield Static(
                    "Digite sua senha atual e depois defina a nova senha",
                    classes="subtitle"
                )
                # Campo da senha atual + botão mostrar/ocultar senha
                with Horizontal(id="current-password-row"):
                    yield Input(
                        placeholder="Digite sua senha atual...",
                        id="current_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_current_password")
                
                # Campo de nova senha + botão mostrar/ocultar
                with Horizontal(id="new-password-row"):
                    yield Input(
                        placeholder="Digite a sua nova senha...",
                        id="new_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_new_password")
                
                # Campo de confirmação da nova senha + botão mostrar/ocultar senha 
                with Horizontal(id="confirm-password-row"):
                    yield Input(
                        placeholder="Confirme a nova senha...",
                        id="confirm_password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_confirm_password")
                
                # Área onde mensagens de erro ou sucesso serão exibidos
                yield Static("", id="message")

                # Botão para salvar nova senha
                yield Button(
                    "Salvar",
                    id="button_save",
                    variant="primary",
                    classes="action_button"
                )
                
                # Botão para voltar a tela anterior
                yield Button(
                    "Voltar",
                    id="button_back",
                    variant="error",
                    classes="action_button"
                )

    """
    Função auxiliadora para mostrar ou ocultar a senha de um campo.
        1. Localiza o campo Input pelo id
        2. Localiza o botão correspondente pelo id
        3. Inverte o estado da exibição da senha
        4. Atualiza o texto do botão entre "Mostrar" e "Ocultar"
    """
    def _toggle_visibility(self, input_id: str, button_id: str) -> None:
        # Campo de entrada da senha
        password_input = self.query_one(f"#{input_id}", Input)
       
        # Botão responsável por alterar a visibilidade
        toggle_button = self.query_one(f"#{button_id}", Button)
        
        # Inverte o estado atual do campo
        password_input.password = not password_input.password
        
        # Atualiza o rótulo do botão conforme o estado do campo
        toggle_button.label = "Mostrar" if password_input.password else "Ocultar"

    """
    Função que trata os cliques dos botões na tela.
        1. Verifica se o clique foi em algum botão de mostrar/ocultar senha
        2. Se for salvar, coleta os valores digitados
        3. Verifica se a nova senha e a confirmação são iguais
        4. Chama a função de alteração de senha no serviço
        5. Exibe a mensagem de retorno
        6. Se der certo, mostra mensagem e fecha a tela
        7. Se clicar em voltar, retorna  para a tela anterior
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Campo de mensagem usado para mostrar erros ou confirmações
        response = self.query_one("#message", Static)

        # Alterna a visibilidade da senha atual
        if event.button.id == "toggle_current_password":
            self._toggle_visibility(
                "current_password", "toggle_current_password")
            return

        # Alterna a visibilidade da nova senha
        if event.button.id == "toggle_new_password":
            self._toggle_visibility("new_password", "toggle_new_password")
            return

        # Alterna a visibilidade da confirmação da nova senha
        if event.button.id == "toggle_confirm_password":
            self._toggle_visibility(
                "confirm_password", "toggle_confirm_password")
            return

        # Se clicou no botão de salvar
        if event.button.id == "button_save":
            # Salva os valores digitados nos campos
            current_password = self.query_one("#current_password", Input).value
            new_password = self.query_one("#new_password", Input).value
            confirm_password = self.query_one("#confirm_password", Input).value

            # Verifica se a senha nova é igual à confirmação da senha
            if new_password != confirm_password:
                response.update("As senhas não coincidem.")
                return
            
            # Chama a função responsável por alterar senha
            success, message = change_user_password(
                self.user_id,
                current_password,
                new_password
            )
            response.update(message)

            # Se a alteração deu certo, mostre a notificação e volta para a tela anterior
            if success:
                self.notify("Senha alterada com sucesso.")
                self.app.pop_screen()
                
        # Se clicou no botão de voltar, apenas feche a tela atual
        elif event.button.id == "button_back":
            self.app.pop_screen()
