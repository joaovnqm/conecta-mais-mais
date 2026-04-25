from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Select
from textual.containers import Center, VerticalScroll
from services.events import check_events_with_interests, check_events_by_interest
from services.interests import check_interests_name
from screens.event_details_view import EventDetailsView

MAIN_PAGE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 60;
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

#events_container {
    content-align: center middle;
}

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

.event_buttons{
    content-align: center middle;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EventsView(Screen):
    """
    Classe responsável pela tela de listagem de eventos. Ela exibe uma lista de eventos disponíveis, com a opção de filtrar 
    por interesse.
    """
    CSS = MAIN_PAGE_CSS

    # Inicializa a tela com os dados básicos do usuário autenticado
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_name = user_name
        self.user_id = user_id

    # Monta a interface com filtros por interesse e listagem de eventos
    def compose(self) -> ComposeResult:
        events = check_events_with_interests(self.user_id)
        interests = check_interests_name(self.user_id)
        select_options = [("Todos os Eventos", "all_events")] + [(interest, interest) for interest in interests]
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Filtrar por interesse:")
                yield Select(select_options, value="all_events", allow_blank=False)
                yield Static("Clique em algum evento abaixo para saber mais.", id="main_title")
                with VerticalScroll(id="events_container"):
                    if events:
                        for event in events:
                            yield Button(event[1], id=f"event_{event[0]}", classes="event_buttons")

                    else:
                        yield Static("Nenhum evento encontrado.", classes="main_subtitle")

                yield Button("Voltar", id="button_return", variant="error")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
        e executa a ação correspondente:
        - Se for um botão de evento, ela extrai o ID do evento a partir do ID do botão e navega para a tela de detalhes do evento.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        """
        if event.button.has_class("event_buttons"):
            button_id = event.button.id
            event_id = str(button_id.split("_")[1])
            self.app.push_screen(EventDetailsView(self.user_id, event_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()
            
    async def on_select_changed(self, event: Select.Changed) -> None:
        """
        Função que lida com os eventos de mudança na seleção do filtro por interesse. Ela verifica o valor selecionado,
        e chama a função correspondente para obter os eventos filtrados, e então atualiza a listagem de eventos exibida na 
        tela com base no resultado do filtro aplicado. Se "Todos os Eventos" for selecionado, ela chama check_events_with_interests 
        para obter todos os eventos relacionados aos interesses do usuário.
        """
        selected_value = event.value
        if selected_value is "all_events":
            result = check_events_with_interests(self.user_id)

        else:
            result = check_events_by_interest(selected_value)

        await self.update_events_on_screen(result)

    async def update_events_on_screen(self, result):
        """
        Função auxiliar para atualizar a listagem de eventos exibida na tela, com base no resultado da aplicação do filtro 
        por interesse. Ela remove os eventos atualmente exibidos e monta novos botões para os eventos filtrados, 
        ou exibe uma mensagem caso nenhum evento esteja disponível para os filtros selecionados.
        """
        container = self.query_one("#events_container")
        await container.remove_children()
        if result:
            for event in result:
                container.mount(
                    Button(event[1], id=f"event_{event[0]}", classes="event_buttons")
                )
        
        else:
            container.mount(
                Static("Eventos com filtros selecionados não disponíveis no momento.")
            )