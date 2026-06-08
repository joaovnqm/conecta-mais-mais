from typing import Any
import sqlite3
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Select, Static
from database.repositories.event_important_dates_repository import (EventImportantDatesRepository)
from database.repositories.event_repository import event_services
from database.repositories.interest_repository import interest_services
from screens.events.event_details_view import EventDetailsView


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
    min-height: 4;
    margin-bottom: 1;
}

.event_buttons {
    width: 100%;
    height: 4;
}

.submission_badges {
    width: 100%;
    height: auto;
    padding: 0 1;
}

.submission_badge_line {
    width: 100%;
    height: auto;
    min-height: 1;
    content-align: left middle;
    text-style: bold;
}

.status_open {
    color: green;
}

.status_closing_soon {
    color: yellow;
}

.status_closed {
    color: red;
}

.status_not_started {
    color: cyan;
}

.status_track_specific {
    color: yellow;
}

.status_unknown {
    color: $text-muted;
    text-style: none;
}

#button_return {
    width: 100%;
    margin-top: 2;
}
"""


class EventsView(Screen):
    """
    Tela de listagem de eventos.

    Exibe:
    - busca por nome do evento;
    - filtro por interesse;
    - lista de eventos disponíveis;
    - status de submissão de resumos/artigos quando a data for simples;
    - aviso para consultar o site oficial quando houver trilhas, tracks,
      modalidades ou múltiplas datas de submissão.
    """

    CSS = EVENTS_PAGE_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        events = event_services.check_events_by_interests(self.user_id)
        interests = interest_services.check_user_interests(self.user_id)

        select_options = [("Todos os Eventos", "all_events")] + [
            (interest.name, interest.name)
            for interest in interests
            if interest.name != "Social"
        ]

        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Eventos", id="main_title")

                yield Static("Buscar evento:")
                yield Input(
                    placeholder="Insira o nome do evento...",
                    id="search_event",
                )

                yield Static("Filtrar por interesse:")
                yield Select(
                    select_options,
                    value="all_events",
                    allow_blank=False,
                )

                yield Static(
                    "Clique em algum evento abaixo para saber mais.",
                    classes="main_subtitle",
                )

                with VerticalScroll(id="events_container"):
                    if events:
                        for event in events:
                            yield self._build_event_row(event)
                    else:
                        yield Static(
                            "Nenhum evento encontrado.",
                            classes="main_subtitle",
                        )

                yield Button("Voltar", id="button_return", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Trata cliques nos botões da tela.
        """

        if event.button.has_class("event_buttons"):
            button_id = event.button.id or ""

            if "_" not in button_id:
                return

            event_id = str(button_id.split("_", maxsplit=1)[1])
            self.app.push_screen(EventDetailsView(self.user_id, event_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """
        Reaplica os filtros quando o usuário digita no campo de busca.
        """

        if event.input.id == "search_event":
            await self._apply_filters()

    async def on_select_changed(self, event: Select.Changed) -> None:
        """
        Reaplica os filtros quando o usuário altera o interesse selecionado.
        """

        await self._apply_filters()

    async def _apply_filters(self) -> None:
        """
        Aplica filtro por interesse e busca por nome.
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
            result = [
                event
                for event in result
                if search_term in event.name.lower()
            ]

        await self.update_events_on_screen(result)

    async def update_events_on_screen(self, result) -> None:
        """
        Atualiza a lista de eventos após busca ou filtro.
        """

        container = self.query_one("#events_container")
        await container.remove_children()

        if not result:
            await container.mount(
                Static(
                    "Eventos com filtros selecionados não disponíveis no momento.",
                    classes="main_subtitle",
                )
            )
            return

        for event in result:
            await container.mount(self._build_event_row(event))

    def _build_event_row(self, event) -> Horizontal:
        """
        Monta uma linha da listagem com:
        - botão do evento;
        - status de submissão ou aviso de trilhas/modalidades.
        """

        return Horizontal(
            Button(
                event.name,
                id=f"event_{event.event_id}",
                classes="event_buttons",
            ),
            self._build_submission_badges(event.event_id),
            classes="event_listing",
        )

    def _build_submission_badges(self, event_id: int) -> Vertical:
        """
        Monta os status resumidos da submissão.

        Pode exibir:
        - Resumos;
        - Artigos;
        - aviso para consultar site oficial;
        - sem submissão publicada.
        """

        statuses = self._get_submission_statuses_safe(event_id)

        status_widgets = []

        for status in statuses:
            status_name = status.get("status", "unknown")

            status_text = (
                status.get("short_message")
                or status.get("message")
                or "⚪ Sem submissão publicada"
            )

            css_class = self._get_submission_status_class(status_name)

            status_widgets.append(
                Static(
                    status_text,
                    classes=f"submission_badge_line {css_class}",
                )
            )

        return Vertical(
            *status_widgets,
            classes="submission_badges",
        )

    def _get_submission_statuses_safe(self, event_id: int) -> list[dict[str, Any]]:
        """
        Consulta os status de submissão.

        Se der erro, retorna um status neutro para não quebrar a tela.
        """

        try:
            with sqlite3.connect(event_services.database_path) as connection:
                repository = EventImportantDatesRepository(connection)

                if hasattr(repository, "get_submission_statuses"):
                    return repository.get_submission_statuses(event_id)

                return [repository.get_submission_status(event_id)]

        except sqlite3.Error:
            return [
                {
                    "status": "unknown",
                    "short_message": "⚪ Status indisponível",
                    "message": "Não foi possível consultar as datas de submissão.",
                    "opening_date": None,
                    "deadline_date": None,
                    "days_until_deadline": None,
                }
            ]

    def _get_submission_status_class(self, status: str) -> str:
        """
        Converte o status lógico em classe CSS.
        """

        status_classes = {
            "open": "status_open",
            "closing_soon": "status_closing_soon",
            "closed": "status_closed",
            "not_started": "status_not_started",
            "open_no_deadline": "status_open",
            "track_specific": "status_track_specific",
            "unknown": "status_unknown",
            "none": "status_unknown",
        }

        return status_classes.get(status, "status_unknown")
