from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Select, Input
from textual.containers import Center, VerticalScroll, Horizontal
from database.repositories.event_repository import event_services
from database.repositories.interest_repository import interest_services
from screens.events.event_details_view import EventDetailsView
import sqlite3
from database.repositories.event_important_dates_repository import EventImportantDatesRepository

EVENTS_PAGE_CSS = """
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

#events_container {
    content-align: center middle;
}

#search_event {
    width: 1fr;
    margin-bottom: 1;
}

.main_subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.event_listing {
    layout: grid;
    grid-size: 2;
    grid-columns: 2fr 1fr;
    height: auto;
    margin-bottom: 1;
}

.event_buttons {
    width: 100%;
    height: 3;
}

.event_submission_status {
    width: 100%;
    height: 100%;
    content-align: center middle;
}

#button_return {
    width: 100%;
    margin-top: 2;
}
"""

class EventsView(Screen):
    """
    Classe responsável pela tela de listagem de eventos. Ela exibe uma lista de eventos disponíveis, com a opção de filtrar 
    por interesse e buscar por nome.
    """
    CSS = EVENTS_PAGE_CSS

    # Inicializa a tela com os dados básicos do usuário autenticado
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com filtros por interesse e listagem de eventos
    def compose(self) -> ComposeResult:
        events = event_services.check_events_by_interests(self.user_id)
        interests = interest_services.check_user_interests(self.user_id)
        select_options = [("Todos os Eventos", "all_events")] + [(interest.name, interest.name) for interest in interests if interest.name != "Social"]
        
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Eventos", id="main_title")
                yield Static("Buscar evento:")
                yield Input(
                    placeholder="Insira o nome do evento...",
                    id="search_event"
                )
                yield Static("Filtrar por interesse:")
                yield Select(select_options, value="all_events", allow_blank=False)
                yield Static("Clique em algum evento abaixo para saber mais.", classes="main_subtitle")
                
                with VerticalScroll(id="events_container"):
                    if events:
                        # carregar status de submissão para exibição
                        with sqlite3.connect(event_services.database_path) as connection:
                            repo = EventImportantDatesRepository(connection)

                            for event in events:
                                status = repo.get_submission_status(event.event_id)
                                status_text = status.get("message", "—")

                                with Horizontal(classes="event_listing"):
                                    yield Button(event.name, id=f"event_{event.event_id}", classes="event_buttons")
                                    yield Static(status_text, classes="event_submission_status")
                    else:
                        yield Static("Nenhum evento encontrado.", classes="main_subtitle")

                yield Button("Voltar", id="button_return", variant="primary")
                
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

    async def on_input_changed(self, event: Input.Changed) -> None:
        """
        Função que lida com a digitação no campo de busca. Sempre que o texto muda, ela aciona a reavaliação dos filtros.
        """
        if event.input.id == "search_event":
            await self._apply_filters()
            
    async def on_select_changed(self, event: Select.Changed) -> None:
        """
        Função que lida com os eventos de mudança na seleção do filtro por interesse.
        """
        await self._apply_filters()

    async def _apply_filters(self) -> None:
        """
        Função centralizadora que lê o estado do Select e do Input, aplica ambas as filtragens e chama a atualização da tela.
        """
        select_widget = self.query_one(Select)
        input_widget = self.query_one("#search_event", Input)
        
        selected_interest = select_widget.value
        search_term = input_widget.value.lower().strip()
        
        if selected_interest == "all_events":
            result = event_services.check_events_by_interests(self.user_id)
        else:
            result = event_services.check_events_by_interest(selected_interest)

        if search_term and result:
            result = [event for event in result if search_term in event.name.lower()]

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
            # consultar status de submissão em lote para os eventos filtrados
            with sqlite3.connect(event_services.database_path) as connection:
                repo = EventImportantDatesRepository(connection)

                for event in result:
                    status = repo.get_submission_status(event.event_id)
                    status_text = status.get("message", "—")

                    container.mount(
                        # Adicionada a classe 'event_listing' para garantir que o CSS aplique no rebuild
                        Horizontal(
                            Button(event.name, id=f"event_{event.event_id}", classes="event_buttons"),
                            Static(status_text, classes="event_submission_status"),
                            classes="event_listing"
                        )
                    )
                
        else:
            container.mount(Static("Eventos com filtros selecionados não disponíveis no momento.", classes="main_subtitle"))