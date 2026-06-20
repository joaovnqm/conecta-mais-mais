from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll, Horizontal
from database.repositories.event_repository import event_services
from screens.events.event_details_view import EventDetailsView

EXPIRED_SOCIAL_EVENTS_PAGE_CSS = """
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

#top_bar {
    width: 100%;
    height: auto;
    layout: grid;
    grid-size: 2;
    grid-columns: 8 1fr;
    margin-bottom: 1;
}

#home_button {
    width: 100%;
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

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.event_buttons{
    content-align: center middle;
    width: 100%;
    margin-top: 1;
}
"""

class ExpiredSocialEventsView(Screen):
    """
    Classe responsável pela tela de listagem de eventos sociais que já
    aconteceram. Ela exibe uma lista de eventos passados criados por
    amigos, com a opção de buscar por nome (mesmo filtro já existente
    na tela de Eventos Sociais).
    O botão "🏠" leva diretamente à página principal, independente da
    profundidade de navegação até esta tela.
    """
    CSS = EXPIRED_SOCIAL_EVENTS_PAGE_CSS

    # Inicializa a tela com os dados básicos do usuário autenticado
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com a listagem de eventos sociais expirados
    def compose(self) -> ComposeResult:
        events = event_services.check_events_by_social(self.user_id)
        events = self._filter_expired_events(events)
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Eventos Sociais Expirados", id="top_title")

                yield Static("Buscar evento:")
                yield Input(placeholder="Insira o nome do evento...", id="search_event")
                yield Static("Eventos que já aconteceram. Clique em algum evento abaixo para saber mais.")
                with VerticalScroll(id="events_container"):
                    if events:
                        for event in events:
                            yield Button(event.name, id=f"event_{event.event_id}", classes="event_buttons")

                    else:
                        yield Static("Nenhum evento expirado encontrado.", classes="main_subtitle")

                yield Button("Voltar", id="button_return", variant="primary")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado,
        e executa a ação correspondente:
        - Se for um botão de evento, ela extrai o ID do evento a partir do ID do botão e navega para a tela de detalhes do evento.
        - Se for o botão de voltar, ela simplesmente retorna para a tela anterior.
        - Se for o botão de início, ela volta diretamente para a página principal.
        """
        if event.button.has_class("event_buttons"):
            button_id = event.button.id
            event_id = str(button_id.split("_")[1])
            self.app.push_screen(EventDetailsView(self.user_id, event_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """
        Função que lida com a digitação no campo de busca. Sempre que o texto muda, ela aciona a reavaliação dos filtros.
        """
        if event.input.id == "search_event":
            await self._apply_filters()

    async def _apply_filters(self) -> None:
        """
        Função que lê o estado do Input, aplica a filtragem e chama a atualização da tela,
        mantendo apenas eventos sociais cuja data já passou.
        """
        input_widget = self.query_one("#search_event", Input)
        search_term = input_widget.value.lower().strip()        
        result = event_services.check_events_by_social(self.user_id)
        result = self._filter_expired_events(result)
        if search_term and result:
            result = [event for event in result if search_term in event.name.lower()]

        await self.update_events_on_screen(result)

    def _filter_expired_events(self, events: list) -> list:
        """
        Mantém na lista apenas os eventos cuja data já passou.
        """
        return [event for event in events if event_services.is_event_expired(event.date)]

    async def update_events_on_screen(self, result):
        """
        Função auxiliar para atualizar a listagem de eventos exibida na tela, com base na lista de eventos filtrada. Ela limpa os eventos atuais e monta
        os novos resultados. Se a lista de resultados estiver vazia, ela exibe uma mensagem indicando que nenhum evento foi encontrado com aquele nome.
        """
        container = self.query_one("#events_container")
        await container.remove_children()
        if result:
            for event in result:
                await container.mount(Button(event.name, id=f"event_{event.event_id}", classes="event_buttons"))
        
        else:
            await container.mount(Static("Eventos expirados com esse nome não encontrados.", classes="main_subtitle"))