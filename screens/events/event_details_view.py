from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll, Vertical
from database.repositories.event_repository import event_services
from database.repositories.user_repository import user_services
from services.favorite_events import (
    check_favorite_event,
    favorite_event,
    remove_from_favorite_event
)
from services.event_participation import event_participation_service


EVENT_DETAILS_VIEW = """
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

.subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

.section_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}

#favorite_button_container,
#presence_button_container,
#friends_presence_container,
#friends_favorites_container {
    width: 100%;
    height: auto;
    margin: 0;
    padding: 0;
}

.section_title {
    text-style: bold;
    margin-bottom: 1;
}

.info_label {
    margin-top: 1;
    text-style: bold;
}

.info_value {
    color: $text-muted;
    margin-bottom: 1;
}

.social_text {
    color: $text-muted;
    margin-top: 1;
}

.empty_state {
    color: $text-muted;
    margin-top: 1;
}

#button_favorite_event,
#button_presence_event {
    width: 100%;
    margin-top: 1;
    margin-bottom: 0;
}

#button_return {
    width: 100%;
    margin-top: 1;
}
"""


class EventDetailsView(Screen):
    """
    Tela responsável por exibir detalhes do evento e permitir ações sociais:
    - favoritar/desfavoritar;
    - confirmar/desmarcar presença;
    - visualizar amigos presentes;
    - visualizar amigos que favoritaram.
    """

    CSS = EVENT_DETAILS_VIEW

    def __init__(self, user_id: int, event_id: int):
        super().__init__()
        self.user_id = user_id
        self.event_id = int(event_id)

    def compose(self) -> ComposeResult:
        """
        Composição da tela de detalhes do evento, exibindo informações do evento e ações sociais disponíveis para o usuário.
        """
        event = event_services.check_event(self.event_id)
        creator_name = user_services.check_user_name(event.creator_id)
        total_presence = event_participation_service.count_confirmed_presence(self.event_id)
        total_favorites = event_participation_service.count_favorites(self.event_id)

        with Center():
            with VerticalScroll(id="main_box"):
                yield Static(f"Evento: {event.name}", id="main_title")
                yield Static(
                    "Veja os detalhes do evento e acompanhe a atividade dos seus amigos.",
                    classes="subtitle"
                )

                with Vertical(classes="section_card"):
                    yield Static("Informações do evento", classes="section_title")

                    yield Static("Descrição:", classes="info_label")
                    yield Static(event.description, classes="info_value")

                    yield Static("Local:", classes="info_label")
                    if event.event_location:
                        yield Static(event.event_location, classes="info_value")
                    else:
                        yield Static(
                            "O local do evento ainda não está disponível.",
                            classes="info_value"
                        )

                    yield Static("Data:", classes="info_label")
                    if event.date:
                        yield Static(event.date, classes="info_value")
                    else:
                        yield Static(
                            "A data do evento ainda não está disponível.",
                            classes="info_value"
                        )

                    yield Static("Hora:", classes="info_label")
                    if event.hour:
                        yield Static(event.hour, classes="info_value")
                    else:
                        yield Static(
                            "A hora do evento ainda não foi divulgada.",
                            classes="info_value"
                        )

                    yield Static("Criador:", classes="info_label")
                    yield Static(
                        creator_name or "Criador não encontrado.",
                        classes="info_value"
                    )

                with Vertical(classes="section_card"):
                    yield Static("Ações do evento:", classes="section_title")
                    yield Vertical(id="favorite_button_container")
                    yield Vertical(id="presence_button_container")

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

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        """Ao montar a tela, carrega os dados sociais do evento para exibir as ações disponíveis e o resumo social."""
        await self.reload_event_social_data()

    async def on_screen_resume(self) -> None:
        """Quando a tela for retomada (após voltar de outra tela), recarrega os dados sociais para garantir que as informações estejam atualizadas."""
        await self.reload_event_social_data()

    async def reload_event_social_data(self) -> None:
        """Recarrega os dados sociais do evento, incluindo o estado dos botões de favoritar e presença, o resumo social e as listas de amigos presentes e que favoritaram."""
        await self.reload_favorite_button()
        await self.reload_presence_button()
        await self.reload_social_summary()
        await self.reload_friends_presence()
        await self.reload_friends_favorites()

    async def reload_favorite_button(self) -> None:
        """Recarrega o estado do botão de favoritar/desfavoritar com base na relação atual do usuário com o evento."""
        container = self.query_one("#favorite_button_container")
        await container.remove_children()

        if check_favorite_event(self.user_id, self.event_id):
            await container.mount(
                Button(
                    "Desfavoritar evento",
                    id="button_favorite_event",
                    variant="default"
                )
            )
        else:
            await container.mount(
                Button(
                    "★ Favoritar evento",
                    id="button_favorite_event",
                    variant="warning"
                )
            )

    async def reload_presence_button(self) -> None:
        """Recarrega o estado do botão de confirmar/desmarcar presença com base na relação atual do usuário com o evento."""
        container = self.query_one("#presence_button_container")
        await container.remove_children()

        if event_participation_service.check_presence(self.user_id, self.event_id):
            await container.mount(
                Button(
                    "Desmarcar presença",
                    id="button_presence_event",
                    variant="error"
                )
            )
        else:
            await container.mount(
                Button(
                    "Confirmar presença",
                    id="button_presence_event",
                    variant="success"
                )
            )

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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os eventos de clique nos botões de favoritar/desfavoritar, confirmar/desmarcar presença e voltar, chamando os métodos apropriados para cada ação."""
        if event.button.id == "button_favorite_event":
            await self.handle_favorite_button()
            return

        if event.button.id == "button_presence_event":
            await self.handle_presence_button()
            return

        if event.button.id == "button_return":
            self.app.pop_screen()
            return

    async def handle_favorite_button(self) -> None:
        """Gerencia a lógica de favoritar ou desfavoritar o evento com base no estado atual, atualizando o banco de dados e recarregando os dados sociais após a ação."""
        if check_favorite_event(self.user_id, self.event_id):
            success, message = remove_from_favorite_event(
                self.user_id,
                self.event_id
            )
        else:
            success, message = favorite_event(
                self.user_id,
                self.event_id
            )

        self.app.notify(message)

        if success:
            await self.reload_event_social_data()

    async def handle_presence_button(self) -> None:
        """Gerencia a lógica de confirmar ou desmarcar presença no evento com base no estado atual, atualizando o banco de dados e recarregando os dados sociais após a ação."""
        if event_participation_service.check_presence(self.user_id, self.event_id):
            success, message = event_participation_service.cancel_presence(
                self.user_id,
                self.event_id
            )
        else:
            success, message = event_participation_service.confirm_presence(
                self.user_id,
                self.event_id
            )

        self.app.notify(message)

        if success:
            await self.reload_event_social_data()