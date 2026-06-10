import sqlite3
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical, VerticalScroll, Horizontal
from database.repositories.event_important_dates_repository import EventImportantDatesRepository
from database.repositories.event_repository import event_services
from screens.events.delete_social_event_view import DeleteSocialEventView
from screens.events.edit_social_event_view import EditSocialEventView
from database.repositories.event_participation import event_participation_service


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

.section_title {
    text-style: bold;
    margin-bottom: 1;
}

.social_text,
.empty_state,
.info_value {
    color: $text-muted;
    margin-top: 1;
}

.info_label {
    margin-top: 1;
    text-style: bold;
}

#important_dates_list {
    color: $text-muted;
    margin-top: 1;
}
"""


class MyEventDetailsView(Screen):
    """
    Tela de detalhes do evento criado pelo usuário.
    """

    CSS = MY_EVENT_DETAILS_VIEW

    def __init__(self, event_id: int, user_id: int):
        """Inicializa a tela de detalhes do evento criado pelo usuário."""
        super().__init__()
        self.event_id = event_id
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        """Estrutura a interface da tela de detalhes do evento criado pelo usuário."""
        event = event_services.check_event(self.event_id)
        total_presence = event_participation_service.count_confirmed_presence(
            self.event_id)
        total_favorites = event_participation_service.count_favorites(
            self.event_id)

        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static(f"Evento: {event.name}", id="top_title")
                    yield Static("")
                yield Static(
                    "Veja as informações do seu evento criado. Você pode editar ou excluir o evento usando os botões abaixo."
                )

                with Vertical(classes="section_card"):
                    yield Static("Informações do evento", classes="section_title")

                    yield Static("Descrição:", classes="info_label")
                    yield Static(event.description, classes="info_value")

                    yield Static("Local:", classes="info_label")
                    yield Static(
                        event.event_location or "O local do evento ainda não está disponível.",
                        classes="info_value"
                    )

                    yield Static("Data:", classes="info_label")
                    yield Static(
                        event.date or "A data do evento ainda não está disponível.",
                        classes="info_value"
                    )

                    yield Static("Hora:", classes="info_label")
                    yield Static(
                        event.hour or "A hora do evento ainda não foi divulgada.",
                        classes="info_value"
                    )

                    yield Static("Fonte oficial:", classes="info_label")
                    yield Static(
                        event.official_url or "Nenhum link oficial cadastrado.",
                        classes="info_value"
                    )

                with Vertical(classes="section_card"):
                    yield Static("Datas importantes", classes="section_title")
                    yield Static(
                        "Carregando datas importantes...",
                        id="important_dates_list"
                    )

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
                    yield Static("Ações do evento:", classes="section_title")
                    yield Button("Editar Evento", id="button_edit_event")
                    yield Button("Excluir Evento", id="button_delete_event", variant="error")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        """Carrega as datas importantes e os dados sociais do evento ao montar a tela."""
        self.load_important_dates()
        await self.reload_event_social_data()

    async def on_screen_resume(self) -> None:
        """Recarrega as datas importantes e os dados sociais do evento ao retornar para a tela."""
        self.load_important_dates()
        await self.reload_event_social_data()

    def load_important_dates(self) -> None:
        """Carrega as datas importantes do evento e atualiza a interface."""
        dates_widget = self.query_one("#important_dates_list", Static)

        with sqlite3.connect(event_services.database_path) as connection:
            repository = EventImportantDatesRepository(connection)
            important_dates = repository.find_by_event_id(self.event_id)

        if not important_dates:
            dates_widget.update(
                "Nenhuma data importante encontrada ainda. Cadastre um link oficial para permitir a busca automática."
            )
            return

        formatted_dates = []

        for item in important_dates:
            confidence_percent = int(item["confidence"] * 100)
            status = "confirmada" if item["is_confirmed"] else "precisa de confirmação"
            time_text = f" às {item['time']}" if item["time"] else ""
            checked_text = self._format_datetime(item["last_checked_at"])

            formatted_dates.append(
                f"• {item['title']}: {self._format_date(item['date'])}{time_text} "
                f"({confidence_percent}% de confiança, {status})\n"
                f"  Fonte: {item['source_url'] or 'não informada'}\n"
                f"  Atualizado em: {checked_text}"
            )

        dates_widget.update("\n\n".join(formatted_dates))

    def _format_date(self, iso_date: str) -> str:
        """Formata uma data no formato ISO (YYYY-MM-DD) para o formato DD/MM/YYYY."""
        year, month, day = iso_date.split("-")
        return f"{day}/{month}/{year}"

    def _format_datetime(self, iso_datetime: str | None) -> str:
        """Formata uma data e hora no formato ISO (YYYY-MM-DDTHH:MM:SS) para o formato DD/MM/YYYY às HH:MM."""
        if not iso_datetime:
            return "não informado"

        try:
            parsed_datetime = datetime.fromisoformat(iso_datetime)
            return parsed_datetime.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return iso_datetime

    async def reload_event_social_data(self) -> None:
        """Recarrega os dados sociais do evento, incluindo o resumo social, a presença dos amigos e os favoritos dos amigos."""
        await self.reload_social_summary()
        await self.reload_friends_presence()
        await self.reload_friends_favorites()

    async def reload_social_summary(self) -> None:
        """Recarrega o resumo social do evento."""
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
        """Trata os eventos de clique nos botões da tela, permitindo editar, excluir o evento ou navegar para a tela inicial."""
        if event.button.id == "button_edit_event":
            self.app.push_screen(EditSocialEventView(self.event_id))

        elif event.button.id == "button_delete_event":
            self.app.push_screen(DeleteSocialEventView(self.event_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id == "home_button":
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.pop_screen()