from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical
from screens.events.events_view import EventsView
from screens.events.events_social_view import EventsSocialView
from screens.events.create_social_event_view import CreateSocialEventView

EVENTS_GENERAL_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 86;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EventsGeneralView(Screen):
    """
    Classe responsável pela tela intermediária de eventos. Ela é exibida após o usuário clicar em "Eventos", e oferece opções de navegação para
    a página dos diversos tipos de eventos, além de eventos sociais (criados por amigos) e de criar eventos sociais. O botão de voltar também está presente.
    """
    CSS = EVENTS_GENERAL_CSS
    
    # Inicializa a tela principal com os dados do usuário autenticado
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_name = user_name
        self.user_id = user_id
    
    # Monta a tela principal após o login
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="main_box"):
                yield Static("Eventos", id="main_title")
                yield Button("Eventos de T.I.", id="button_ti")
                yield Button("Eventos Sociais", id="button_social")
                yield Button("Criar Evento Social", id="button_create_social_event")
                yield Button("Voltar", id="button_return", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela principal. Ela verifica qual botão foi clicado, e executa a ação 
        correspondente:
        - Se for o botão de eventos de T.I., a tela de listagem de eventos é exibida, com os eventos relacionados a T.I. e os interesses do usuário.
        - Se for o botão de eventos sociais, a tela de listagem de eventos sociais é exibida, com os eventos sociais criados por amigos do usuário.
        - Se for o botão de criar evento social, a tela de criação de evento social é exibida, permitindo que o usuário crie um evento social e 
        convide seus amigos.
        - Se for o botão de voltar, a tela anterior é exibida.
        """
        
        if event.button.id == "button_ti":
            self.app.push_screen(EventsView(self.user_id))

        elif event.button.id == "button_social":
            self.app.push_screen(EventsSocialView(self.user_id))

        elif event.button.id == "button_create_social_event":
            self.app.push_screen(CreateSocialEventView(self.user_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()