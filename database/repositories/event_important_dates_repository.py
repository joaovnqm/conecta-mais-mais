import sqlite3
from datetime import datetime


class EventImportantDatesRepository:
    """
    Repositório responsável por manipular as datas importantes dos eventos.
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def replace_auto_generated_dates(
        self,
        event_id: int,
        important_dates: list[dict]
    ) -> None:
        """
        Substitui as datas automáticas de um evento pelas datas mais recentes
        encontradas na fonte oficial.

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
                    now
                )
            )

        self.connection.commit()

    def find_by_event_id(self, event_id: int) -> list[dict]:
        """
        Retorna todas as datas importantes de um evento, ordenadas por data.
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

        dates = cursor.fetchall()

        return [
            {
                "id": date[0],
                "title": date[1],
                "date": date[2],
                "time": date[3],
                "source_url": date[4],
                "confidence": float(date[5]),
                "is_confirmed": bool(date[6]),
                "is_auto_generated": bool(date[7]),
                "last_checked_at": date[8],
            }
            for date in dates # Isso aqui é uma list comprehension!
        ]

    def get_submission_status(self, event_id: int) -> dict:
        """
        Determina o status do período de submissão para um evento.
        Retorna um dicionário com as chaves:
        - status: um entre 'none', 'not_started', 'open', 'closed', 'open_no_deadline'
        - message: string amigável para exibição
        - opening_date: data de abertura (ISO str) ou None
        - deadline_date: data de prazo (ISO str) ou None
        """
        items = self.find_by_event_id(event_id)

        if not items:
            return {
                "status": "none",
                "message": "— Nenhuma informação de submissão",
                "opening_date": None,
                "deadline_date": None,
            }

        # Palavras-chave simples para identificar datas relacionadas a submissão
        title_lower = lambda item: (item.get("title") or "").lower()
        submission_indicators = [
            "submiss",
            "submission",
            "submission deadline",
            "abstract submission",
            "paper submission",
            "prazo",
            "deadline",
            "abert",
            "opens",
            "opening",
        ]

        related = []

        for item in items:
            if any(k in title_lower(item) for k in submission_indicators):
                try:
                    parsed = datetime.fromisoformat(item["date"]).date()

                except Exception:
                    continue

                related.append({
                    "date": parsed,
                    "title": item.get("title"),
                })

        if not related:
            return {
                "status": "none",
                "message": "— Nenhuma informação de submissão",
                "opening_date": None,
                "deadline_date": None,
            }

        # Ordena as datas encontradas
        related.sort(key=lambda x: x["date"])
        opening = related[0]["date"]
        deadline = related[-1]["date"] if len(related) > 1 else None

        now = datetime.now().date()

        def fmt(d: datetime.date) -> str:
            """
            Essa função formata a data para uma string amigável, no formato DD/MM/YYYY.
            """
            return d.strftime("%d/%m/%Y")

        # Se houver apenas uma data, tentamos inferir se é abertura ou prazo
        if deadline is None:
            title = (related[0]["title"] or "").lower()
            if any(k in title for k in ("abert", "opens", "opening")):
                if now < opening:
                    return {
                        "status": "not_started",
                        "message": f"⌛ Período de submissão começa em {fmt(opening)}",
                        "opening_date": opening.isoformat(),
                        "deadline_date": None,
                    }
                else:
                    return {
                        "status": "open_no_deadline",
                        "message": "✅ Período de submissão aberto",
                        "opening_date": opening.isoformat(),
                        "deadline_date": None,
                    }
            else:
                # Assume-se que é um prazo
                if now <= opening:
                    return {
                        "status": "open",
                        "message": f"✅ Período de submissão aberto até {fmt(opening)}",
                        "opening_date": None,
                        "deadline_date": opening.isoformat(),
                    }
                else:
                    return {
                        "status": "closed",
                        "message": f"❌ Período de submissão finalizada em {fmt(opening)}",
                        "opening_date": None,
                        "deadline_date": opening.isoformat(),
                    }

        # Se temos intervalo (abertura .. prazo)
        if opening and deadline:
            if now < opening:
                return {
                    "status": "not_started",
                    "message": f"⌛ Período de submissão começa em {fmt(opening)}",
                    "opening_date": opening.isoformat(),
                    "deadline_date": deadline.isoformat(),
                }
            elif opening <= now <= deadline:
                return {
                    "status": "open",
                    "message": f"✅ Período de submissão aberto até {fmt(deadline)}",
                    "opening_date": opening.isoformat(),
                    "deadline_date": deadline.isoformat(),
                }
            else:
                return {
                    "status": "closed",
                    "message": f"❌ Período de submissão finalizada em {fmt(deadline)}",
                    "opening_date": opening.isoformat(),
                    "deadline_date": deadline.isoformat(),
                }

