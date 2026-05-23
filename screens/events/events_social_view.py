from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll
from database.repositories.event_repository import event_services
from screens.events.event_details_view import EventDetailsView

SOCIAL_EVENTS_PAGE_CSS = """
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

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.event_buttons{
    content-align: center middle;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class EventsSocialView(Screen):
    """
    Classe responsável pela tela de listagem de eventos sociais. Ela exibe uma lista de eventos criados por amigos e que estão disponíveis, com a opção
    de buscar por nome.
    """
    CSS = SOCIAL_EVENTS_PAGE_CSS

    # Inicializa a tela com os dados básicos do usuário autenticado
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    # Monta a interface com filtros por interesse e listagem de eventos
    def compose(self) -> ComposeResult:
        events = event_services.check_events_by_social(self.user_id)
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Eventos Sociais", id="main_title")
                yield Static("Buscar evento:")
                yield Input(
                    placeholder="Insira o nome do evento...",
                    id="search_event"
                )
                yield Static("Clique em algum evento abaixo para saber mais.")
                with VerticalScroll(id="events_container"):
                    if events:
                        for event in events:
                            yield Button(event.name, id=f"event_{event.event_id}", classes="event_buttons")

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

    async def _apply_filters(self) -> None:
        """
        Função que lê o estado do Input, aplica a filtragem e chama a atualização da tela.
        """
        input_widget = self.query_one("#search_event", Input)
        search_term = input_widget.value.lower().strip()
        
        result = event_services.check_events_by_social(self.user_id)
        
        if search_term and result:
            result = [event for event in result if search_term in event.name.lower()]

        await self.update_events_on_screen(result)

    async def update_events_on_screen(self, result):
        """
        Função auxiliar para atualizar a listagem de eventos exibida na tela, com base na lista de eventos filtrada. Ela limpa os eventos atuais e monta
        os novos resultados. Se a lista de resultados estiver vazia, ela exibe uma mensagem indicando que nenhum evento foi encontrado com aquele nome.
        """
        container = self.query_one("#events_container")
        await container.remove_children()
        
        if result:
            for event in result:
                container.mount(Button(event.name, id=f"event_{event.event_id}", classes="event_buttons"))
        else:
            container.mount(Static("Eventos com esse nome não encontrados.", classes="main_subtitle"))