from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Checkbox, Label
from textual.containers import Center, Vertical
from screens.main_page_view import MainPageView
from services.interests import add_interests, check_all_interests
from unidecode import unidecode

AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#interest_box {
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

Button {
    width: 100%;
    margin-top: 1;
}

#message {
    height: 2;
    margin-top: 1;
    color: $warning;
}
"""

class InterestsView(Screen):
    """
    Classe responsável pela tela de seleção de interesses. Ela é exibida após o cadastro do usuário, e permite que ele selecione 
    os seus interesses a partir de uma lista de opções disponíveis. Os interesses selecionados são salvos no banco de dados e 
    associados ao perfil do usuário, para que possam ser utilizados posteriormente para personalizar a experiência do usuário 
    na plataforma, como por exemplo, exibir eventos relacionados aos interesses selecionados.
    """
    CSS = AUTH_CSS
    
    # Inicializa a tela com os dados do usuário recém cadastrado
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        
    # Monta a interface com a lista de interesses disponíveis
    def compose(self) -> ComposeResult:
        interests = check_all_interests()
        with Center():
            with Vertical(id="interest_box"):
                yield Static("Conecta++", id="title")
                yield Static("Selecione os seus interesses abaixo", classes="subtitle")
                if interests:
                    for interest in interests:
                        interest_id = interest[0].replace(" ", "_").lower().strip()
                        interest_id = unidecode(interest_id)
                        yield Checkbox(interest[0], id=f"interesse_{interest_id}", classes="interests")

                else:
                    yield Static("Nenhum interesse encontrado.", classes="main_subtitle")
                yield Button("Definir interesses", id="button_register_interests", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
            """
            Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
            e executa a ação correspondente:
            - Se for o botão de definir interesses, ela coleta os interesses marcados, chama a função de adição de interesses,
              e exibe a mensagem de resposta. Se a operação for bem-sucedida, ela navega para a tela principal.
            """
            if event.button.id == "button_register_interests":
                checkboxes = self.query(".interests")
                selected_checkboxes = [cb for cb in checkboxes if cb.value]
                if not selected_checkboxes:
                    self.notify("Você precisa adicionar pelo menos um interesse.")
                    return
                    
                else:
                    for checkbox in selected_checkboxes:
                        add_interests(self.user_id, str(checkbox.label))

                    self.notify("Interesse(s) adicionado(s) com sucesso!")
                    self.app.push_screen(MainPageView(self.user_id, self.user_name))