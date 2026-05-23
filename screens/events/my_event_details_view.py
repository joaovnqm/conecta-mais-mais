from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical, VerticalScroll
from screens.events.delete_social_event_view import DeleteSocialEventView
from screens.events.edit_social_event_view import EditSocialEventView
from database.repositories.event_repository import event_services
from services.event_participation import event_participation_service

MY_EVENT_DETAILS_VIEW = """
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
    align: center top;
}

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

#button_edit_event,
#button_delete_event,
#button_return {
    width: 100%;
    content-align: center middle;
    margin: 1;
}

#friends_presence_container,
#friends_favorites_container {
    width: 100%;
    height: auto;
    margin: 0;
    padding: 0;
}

.section_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}
"""

class MyEventDetailsView(Screen):
    """
    Classe responsável pela tela de detalhes do evento criado pelo usuário. Ela exibe as informações do evento selecionado, como nome, descrição, local, 
    data, hora e opções para editar ou excluir o evento.
    """
    CSS = MY_EVENT_DETAILS_VIEW

    # Inicializa a tela com o evento que será exibido
    def __init__(self, event_id: int, user_id: int):
        super().__init__()
        self.event_id = event_id
        self.user_id = user_id

    # Monta a interface com as informações do evento e do criador
    def compose(self) -> ComposeResult:
        event = event_services.check_event(self.event_id)
        total_presence = event_participation_service.count_confirmed_presence(self.event_id)
        total_favorites = event_participation_service.count_favorites(self.event_id)

        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Evento: {event.name}", id="main_title")
                yield Static(
                    "Veja as informações do seu evento criado. Você pode editar ou excluir o evento usando os botões abaixo."
                )
                with Vertical(classes="section_card"):
                    yield Static(f"Descrição: {event.description}")
                    if event.event_location == None:
                        yield Static("O local do evento ainda não está disponível")

                    else:
                        yield Static(f"Local: {event.event_location}.")
                    
                    if event.date == None:
                        yield Static("A data do evento ainda não está disponível")

                    else: 
                        yield Static(f"Data: {event.date}.")

                    if event.hour == None:
                        yield Static("A hora do evento ainda não foi divulgada")
                        
                    else:
                        yield Static(f"Hora: {event.hour}")

                with Vertical(classes="section_card"):
                    yield Static("Resumo social", classes="section_title")
                    yield Static(
                        f"Pessoas com presença confirmada: {total_presence}",
                        id="presence_count",
                        classes="social_text"
                    )
                    yield Static(
                        f"Pessoas que favoritaram: {total_favorites}",
                        id="favorite_count",
                        classes="social_text"
                    )
                
                with Vertical(classes="section_card"):
                    yield Static("Amigos que vão", classes="section_title")
                    yield Vertical(id="friends_presence_container")

                with Vertical(classes="section_card"):
                    yield Static("Amigos que favoritaram", classes="section_title")
                    yield Vertical(id="friends_favorites_container")

                with Vertical(classes="section_card"):
                    yield Static("Ações do evento:")
                    yield Button("Editar Evento", id="button_edit_event")
                    yield Button("Excluir Evento", id="button_delete_event", variant="error")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        """Ao montar a tela, carrega os dados sociais do evento para exibir as ações disponíveis e o resumo social."""
        await self.reload_event_social_data()

    async def on_screen_resume(self) -> None:
        """Quando a tela for retomada (após voltar de outra tela), recarrega os dados sociais para garantir que as informações estejam atualizadas."""
        await self.reload_event_social_data()

    async def reload_event_social_data(self) -> None:
        """Recarrega os dados sociais do evento, incluindo o resumo social e as listas de amigos presentes e que favoritaram."""
        await self.reload_social_summary()
        await self.reload_friends_presence()
        await self.reload_friends_favorites()

    async def reload_social_summary(self) -> None:
        """Recarrega o resumo social do evento, atualizando as contagens de presença confirmada e favoritos com base nos dados mais recentes do banco de dados."""
        total_presence = event_participation_service.count_confirmed_presence(
            self.event_id
        )

        total_favorites = event_participation_service.count_favorites(
            self.event_id
        )

        self.query_one("#presence_count", Static).update(
            f"Pessoas com presença confirmada: {total_presence}"
        )

        self.query_one("#favorite_count", Static).update(
            f"Pessoas que favoritaram: {total_favorites}"
        )

    async def reload_friends_presence(self) -> None:
        """Recarrega a lista de amigos que confirmaram presença no evento."""
        container = self.query_one("#friends_presence_container")
        await container.remove_children()

        friends = event_participation_service.list_friends_confirmed_presence(
            self.user_id,
            self.event_id
        )

        if not friends:
            await container.mount(
                Static(
                    "Nenhum amigo confirmou presença neste evento.",
                    classes="empty_state"
                )
            )
            return

        for friend in friends:
            await container.mount(
                Static(
                    f"{friend['name']} - @{friend['username']}",
                    classes="social_text"
                )
            )

    async def reload_friends_favorites(self) -> None:
        """Recarrega a lista de amigos que favoritaram o evento."""
        container = self.query_one("#friends_favorites_container")
        await container.remove_children()

        friends = event_participation_service.list_friends_favorited_event(
            self.user_id,
            self.event_id
        )

        if not friends:
            await container.mount(
                Static(
                    "Nenhum amigo favoritou este evento.",
                    classes="empty_state"
                )
            )
            return

        for friend in friends:
            await container.mount(
                Static(
                    f"{friend['name']} - @{friend['username']}",
                    classes="social_text"
                )
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_edit_event":
            self.app.push_screen(EditSocialEventView(self.event_id))
        
        elif event.button.id == "button_delete_event":
            self.app.push_screen(DeleteSocialEventView(self.event_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()