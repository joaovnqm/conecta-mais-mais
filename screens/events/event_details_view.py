import sqlite3
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Checkbox
from textual.containers import Center, VerticalScroll, Vertical
from database.repositories.event_important_dates_repository import EventImportantDatesRepository
from database.repositories.event_repository import event_services
from database.repositories.user_repository import user_services
from database.repositories.interest_repository import interest_services
from services.favorite_events import favorite_events_services
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
#activities_container,
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

#important_dates_list {
    color: $text-muted;
    margin-top: 1;
}

#button_favorite_event,
#button_presence_event {
    width: 100%;
    margin-top: 1;
    margin-bottom: 0;
}

#button_return,
#button_certificate_emission {
    width: 100%;
    margin-top: 1;
}
"""


class EventDetailsView(Screen):
    """
    Tela responsável por exibir detalhes do evento e permitir ações sociais.
    """

    CSS = EVENT_DETAILS_VIEW

    def __init__(self, user_id: int, event_id: int):
        super().__init__()
        self.user_id = user_id
        self.event_id = int(event_id)

    def compose(self) -> ComposeResult:
        event = event_services.check_event(self.event_id)
        creator_name = user_services.check_user_name(event.creator_id)
        interests = interest_services.check_event_interests(event.event_id)
        total_presence = event_participation_service.count_confirmed_presence(
            self.event_id)
        total_favorites = event_participation_service.count_favorites(
            self.event_id)
        event_date_object = datetime.strptime(event.date, "%d-%m-%Y").date() if event.date else None
        today = datetime.now().date()

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

                    yield Static("Criador:", classes="info_label")
                    yield Static(
                        creator_name or "Criador não encontrado.",
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

                if event_date_object is None or event_date_object >= today:
                    with Vertical(classes="section_card"):
                        yield Static("Ações do evento:", classes="section_title")
                        yield Vertical(id="favorite_button_container")
                        yield Vertical(id="presence_button_container")
                        yield Vertical(id="activities_container")
                
                else:
                    if event_participation_service.check_presence(self.user_id, event.event_id) and interests and not any(interest.name.lower() == "social" for interest in interests):
                        with Vertical(classes="section_card"):
                            yield Static("Você participou deste evento, envie o seu certificado de participação para o seu e-mail através do botão abaixo.")
                            yield Button("Emitir Certificado", id="button_certificate_emission", variant="success")
                    else:
                        with Vertical(classes="section_card"):
                            yield Static("Esse evento já aconteceu. Não é mais possível confirmar presença ou favoritar o evento, mas você pode conferir o resumo social e as datas importantes cadastradas.")

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
        self.load_important_dates()
        await self.reload_event_social_data()

    async def on_screen_resume(self) -> None:
        self.load_important_dates()
        await self.reload_event_social_data()

    def load_important_dates(self) -> None:
        """
        Carrega as datas importantes salvas no banco e exibe na tela.
        """

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
        year, month, day = iso_date.split("-")
        return f"{day}/{month}/{year}"

    def _format_datetime(self, iso_datetime: str | None) -> str:
        if not iso_datetime:
            return "não informado"

        try:
            parsed_datetime = datetime.fromisoformat(iso_datetime)
            return parsed_datetime.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return iso_datetime

    async def reload_event_social_data(self) -> None:
        await self.reload_favorite_button()
        await self.reload_presence_button()
        await self.reload_social_summary()
        await self.reload_friends_presence()
        await self.reload_friends_favorites()
        await self.reload_activity_checkboxes()

    async def reload_favorite_button(self) -> None:
            try:
                container = self.query_one("#favorite_button_container")
            except:
                return
            
            await container.remove_children()

            if favorite_events_services.check_favorite_event(self.user_id, self.event_id):
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
        try:
            container = self.query_one("#presence_button_container")
        except:
            return

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

    async def reload_activity_checkboxes(self) -> None:
        """
        Atualiza o container de atividades (checkboxes) de acordo com o estado de presença do usuário e os interesses do evento.
        """
        container = self.query_one("#activities_container")
        await container.remove_children()

        interests = interest_services.check_event_interests(self.event_id)
        if (not event_participation_service.check_presence(self.user_id, self.event_id)) \
                and interests and not any(interest.name.lower() == "social" for interest in interests):
            await container.mount(Static("Você planeja participar de algumas das seguintes atividades extras caso elas aconteçam?", classes="info_label"))
            await container.mount(Checkbox("Publicação de Artigo", id="article_presentation"))
            await container.mount(Checkbox("Apresentação de Palestra", id="speaker_presentation"))
            await container.mount(Checkbox("Minicurso", id="workshop"))
            await container.mount(Checkbox("Workshop", id="mini_course"))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
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
        if favorite_events_services.check_favorite_event(self.user_id, self.event_id):
            success, message = favorite_events_services.remove_from_favorite_event(
                self.user_id,
                self.event_id
            )
        else:
            success, message = favorite_events_services.favorite_event(
                self.user_id,
                self.event_id
            )

        self.app.notify(message)

        if success:
            await self.reload_event_social_data()

    async def handle_presence_button(self) -> None:
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
