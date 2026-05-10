from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Checkbox
from textual.containers import Center, Vertical
from database.repositories.interest_repository import interest_services
from unidecode import unidecode

INTEREST_CSS = """
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

.interests.-on {
    color: limegreen 90%;
}

.interests.-on > .toggle--button {
    color: limegreen 90%;
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

class ChangeInterestView(Screen):
    """
    Classe responsável pela tela de alteração dos interesses. Ela é exibida após o clique na página de perfil,
    e permite que ele selecione e altere os seus interesses a partir de uma lista de opções disponíveis. 
    Os interesses selecionados são salvos no banco de dados e associados ao perfil do usuário, para que possam 
    ser utilizados posteriormente para personalizar a experiência do usuário na plataforma, como por exemplo,
    exibir eventos relacionados aos interesses selecionados.
    """
    CSS = INTEREST_CSS

    # Inicializa a tela com os dados do usuário recém cadastrado
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com a lista de interesses disponíveis
    def compose(self) -> ComposeResult:
        user_interests = interest_services.check_user_interests(self.user_id)
        interests = interest_services.check_all_interests()
        with Center():
            with Vertical(id="interest_box"):
                yield Static("Conecta++", id="title")
                yield Static("Selecione todos os seus interesses abaixo. Pode ser mais de um.", classes="subtitle")
                if interests:
                    for interest in interests:
                        interest_id = interest.name.replace(" ", "_").lower().strip()
                        interest_id = unidecode(interest_id)

                        checked = False

                        for user_interest in user_interests:
                            if user_interest.interest_id == interest.interest_id:
                                checked = True
                                break

                        yield Checkbox(interest.name, id=f"interesse_{interest_id}", classes="interests", value=checked)

                else:
                    yield Static("Nenhum interesse encontrado.", classes="main_subtitle")
                    
                yield Button("Atualizar interesses", id="button_change_interests")
                yield Button("Voltar", id="button_back", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
            """
            Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
            e executa a ação correspondente:
            - Se o botão de atualizar interesses for clicado, ela coleta os interesses selecionados e não selecionados, 
            e chama as funções de adição e remoção de interesses, respectivamente, para atualizar os interesses do usuário
            no banco de dados. Após a atualização, ela exibe uma notificação de sucesso e volta para a tela anterior.
            - Se o botão de voltar for clicado, ela simplesmente volta para a tela anterior sem fazer nenhuma alteração.
            """
            if event.button.id == "button_change_interests":
                checkboxes = self.query(".interests")
                selected_interests = {str(cb.label) for cb in checkboxes if cb.value}

                if not selected_interests:
                    self.app.notify("Você precisa adicionar pelo menos um interesse.", severity="warning")
                    return

                current_interests = {interest.name for interest in interest_services.check_user_interests(self.user_id)}
                interests_to_add = selected_interests - current_interests
                interests_to_remove = current_interests - selected_interests

                for interest in interests_to_add:
                    interest_services.add_interests(self.user_id, interest)
                
                for interest in interests_to_remove:
                    interest_services.remove_interests(self.user_id, interest)

                self.app.notify("Interesses atualizados com sucesso!")
                self.app.pop_screen()

            elif event.button.id == "button_back":
                self.app.pop_screen()