from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll, Horizontal
from screens.events.my_event_details_view import MyEventDetailsView
from database.repositories.event_repository import event_services

MY_EVENTS_PAGE_CSS = """
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

#top_bar {
    width: 100%;
    height: auto;
    layout: grid;
    grid-size: 3;
    grid-columns: 6 1fr 6;
    margin-bottom: 1;
}

#home_button {
    width: 8;
    height: 3;
}

#top_title {
    content-align: center middle;
    height: 3;
    text-style: bold;
}

#button_return {
    width: 100%;
    margin-top: 1;
}

#events_container {
    content-align: center middle;
}

#search_event {
    width: 1fr;
    margin-bottom: 1;
}

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.event_buttons{
    width: 100%;
    margin-top: 1;
    content-align: center middle;
}
"""

class MyEventsView(Screen):
    """
    Classe responsável pela tela de listagem dos eventos criados pelo usuário. Ela exibe uma lista de eventos criados pelo usuário, com a opção de clicar e ver os detalhes do evento.
    """
    CSS = MY_EVENTS_PAGE_CSS

    def __init__(self, user_id: int):
        """Inicializa a tela de meus eventos para um usuário específico."""
        super().__init__()
        self.user_id = user_id
    
    def compose(self) -> ComposeResult:
        """Compõe a interface da tela de meus eventos, exibindo os eventos criados pelo usuário e os botões de navegação."""
        events = event_services.check_events_by_user(self.user_id)
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Meus Eventos", id="top_title")
                    yield Static("")

                yield Static("Clique no evento para ver os detalhes.", classes="main_subtitle")
                if events:
                    for event in events:
                        yield Button(event.name, id=f"event_{event.event_id}", classes="event_buttons")

                else:
                    yield Static("Você ainda não criou nenhum evento.", id="main_subtitle")
                
                yield Button("Voltar", id="button_return", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Essa função é chamada quando um botão de evento é pressionado. Ela extrai o id do evento do id do botão e navega para a tela de detalhes do evento.
        """
        if event.button.has_class("event_buttons"):
            button_id = event.button.id
            event_id = int(button_id.split("_")[1])
            self.app.push_screen(MyEventDetailsView(event_id, self.user_id))
        
        elif event.button.id == "button_return":
            self.app.pop_screen() 

        elif event.button.id == "home_button":
            self.app.pop_screen()
            self.app.pop_screen() 