import sqlite3
from datetime import datetime
from services.important_dates_policy import ImportantDatesPolicy

class EventImportantDatesRepository:
    """
    Repositório responsável por manipular as datas importantes dos eventos.
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def replace_auto_generated_dates(self, event_id: int, important_dates: list[dict]) -> None:
        """
        Substitui as datas automáticas de um evento pelas datas mais recentes.

        Datas manuais podem ser preservadas usando is_auto_generated = 0.
        """

        cursor = self.connection.cursor()
        now = datetime.now().isoformat(timespec="seconds")
        cursor.execute(
            """
            DELETE FROM event_important_dates
            WHERE event_id = ?
              AND is_auto_generated = 1;
            """,
            (event_id,)
        )

        for item in important_dates:
            if item.get("ignore"):
                continue

            confidence = float(item.get("confidence", 0.0))

            cursor.execute(
                """
                INSERT INTO event_important_dates (
                    event_id,
                    title,
                    date,
                    time,
                    source_url,
                    confidence,
                    is_confirmed,
                    is_auto_generated,
                    last_checked_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event_id,
                    item.get("title", "Data importante"),
                    item["date"],
                    item.get("time"),
                    item.get("source_url"),
                    confidence,
                    1 if confidence >= 0.85 else 0,
                    1,
                    now,
                    now,
                )
            )

        self.connection.commit()

    def find_by_event_id(self, event_id: int) -> list[dict]:
        """
        Retorna todas as datas importantes de um evento.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                date,
                time,
                source_url,
                confidence,
                is_confirmed,
                is_auto_generated,
                last_checked_at
            FROM event_important_dates
            WHERE event_id = ?
            ORDER BY date ASC, time ASC;
            """,
            (event_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "date": row[2],
                "time": row[3],
                "source_url": row[4],
                "confidence": float(row[5]),
                "is_confirmed": bool(row[6]),
                "is_auto_generated": bool(row[7]),
                "last_checked_at": row[8],
            }
            for row in rows
        ]

    def get_display_dates_by_event_id(self, event_id: int) -> list[dict]:
        """
        Retorna datas importantes limpas para exibição na tela de detalhes.

        Remove datas genéricas, normaliza títulos e organiza por categoria.
        """

        items = self.find_by_event_id(event_id)
        cleaned_items: list[dict] = []
        seen: set[tuple[str, str, str]] = set()

        for item in items:
            category = ImportantDatesPolicy.classify_title(
                item.get("title", "")
            )

            if category == "ignore":
                continue

            date = item.get("date")

            if not self._is_valid_iso_date(date):
                continue

            normalized_title = ImportantDatesPolicy.normalize_title(
                item["title"]
            )

            key = (category, normalized_title, date)

            if key in seen:
                continue

            seen.add(key)

            cleaned_items.append({
                **item,
                "title": normalized_title,
                "category": category,
                "category_label": ImportantDatesPolicy.category_label(category),
                "sort_order": ImportantDatesPolicy.sort_order(category),
            })

        has_submission = any(
            item["category"] in {
                "submission_abstract",
                "submission_article",
            }
            for item in cleaned_items
        )

        if not has_submission:
            return []

        cleaned_items.sort(
            key=lambda item: (
                item["sort_order"],
                item["date"],
                item["title"],
            )
        )

        return cleaned_items[: ImportantDatesPolicy.MAX_DISPLAY_DATES]

    def get_submission_status(self, event_id: int) -> dict:
        """
        Retorna um status geral de submissão.

        Mantido por compatibilidade com outras partes do sistema.
        A tela principal de eventos deve preferir get_submission_statuses().
        """

        statuses = self.get_submission_statuses(event_id)

        valid_statuses = [
            status
            for status in statuses
            if status.get("status") not in {"unknown", "track_specific"}
        ]

        if not valid_statuses:
            return statuses[0]

        valid_statuses.sort(
            key=lambda status: status.get("deadline_date") or "",
            reverse=True,
        )

        return valid_statuses[0]

    def get_submission_statuses(self, event_id: int) -> list[dict]:
        """
        Retorna os status separados das datas de submissão.

        Regras:
        - SBBD mostra resumos/artigos de completos e curtos.
        - Eventos com trilhas genéricas mostram aviso para consultar o site.
        - Eventos simples mostram Resumos e Artigos normalmente.
        """

        items = self.get_display_dates_by_event_id(event_id)

        if not items:
            return [
                self._build_submission_status(
                    status="unknown",
                    short_message="⚪ Sem submissão publicada",
                    message=(
                        "Nenhuma data de submissão de resumo ou artigo "
                        "foi identificada."
                    ),
                )
            ]

        source_url = items[0].get("source_url") or ""

        if "sbbd.org.br/2026/trilha-principal" in source_url.lower():
            return self._build_sbbd_submission_statuses(items)

        has_track_specific_dates = ImportantDatesPolicy.has_track_specific_dates(
            items,
            source_url,
        )

        abstract_dates = self._get_dates_by_category(
            items,
            "submission_abstract",
        )

        article_dates = self._get_dates_by_category(
            items,
            "submission_article",
        )

        has_multiple_submission_dates = (
            len(abstract_dates) > 1
            or len(article_dates) > 1
        )

        if has_track_specific_dates or has_multiple_submission_dates:
            return [
                self._build_submission_status(
                    status="track_specific",
                    short_message="⚠️ Consulte as datas por trilha no site oficial",
                    message=(
                        "Este evento possui trilhas, modalidades ou várias datas "
                        "de submissão. Consulte o site oficial para verificar a "
                        "data correta da trilha desejada."
                    ),
                )
            ]

        statuses: list[dict] = []

        if abstract_dates:
            statuses.append(
                self._build_submission_status_by_date(
                    label="Resumos",
                    deadline_date=abstract_dates[0],
                )
            )

        if article_dates:
            statuses.append(
                self._build_submission_status_by_date(
                    label="Artigos",
                    deadline_date=article_dates[0],
                )
            )

        if not statuses:
            return [
                self._build_submission_status(
                    status="unknown",
                    short_message="⚪ Sem submissão publicada",
                    message=(
                        "Nenhuma data de submissão de resumo ou artigo "
                        "foi identificada."
                    ),
                )
            ]

        return statuses

    def _build_sbbd_submission_statuses(self, items: list[dict]) -> list[dict]:
        """
        Monta os quatro status específicos do SBBD:

        - Resumos completos
        - Artigos completos
        - Resumos curtos
        - Artigos curtos
        """

        expected_dates = [
            (
                "submission_abstract",
                "artigos completos",
                "Resumos completos",
            ),
            (
                "submission_article",
                "artigos completos",
                "Artigos completos",
            ),
            (
                "submission_abstract",
                "artigos curtos",
                "Resumos curtos",
            ),
            (
                "submission_article",
                "artigos curtos",
                "Artigos curtos",
            ),
        ]

        statuses: list[dict] = []

        for category, title_part, label in expected_dates:
            deadline_date = self._get_latest_date_by_category_and_title_part(
                items,
                category,
                title_part,
            )

            if not deadline_date:
                continue

            statuses.append(
                self._build_submission_status_by_date(
                    label=label,
                    deadline_date=deadline_date,
                )
            )

        if not statuses:
            return [
                self._build_submission_status(
                    status="unknown",
                    short_message="⚪ Sem submissão publicada",
                    message=(
                        "Nenhuma data de submissão de resumo ou artigo "
                        "foi identificada para o SBBD."
                    ),
                )
            ]

        return statuses

    def _get_latest_date_by_category_and_title_part(self, items: list[dict], category: str, title_part: str):
        """
        Busca a maior data de uma categoria específica e com um trecho no título.
        Exemplo:
        category = "submission_article"
        title_part = "artigos curtos"
        """

        dates = []

        normalized_title_part = ImportantDatesPolicy._normalize_text(
            title_part)

        for item in items:
            if item.get("category") != category:
                continue

            title = ImportantDatesPolicy._normalize_text(
                item.get("title", "")
            )

            if normalized_title_part not in title:
                continue

            parsed_date = self._parse_iso_date(item.get("date"))

            if parsed_date:
                dates.append(parsed_date)

        if not dates:
            return None

        return max(dates)

    def _get_dates_by_category(self, items: list[dict], category: str) -> list:
        """
        Retorna todas as datas de uma categoria específica.
        """

        dates = []

        for item in items:
            if item.get("category") != category:
                continue

            parsed_date = self._parse_iso_date(item.get("date"))

            if parsed_date:
                dates.append(parsed_date)

        dates.sort()
        return dates

    def _build_submission_status_by_date(self, label: str, deadline_date) -> dict:
        """
        Monta o status visual para uma data específica de submissão.
        """

        today = datetime.now().date()
        warning_days = 15
        days_until_deadline = (deadline_date - today).days
        formatted_date = self._format_date(deadline_date)

        if days_until_deadline < 0:
            return self._build_submission_status(
                status="closed",
                short_message=f"🔴 {label}: {formatted_date}",
                message=f"{label} encerrado em {formatted_date}.",
                deadline_date=deadline_date.isoformat(),
                days_until_deadline=days_until_deadline,
            )

        if days_until_deadline == 0:
            return self._build_submission_status(
                status="closing_soon",
                short_message=f"🟡 {label}: hoje",
                message=f"{label} encerra hoje.",
                deadline_date=deadline_date.isoformat(),
                days_until_deadline=days_until_deadline,
            )

        if days_until_deadline <= warning_days:
            return self._build_submission_status(
                status="closing_soon",
                short_message=f"🟡 {label}: {formatted_date}",
                message=f"{label} encerra em {days_until_deadline} dias.",
                deadline_date=deadline_date.isoformat(),
                days_until_deadline=days_until_deadline,
            )

        return self._build_submission_status(
            status="open",
            short_message=f"🟢 {label}: {formatted_date}",
            message=f"{label} aberto até {formatted_date}.",
            deadline_date=deadline_date.isoformat(),
            days_until_deadline=days_until_deadline,
        )

    def _parse_iso_date(self, value: str | None):
        """Tenta converter uma string ISO para um objeto date. Retorna None se falhar."""
        if not value:
            return None

        try:
            return datetime.fromisoformat(value).date()
        except (TypeError, ValueError):
            return None

    def _is_valid_iso_date(self, value: str | None) -> bool:
        """Verifica se uma string é uma data ISO válida."""
        return self._parse_iso_date(value) is not None

    def _format_date(self, value) -> str:
        """Formata um objeto date para o formato dd/mm/yyyy."""
        return value.strftime("%d/%m/%Y")

    def _build_submission_status(
        self,
        status: str,
        short_message: str,
        message: str,
        opening_date: str | None = None,
        deadline_date: str | None = None,
        days_until_deadline: int | None = None,
    ) -> dict:
        """Constrói um dicionário de status de submissão com as informações fornecidas."""
        return {
            "status": status,
            "short_message": short_message,
            "message": message,
            "opening_date": opening_date,
            "deadline_date": deadline_date,
            "days_until_deadline": days_until_deadline,
        }