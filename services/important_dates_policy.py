from __future__ import annotations

import unicodedata
from datetime import datetime


class ImportantDatesPolicy:
    """
    Camada de qualidade para datas importantes.

    Objetivos:
    - Evitar datas genéricas, repetidas ou confusas.
    - Padronizar títulos como "Paper registration" e "Paper submission".
    - Separar eventos simples de eventos com trilhas/tracks.
    - Permitir fallback confiável para eventos conhecidos.
    """

    MAX_DISPLAY_DATES = 12

    BLOCKED_URL_PARTS = (
        "doity.com.br/cesar-beat",
        "ihc.sbc.org.br/2025",
    )

    @classmethod
    def prepare_dates_for_storage(
        cls,
        raw_dates: list[dict],
        source_url: str,
    ) -> list[dict]:
        """
        Recebe datas extraídas automaticamente e retorna somente datas confiáveis.
        """

        curated_dates = cls.get_curated_dates_by_url(source_url)

        if curated_dates:
            return curated_dates

        if cls.should_block_url(source_url):
            return []

        cleaned_dates = cls._clean_raw_dates(raw_dates, source_url)

        has_submission = any(
            cls.classify_title(item.get("title", "")) in {
                "submission_abstract",
                "submission_article",
            }
            for item in cleaned_dates
        )

        if not has_submission:
            return []

        return cleaned_dates[: cls.MAX_DISPLAY_DATES]

    @classmethod
    def should_block_url(cls, source_url: str | None) -> bool:
        url = (source_url or "").lower()

        if not url:
            return True

        return any(blocked in url for blocked in cls.BLOCKED_URL_PARTS)

    @classmethod
    def get_curated_dates_by_url(cls, source_url: str | None) -> list[dict]:
        """
        Datas confiáveis para páginas conhecidas.

        Quando a URL é conhecida, preferimos datas curadas para evitar que
        o extrator gere datas duplicadas, genéricas ou incorretas.
        """

        url = (source_url or "").lower()

        if "bracis.sbc.org.br/2026/eniac" in url:
            return [
                cls._manual_date(
                    "Submissão de artigos",
                    "2026-06-08",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores",
                    "2026-07-20",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Envio da versão final",
                    "2026-08-24",
                    source_url,
                    0.95,
                ),
            ]

        if "bracis.sbc.org.br/2026/bracis" in url:
            return [
                cls._manual_date(
                    "Submissão de resumos",
                    "2026-04-27",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos",
                    "2026-05-04",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores",
                    "2026-06-08",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Envio da versão final",
                    "2026-06-29",
                    source_url,
                    0.95,
                ),
            ]

        if "aaai.org/conference/aaai/aaai-26" in url:
            return [
                cls._manual_date(
                    "Abertura do sistema OpenReview para cadastro de autores",
                    "2025-06-16",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Abertura do sistema OpenReview para envio de artigos",
                    "2025-06-25",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de resumos",
                    "2025-07-25",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos",
                    "2025-08-01",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Material suplementar e código",
                    "2025-08-04",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Notificação da fase 1",
                    "2025-09-15",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Início da janela de feedback dos autores",
                    "2025-10-07",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Fim da janela de feedback dos autores",
                    "2025-10-13",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Notificação final de aceite ou rejeição",
                    "2025-11-08",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Envio dos arquivos finais camera-ready",
                    "2025-11-16",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Início do evento",
                    "2026-01-20",
                    source_url,
                    0.90,
                ),
                cls._manual_date(
                    "Fim do evento",
                    "2026-01-27",
                    source_url,
                    0.90,
                ),
            ]

        if "sbbd.org.br/2026/trilha-principal" in url:
            return [
                # Artigos completos
                cls._manual_date(
                    "Submissão de resumos — Artigos completos",
                    "2026-03-20",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos — Artigos completos",
                    "2026-03-29",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores — Artigos completos",
                    "2026-05-11",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de rebuttal — Artigos completos",
                    "2026-05-18",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Notificação final — Artigos completos",
                    "2026-06-03",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Envio da versão final — Artigos completos",
                    "2026-06-14",
                    source_url,
                    0.95,
                ),

                # Artigos curtos
                cls._manual_date(
                    "Submissão de resumos — Artigos curtos",
                    "2026-05-15",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos — Artigos curtos",
                    "2026-05-15",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores — Artigos curtos",
                    "2026-06-04",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Envio da versão final — Artigos curtos",
                    "2026-06-18",
                    source_url,
                    0.95,
                ),
            ]

        if "vldb.org/2026/important-dates" in url:
            return [
                cls._manual_date(
                    "Abertura das submissões",
                    "2025-03-23",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos",
                    "2026-03-01",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores",
                    "2026-04-15",
                    source_url,
                    0.90,
                ),
            ]

        if "icde2026.github.io/important-dates" in url:
            return [
                cls._manual_date(
                    "Submissão de artigos — Research Track 1º round",
                    "2025-06-18",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos — Research Track 2º round",
                    "2025-10-27",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos — Industry and Application Track",
                    "2025-10-27",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos — Demonstrations",
                    "2025-11-01",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — Workshop Proposals",
                    "2025-09-15",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — Tutorials",
                    "2025-11-11",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — TKDE Poster",
                    "2025-12-09",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — Ph.D. Symposium",
                    "2026-02-01",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — Lightning Talks",
                    "2025-11-14",
                    source_url,
                    0.95,
                ),
                cls._manual_date(
                    "Submissão de artigos — Data Engineering Future Technologies",
                    "2025-11-09",
                    source_url,
                    0.95,
                ),
            ]

        if "icml.cc/conferences/2026/callforpapers" in url:
            return [
                cls._manual_date(
                    "Abertura das submissões",
                    "2026-01-08",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de resumos",
                    "2026-01-23",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Submissão de artigos",
                    "2026-01-28",
                    source_url,
                    0.98,
                ),
                cls._manual_date(
                    "Notificação aos autores",
                    "2026-04-30",
                    source_url,
                    0.95,
                ),
            ]

        return []

    @classmethod
    def has_track_specific_dates(
        cls,
        important_dates: list[dict],
        source_url: str | None = None,
    ) -> bool:
        """
        Verifica se o evento possui trilhas, tracks ou modalidades específicas.

        Importante:
        BRACIS não é tratado automaticamente como evento com trilha.
        Só recebe aviso se os próprios títulos indicarem trilhas/modalidades.
        """

        url = (source_url or "").lower()

        if "sbbd.org.br/2026/trilha-principal" in url:
            return False

        track_url_parts = (
            "icde2026.github.io/important-dates",
        )

        if any(part in url for part in track_url_parts):
            return True

        track_terms = (
            "research track",
            "main track",
            "industry and application track",
            "industry track",
            "application track",
            "workshop proposals",
            "demonstrations",
            "tutorials",
            "ph.d. symposium",
            "phd symposium",
            "lightning talks",
            "short papers",
            "long papers",
            "artigos curtos",
            "artigos completos",
            "trilha ",
            "trilhas ",
            " track",
            " tracks",
            "modalidade ",
            "modalidades ",
        )

        for item in important_dates:
            title = cls._normalize_text(item.get("title", ""))

            if any(term in title for term in track_terms):
                return True

        return False

    @classmethod
    def get_track_specific_dates_notice(cls) -> str:
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ ATENÇÃO — DATAS POR TRILHA\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• Este evento possui trilhas, tracks ou modalidades específicas.\n"
            "• As datas podem mudar conforme a trilha escolhida.\n"
            "• Confira no site oficial as datas de cada trilha específica!"
        )

    @classmethod
    def classify_title(cls, title: str) -> str:
        normalized = cls._normalize_text(title)

        if not normalized:
            return "ignore"

        if any(term in normalized for term in (
            "submissao de resumos",
            "submissao de resumo",
            "submissao do resumo",
            "registro de resumo",
            "registro do resumo",
            "paper registration abstract",
            "paper registration",
            "abstract registration",
            "abstracts due",
            "abstract due",
            "abstract submission",
            "abstract submission deadline",
            "abstract deadline",
        )):
            return "submission_abstract"

        if any(term in normalized for term in (
            "submissao de artigos",
            "submissao de artigo",
            "submissao do artigo",
            "envio de artigos",
            "envio do artigo",
            "submission due",
            "submission deadline",
            "paper submission",
            "paper submission deadline",
            "full papers due",
            "full paper due",
            "full paper submission",
            "full paper submission deadline",
            "prazo de submissao",
        )):
            return "submission_article"

        if any(term in normalized for term in (
            "abertura das submissoes",
            "submission site opens",
            "submissions open",
            "openreview",
        )):
            return "submission_opening"

        if "rebuttal" in normalized:
            return "rebuttal"

        if any(term in normalized for term in (
            "notificacao final",
            "final notification",
            "notificacao final de aceite",
        )):
            return "notification_final"

        if any(term in normalized for term in (
            "notificacao",
            "notification",
        )):
            return "notification"

        if any(term in normalized for term in (
            "versao final",
            "camera ready",
            "camera-ready",
            "camera",
            "camera-ready copy due",
            "camera ready copy",
            "envio dos arquivos finais",
            "camera ready files",
        )):
            return "camera_ready"

        if any(term in normalized for term in (
            "inicio do evento",
            "inicio da conferencia",
            "event start",
            "conference start",
        )):
            return "event_start"

        if any(term in normalized for term in (
            "fim do evento",
            "fim da conferencia",
            "event end",
            "conference end",
        )):
            return "event_end"

        if any(term in normalized for term in (
            "material suplementar",
            "supplementary",
            "codigo",
            "code",
        )):
            return "supplementary"

        if any(term in normalized for term in (
            "prazo",
            "prazo final",
            "deadline",
            "due",
            "datas importantes",
            "data importante",
            "data do evento",
            "inicio",
            "fim",
            "evento",
            "conference",
            "workshop",
            "tutorial",
        )):
            return "ignore"

        return "ignore"

    @classmethod
    def normalize_title(cls, title: str) -> str:
        category = cls.classify_title(title)

        normalized_titles = {
            "submission_opening": "Abertura das submissões",
            "submission_abstract": "Submissão de resumos",
            "submission_article": "Submissão de artigos",
            "supplementary": "Material suplementar e código",
            "rebuttal": "Submissão de rebuttal",
            "notification": "Notificação aos autores",
            "notification_final": "Notificação final",
            "camera_ready": "Envio da versão final",
            "event_start": "Início do evento",
            "event_end": "Fim do evento",
        }

        base_title = normalized_titles.get(category, title)

        # Preserva o complemento depois de "—".
        # Exemplo:
        # "Submissão de artigos — Artigos completos"
        # continua indicando a modalidade.
        if "—" in title and category in {
            "submission_abstract",
            "submission_article",
            "rebuttal",
            "notification",
            "notification_final",
            "camera_ready",
        }:
            suffix = title.split("—", 1)[1].strip()
            return f"{base_title} — {suffix}"

        return base_title

    @classmethod
    def category_label(cls, category: str) -> str:
        labels = {
            "submission_opening": "Submissões",
            "submission_abstract": "Submissões",
            "submission_article": "Submissões",
            "supplementary": "Submissões",
            "rebuttal": "Pós-submissão",
            "notification": "Pós-submissão",
            "notification_final": "Pós-submissão",
            "camera_ready": "Pós-submissão",
            "event_start": "Evento",
            "event_end": "Evento",
        }

        return labels.get(category, "Outras datas")

    @classmethod
    def sort_order(cls, category: str) -> int:
        order = {
            "submission_opening": 10,
            "submission_abstract": 20,
            "submission_article": 30,
            "supplementary": 40,
            "rebuttal": 50,
            "notification": 60,
            "notification_final": 70,
            "camera_ready": 80,
            "event_start": 90,
            "event_end": 100,
        }

        return order.get(category, 999)

    @classmethod
    def _clean_raw_dates(
        cls,
        raw_dates: list[dict],
        source_url: str,
    ) -> list[dict]:
        cleaned_dates: list[dict] = []
        seen: set[tuple[str, str, str]] = set()

        for item in raw_dates:
            if item.get("ignore"):
                continue

            title = item.get("title", "")
            date = item.get("date")

            if not cls._is_valid_iso_date(date):
                continue

            category = cls.classify_title(title)

            if category == "ignore":
                continue

            normalized_title = cls.normalize_title(title)
            key = (category, normalized_title, date)

            if key in seen:
                continue

            seen.add(key)

            cleaned_dates.append({
                "title": normalized_title,
                "date": date,
                "time": item.get("time"),
                "source_url": item.get("source_url") or source_url,
                "confidence": max(float(item.get("confidence", 0.0)), 0.85),
                "ignore": False,
            })

        cleaned_dates.sort(
            key=lambda item: (
                cls.sort_order(cls.classify_title(item["title"])),
                item["date"],
                item["title"],
            )
        )

        return cleaned_dates

    @staticmethod
    def _manual_date(
        title: str,
        date: str,
        source_url: str | None,
        confidence: float = 0.95,
    ) -> dict:
        return {
            "title": title,
            "date": date,
            "time": None,
            "source_url": source_url,
            "confidence": confidence,
            "ignore": False,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text or ""
        text = unicodedata.normalize("NFD", text)
        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Mn"
        )
        return text.lower().strip()

    @staticmethod
    def _is_valid_iso_date(value: str | None) -> bool:
        if not value:
            return False

        try:
            datetime.fromisoformat(value).date()
            return True
        except (TypeError, ValueError):
            return False
