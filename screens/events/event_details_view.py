import sqlite3
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Checkbox
from textual.containers import Center, VerticalScroll, Vertical, Horizontal
from database.repositories.event_important_dates_repository import EventImportantDatesRepository
from services.important_dates_policy import ImportantDatesPolicy
from database.repositories.event_repository import event_services
from database.repositories.user_repository import user_services
from database.repositories.interest_repository import interest_services
from database.repositories.ranking_repository import ranking_repository_services
from services.favorite_events import favorite_events_services
from database.repositories.event_participation import event_participation_service
from services.event_certificate import certificate_service
from services.add_event_to_calendar import calendar_service

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
#friends_favorites_container{
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

.activities.-on {
    color: limegreen 90%;
}

.activities.-on > .toggle--button {
    color: limegreen 90%;
}

.language_buttons {
    width: 100%;
    height: auto;
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

#button_return {
    width: 100%;
    margin-top: 1;
}

.language_buttons {
    width: 100%;
    height: auto;
    content-align: center middle;
}

.language_buttons Button {
    width: 1fr;
    margin: 1;
    content-align: center middle;
}
"""

RANKING_POINTS = {
    "presence_confirmed": 15,
    "article_publication": 40,
    "lecture_presentation": 70,
    "mini_course": 30,
    "workshop": 30,
    "certificate_presence": 25,
}


ACTIVITY_OPTIONS = {
    "activity_article_publication": {
        "label": "Publicação de Artigo",
        "ranking_action": "article_publication",
    },
    "activity_lecture_presentation": {
        "label": "Apresentação de Palestra",
        "ranking_action": "lecture_presentation",
    },
    "activity_mini_course": {
        "label": "Minicurso",
        "ranking_action": "mini_course",
    },
    "activity_workshop": {
        "label": "Workshop",
        "ranking_action": "workshop",
    },
}

class EventDetailsView(Screen):
    """
    Tela responsável por exibir detalhes do evento e permitir ações sociais.
    """

    CSS = EVENT_DETAILS_VIEW

    def __init__(self, user_id: int, event_id: int):
        """Inicializa a tela de detalhes do evento com o ID do usuário e do evento, além de preparar o repositório de ranking para futuras atualizações de pontos."""
        super().__init__()
        self.user_id = int(user_id)
        self.event_id = int(event_id)
        self.ranking_repository = ranking_repository_services

    def compose(self) -> ComposeResult:
        """Composição da tela de detalhes do evento."""
        event = event_services.check_event(self.event_id)
        creator_name = user_services.check_user_name(event.creator_id)
        interests = interest_services.check_event_interests(event.event_id)

        total_presence = event_participation_service.count_confirmed_presence(
            self.event_id
        )
        total_favorites = event_participation_service.count_favorites(
            self.event_id
        )

        event_date_object = (
            datetime.strptime(event.date, "%d-%m-%Y").date()
            if event.date
            else None
        )

        today = datetime.now().date()

        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static(f"Detalhes do Evento: {event.name}", id="top_title")
                    yield Static("")

                yield Static(
                    "Veja os detalhes do evento e acompanhe a atividade dos seus amigos.",
                    classes="subtitle",
                )

                with Vertical(classes="section_card"):
                    yield Static("Informações do evento", classes="section_title")

                    yield Static("Descrição:", classes="info_label")
                    yield Static(event.description, classes="info_value")

                    yield Static("Local:", classes="info_label")
                    yield Static(
                        event.event_location or "O local do evento ainda não está disponível.",
                        classes="info_value",
                    )

                    yield Static("Data:", classes="info_label")
                    yield Static(
                        event.date or "A data do evento ainda não está disponível.",
                        classes="info_value",
                    )

                    yield Static("Hora:", classes="info_label")
                    yield Static(
                        event.hour or "A hora do evento ainda não foi divulgada.",
                        classes="info_value",
                    )

                    yield Static("Criador:", classes="info_label")
                    yield Static(
                        creator_name or "Criador não encontrado.",
                        classes="info_value",
                    )

                    yield Static("Fonte oficial:", classes="info_label")
                    yield Static(
                        event.official_url or "Nenhum link oficial cadastrado.",
                        classes="info_value",
                    )

                with Vertical(classes="section_card"):
                    yield Static("Datas importantes", classes="section_title")
                    yield Static(
                        "Carregando datas importantes...",
                        id="important_dates_list",
                    )

                if event_date_object is None or event_date_object >= today:
                    with Vertical(classes="section_card"):
                        yield Static("Ações do evento:", classes="section_title")
                        yield Vertical(id="favorite_button_container")
                        yield Vertical(id="presence_button_container")
                        yield Vertical(id="activities_container")

                else:
                    user_confirmed_presence = event_participation_service.check_presence(
                        self.user_id,
                        event.event_id,
                    )

                    is_social_event = (
                        interests
                        and any(
                            interest.name.lower() == "social"
                            for interest in interests
                        )
                    )

                    if user_confirmed_presence and not is_social_event:
                        with Vertical(classes="section_card"):
                            yield Static(
                                "Você participou deste evento, envie o seu certificado de participação para o " \
                                "seu e-mail através do botão abaixo. Você pode emitir o certificado em português ou em inglês. \n"
                            )
                            
                            with Horizontal(classes="language_buttons"):
                                yield Button(
                                    "Emitir Certificado em Português",
                                    id="button_certificate_emission_portuguese",
                                    variant="success",
                                )
                                yield Button(
                                    "Emitir Certificado em Inglês",
                                    id="button_certificate_emission_english",
                                    variant="success",
                                )

                    else:
                        with Vertical(classes="section_card"):
                            yield Static(
                                "Esse evento já aconteceu. Não é mais possível confirmar presença ou favoritar o evento, mas você pode conferir o resumo social e as datas importantes cadastradas."
                            )

                with Vertical(classes="section_card"):
                    yield Static("Resumo social", classes="section_title")

                    yield Static(
                        f"Pessoas com presença confirmada: {total_presence}",
                        id="presence_count",
                        classes="social_text",
                    )

                    yield Static(
                        f"Pessoas que favoritaram: {total_favorites}",
                        id="favorite_count",
                        classes="social_text",
                    )

                with Vertical(classes="section_card"):
                    yield Static("Amigos que vão", classes="section_title")
                    yield Vertical(id="friends_presence_container")

                with Vertical(classes="section_card"):
                    yield Static("Amigos que favoritaram", classes="section_title")
                    yield Vertical(id="friends_favorites_container")

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_mount(self) -> None:
        """Carrega as datas importantes e os dados sociais do evento ao montar a tela."""
        self.load_important_dates()
        await self.reload_event_social_data()

    async def on_screen_resume(self) -> None:
        """Atualiza as datas importantes e os dados sociais do evento ao retornar para a tela."""
        self.load_important_dates()
        await self.reload_event_social_data()

    def load_important_dates(self) -> None:
        """
        Carrega datas importantes limpas e organizadas por categoria.

        Observação:
        O status resumido de submissão aparece somente na tela principal
        de eventos. Aqui ficam apenas as datas importantes do evento,
        separadas por categoria e com aviso destacado quando houver trilhas,
        tracks ou modalidades específicas.
        """

        dates_widget = self.query_one("#important_dates_list", Static)

        with sqlite3.connect(event_services.database_path) as connection:
            repository = EventImportantDatesRepository(connection)
            important_dates = repository.get_display_dates_by_event_id(self.event_id)

        if not important_dates:
            dates_widget.update(
                "Nenhuma data importante confiável foi encontrada para este evento."
            )
            return

        grouped_dates: dict[str, list[dict]] = {}

        for item in important_dates:
            grouped_dates.setdefault(item["category_label"], []).append(item)

        group_order = [
            "Submissões",
            "Pós-submissão",
            "Evento",
            "Outras datas",
        ]

        formatted_sections: list[str] = []

        for group_name in group_order:
            group_items = grouped_dates.get(group_name)

            if not group_items:
                continue

            section_lines = [group_name.upper()]

            for item in group_items:
                time_text = f" às {item['time']}" if item["time"] else ""

                section_lines.append(
                    f"• {item['title']}: {self._format_date(item['date'])}{time_text}"
                )

            formatted_sections.append("\n".join(section_lines))

        source_url = important_dates[0].get("source_url") or "não informada"
        checked_text = self._format_datetime(
            important_dates[0].get("last_checked_at")
        )

        final_sections = formatted_sections.copy()

        if ImportantDatesPolicy.has_track_specific_dates(
            important_dates,
            source_url,
        ):
            final_sections.insert(
                0,
                ImportantDatesPolicy.get_track_specific_dates_notice(),
            )

        footer = (
            f"Fonte oficial: {source_url}\n"
            f"Atualizado em: {checked_text}"
        )

        final_sections.append(footer)

        dates_widget.update("\n\n".join(final_sections))

    def _format_date(self, iso_date: str) -> str:
        """Formata data do formato ISO (AAAA-MM-DD) para o formato brasileiro (DD/MM/AAAA)."""
        year, month, day = iso_date.split("-")
        return f"{day}/{month}/{year}"

    def _format_datetime(self, iso_datetime: str | None) -> str:
        """Formata data e hora do formato ISO para o formato brasileiro, ou retorna um texto padrão se a data for nula ou inválida."""
        if not iso_datetime:
            return "não informado"

        try:
            parsed_datetime = datetime.fromisoformat(iso_datetime)
            return parsed_datetime.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return iso_datetime

    async def reload_event_social_data(self) -> None:
        """Recarrega os dados sociais do evento, incluindo status de presença, favoritos e atividades extras."""
        await self.reload_favorite_button()
        await self.reload_presence_button()
        await self.reload_social_summary()
        await self.reload_friends_presence()
        await self.reload_friends_favorites()
        await self.reload_activity_checkboxes()

    async def reload_favorite_button(self) -> None:
        """Atualiza o botão de favorito com base no status atual do evento para o usuário."""
        try:
            container = self.query_one("#favorite_button_container")
        except Exception:
            return

        await container.remove_children()

        if favorite_events_services.check_favorite_event(self.user_id, self.event_id):
            await container.mount(
                Button(
                    "Desfavoritar evento",
                    id="button_favorite_event",
                    variant="default",
                )
            )
        else:
            await container.mount(
                Button(
                    "★ Favoritar evento",
                    id="button_favorite_event",
                    variant="warning",
                )
            )

    async def reload_presence_button(self) -> None:
        """Atualiza o botão de presença com base no status atual do evento para o usuário."""
        try:
            container = self.query_one("#presence_button_container")
        except Exception:
            return

        await container.remove_children()

        if event_participation_service.check_presence(self.user_id, self.event_id):
            await container.mount(
                Button(
                    "Desmarcar presença",
                    id="button_presence_event",
                    variant="error",
                )
            )
        else:
            await container.mount(
                Button(
                    "Confirmar presença",
                    id="button_presence_event",
                    variant="success",
                )
            )

    async def reload_social_summary(self) -> None:
        """Atualiza o resumo social do evento, incluindo contagem de presença confirmada e favoritos."""
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
        """Atualiza a lista de amigos com presença confirmada no evento."""
        container = self.query_one("#friends_presence_container")
        await container.remove_children()

        friends = event_participation_service.list_friends_confirmed_presence(
            self.user_id,
            self.event_id,
        )

        if not friends:
            await container.mount(
                Static(
                    "Nenhum amigo confirmou presença neste evento.",
                    classes="empty_state",
                )
            )
            return

        for friend in friends:
            await container.mount(
                Static(
                    f"{friend['name']} - @{friend['username']}",
                    classes="social_text",
                )
            )

    async def reload_friends_favorites(self) -> None:
        """Atualiza a lista de amigos que favoritaram o evento."""
        container = self.query_one("#friends_favorites_container")
        await container.remove_children()

        friends = event_participation_service.list_friends_favorited_event(
            self.user_id,
            self.event_id,
        )

        if not friends:
            await container.mount(
                Static(
                    "Nenhum amigo favoritou este evento.",
                    classes="empty_state",
                )
            )
            return

        for friend in friends:
            await container.mount(
                Static(
                    f"{friend['name']} - @{friend['username']}",
                    classes="social_text",
                )
            )

    async def reload_activity_checkboxes(self) -> None:
        """
        Atualiza o container de atividades extras.

        Os checkboxes só aparecem antes da confirmação de presença.
        Depois que o usuário confirma presença, as atividades ficam salvas
        em event_participation_service.confirm_presence().
        """

        try:
            container = self.query_one("#activities_container")
        except Exception:
            return

        await container.remove_children()

        interests = interest_services.check_event_interests(self.event_id)

        user_has_presence = event_participation_service.check_presence(
            self.user_id,
            self.event_id,
        )

        is_social_event = (
            interests
            and any(
                interest.name.lower() == "social"
                for interest in interests
            )
        )

        if user_has_presence or is_social_event:
            return

        await container.mount(
            Static(
                "Você planeja participar de algumas das seguintes atividades extras caso elas aconteçam?",
                classes="info_label",
            )
        )

        await container.mount(
            Checkbox(
                "Publicação de Artigo",
                id="activity_article_publication",
                classes="activities",
            )
        )

        await container.mount(
            Checkbox(
                "Apresentação de Palestra",
                id="activity_lecture_presentation",
                classes="activities",
            )
        )

        await container.mount(
            Checkbox(
                "Minicurso",
                id="activity_mini_course",
                classes="activities",
            )
        )

        await container.mount(
            Checkbox(
                "Workshop",
                id="activity_workshop",
                classes="activities",
            )
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Trata cliques nos botões da tela de detalhes do evento, direcionando para a função de tratamento correspondente a cada ação."""
        if event.button.id == "button_favorite_event":
            await self.handle_favorite_button()
            return

        elif event.button.id == "button_presence_event":
            await self.handle_presence_button()
            return

        elif event.button.id == "button_certificate_emission_portuguese":
            await self.handle_certificate_emission(lang="pt")
            return

        elif event.button.id == "button_certificate_emission_english":
            await self.handle_certificate_emission(lang="en")
            return

        elif event.button.id == "button_return":
            self.app.pop_screen()
            return
        
        elif event.button.id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()

    async def handle_favorite_button(self) -> None:
        """Favoritar não gera pontos no ranking."""
        if favorite_events_services.check_favorite_event(self.user_id, self.event_id):
            success, message = favorite_events_services.remove_from_favorite_event(
                self.user_id,
                self.event_id,
            )
        else:
            success, message = favorite_events_services.favorite_event(
                self.user_id,
                self.event_id,
            )

        self.app.notify(message)

        if success:
            await self.reload_event_social_data()

    async def handle_presence_button(self) -> None:
        """Confirma ou cancela presença do usuário no evento."""
        if event_participation_service.check_presence(self.user_id, self.event_id):
            success, message = event_participation_service.cancel_presence(
                self.user_id,
                self.event_id,
            )

            self.app.notify(message)

            if success:
                await self.reload_event_social_data()

            return

        selected_extra_activities = self._get_selected_extra_activities()

        activities = ["Presença"]

        for activity in selected_extra_activities:
            activities.append(activity["label"])

        activities_text = "; ".join(activities)

        success, message = event_participation_service.confirm_presence(
            self.user_id,
            self.event_id,
            activities_text,
        )

        self.app.notify(message)

        if not success:
            return

        ranking_message = self._register_ranking_points_for_presence(
            selected_extra_activities
        )

        if ranking_message:
            self.app.notify(ranking_message)

        self._send_event_to_calendar()

        await self.reload_event_social_data()

    async def handle_certificate_emission(self, lang: str = "pt") -> None:
        """Emite certificado (idioma `lang`) e registra pontuação no ranking."""
        event_object = event_services.check_event(self.event_id)
        user = user_services.check_user(self.user_id)

        certificate_service.send_certificate(
            user_id=user.user_id,
            event_id=self.event_id,
            user_email=user.email,
            user_name=user.name,
            event_name=event_object.name,
            date=event_object.date,
            activities=event_participation_service.check_activities(
                self.user_id,
                self.event_id,
            ),
            lang=lang,
        )

        was_registered = self.ranking_repository.add_points_once(
            user_id=self.user_id,
            event_id=self.event_id,
            action_type="certificate_presence",
            points=RANKING_POINTS["certificate_presence"],
        )

        if was_registered:
            self.app.notify(
                f"Certificado emitido. +{RANKING_POINTS['certificate_presence']} pontos adicionados ao ranking."
            )
            
        else:
            self.app.notify(
                "Certificado emitido. A pontuação desse certificado já havia sido registrada."
            )

        await self.reload_event_social_data()

    def _get_selected_extra_activities(self) -> list[dict[str, str]]:
        """Retorna as atividades extras marcadas pelo usuário."""
        selected_activities: list[dict[str, str]] = []

        for checkbox in self.query(".activities"):
            if not isinstance(checkbox, Checkbox):
                continue

            if not checkbox.value:
                continue

            checkbox_id = checkbox.id

            if not checkbox_id:
                continue

            activity = ACTIVITY_OPTIONS.get(checkbox_id)

            if activity:
                selected_activities.append(activity)

        return selected_activities

    def _register_ranking_points_for_presence(self, selected_extra_activities: list[dict[str, str]]) -> str:
        """Registra pontos da presença e das atividades extras."""
        gained_points = 0
        registered_labels: list[str] = []
        duplicated_labels: list[str] = []
        presence_was_registered = self.ranking_repository.add_points_once(
            user_id=self.user_id,
            event_id=self.event_id,
            action_type="presence_confirmed",
            points=RANKING_POINTS["presence_confirmed"],
        )

        if presence_was_registered:
            gained_points += RANKING_POINTS["presence_confirmed"]
            registered_labels.append("presença confirmada")
        else:
            duplicated_labels.append("presença confirmada")

        for activity in selected_extra_activities:
            ranking_action = activity["ranking_action"]
            label = activity["label"]
            points = RANKING_POINTS[ranking_action]

            was_registered = self.ranking_repository.add_points_once(
                user_id=self.user_id,
                event_id=self.event_id,
                action_type=ranking_action,
                points=points,
            )

            if was_registered:
                gained_points += points
                registered_labels.append(label)
            else:
                duplicated_labels.append(label)

        if gained_points > 0:
            return (
                f"+{gained_points} pontos adicionados ao ranking: "
                f"{', '.join(registered_labels)}."
            )

        if duplicated_labels:
            return "Esses pontos já tinham sido registrados anteriormente."

        return ""

    def _send_event_to_calendar(self) -> None:
        """Envia o evento confirmado para o calendário do usuário."""
        try:
            user = user_services.check_user(self.user_id)
            event_object = event_services.check_event(self.event_id)

            if event_object.date and event_object.hour:
                start_time = datetime.strptime(
                    f"{event_object.date} {event_object.hour}",
                    "%d-%m-%Y %H:%M",
                )
            else:
                start_time = datetime.now()

            calendar_service.send_calendar_event(
                user_email=user.email,
                title=event_object.name,
                description=event_object.description or "",
                start_time=start_time,
            )

        except Exception as error:
            self.app.notify(
                f"Presença confirmada, mas não foi possível enviar para o calendário: {error}",
                severity="warning",
            )
