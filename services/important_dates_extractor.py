import html
import re
from datetime import datetime


class ImportantDatesExtractor:
    """
    Extrai datas importantes em português e inglês.
    """

    NUMERIC_DATE_PATTERNS = [
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b",
    ]

    ENGLISH_MONTHS = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
    }

    PORTUGUESE_MONTHS = {
        "janeiro": 1,
        "fevereiro": 2,
        "março": 3,
        "marco": 3,
        "abril": 4,
        "maio": 5,
        "junho": 6,
        "julho": 7,
        "agosto": 8,
        "setembro": 9,
        "outubro": 10,
        "novembro": 11,
        "dezembro": 12,
    }

    KEYWORDS = {
        # Português
        "submissão de resumos": "Submissão de resumos",
        "submissão de artigos": "Submissão de artigos",
        "submissão": "Submissão",
        "notificação final": "Notificação final",
        "notificação": "Notificação aos autores",
        "envio da versão final": "Versão final do artigo",
        "versão final": "Versão final do artigo",
        "datas importantes": "Datas importantes",
        "inscrição": "Período de inscrição",
        "inscrições": "Período de inscrição",
        "inicio": "Início",
        "início": "Início",
        "fim": "Fim",
        "evento": "Data do evento",
        "realização": "Data do evento",
        "pagamento": "Prazo de pagamento",
        "cancelamento": "Prazo de cancelamento",

        # Inglês
        "paper registration (abstract)": "Registro do resumo",
        "paper submission deadline (long and short papers)": "Prazo de submissão",
        "deadline for submission": "Prazo de submissão",
        "submission deadline": "Prazo de submissão",
        "abstract submission deadline": "Submissão de resumo",
        "full paper submission deadline": "Submissão do artigo completo",
        "submission site opens": "Abertura das submissões",
        "paper registration": "Registro do artigo",
        "paper submission": "Submissão do artigo",
        "authors notification": "Notificação aos autores",
        "notification to authors": "Notificação aos autores",
        "author notification": "Notificação aos autores",
        "paper notification": "Notificação do artigo",
        "summary reject notification": "Notificação de rejeição inicial",
        "phase i notification": "Notificação fase I",
        "author's response": "Resposta dos autores",
        "authors response": "Resposta dos autores",
        "author response period": "Período de resposta dos autores",
        "camera-ready versions due": "Versão final do artigo",
        "camera-ready version": "Versão final do artigo",
        "camera-ready version due": "Versão final do artigo",
        "camera-ready manuscript due": "Versão final do artigo",
        "camera-ready copy due": "Versão final do artigo",
        "camera ready copy": "Versão final do artigo",
        "camera-ready deadline": "Versão final do artigo",
        "camera-ready": "Versão final do artigo",
        "workshops and tutorials": "Workshops e tutoriais",
        "opening reception": "Recepção de abertura",
        "ijcai ecai 2026 main conference": "Conferência principal",
        "main conference": "Conferência principal",
        "industry day": "Industry Day",
        "important dates": "Datas importantes",
        "conference": "Data do evento",
        "workshops": "Workshops",
        "tutorials": "Tutoriais",
        "deadline": "Prazo",
        "due": "Prazo final",
    }

    LABEL_TRANSLATIONS = {
        "paper registration (abstract)": "Registro do resumo",
        "paper submission deadline (long and short papers)": "Prazo de submissão",
        "deadline for submission": "Prazo de submissão",
        "submission deadline": "Prazo de submissão",
        "paper registration": "Registro do artigo",
        "paper submission": "Submissão do artigo",
        "authors notification": "Notificação aos autores",
        "notification to authors": "Notificação aos autores",
        "author notification": "Notificação aos autores",
        "paper notification": "Notificação do artigo",
        "phase i notification": "Notificação fase I",
        "author's response": "Resposta dos autores",
        "authors response": "Resposta dos autores",
        "camera-ready versions due": "Versão final do artigo",
        "camera ready versions due": "Versão final do artigo",
        "camera-ready version": "Versão final do artigo",
        "camera ready version": "Versão final do artigo",
        "camera-ready version due": "Versão final do artigo",
        "camera ready version due": "Versão final do artigo",
        "camera-ready copy due": "Versão final do artigo",
        "camera ready copy due": "Versão final do artigo",
        "camera-ready manuscript due": "Versão final do artigo",
        "camera ready copy": "Versão final do artigo",
        "abstract submission deadline": "Submissão de resumo",
        "full paper submission deadline": "Submissão do artigo completo",
        "submission site opens": "Abertura das submissões",
        "summary reject notification": "Notificação de rejeição inicial",
        "workshops and tutorials": "Workshops e tutoriais",
        "opening reception": "Recepção de abertura",
        "ijcai ecai 2026 main conference": "Conferência principal",
        "main conference": "Conferência principal",
        "industry day": "Industry Day",

        # Português
        "submissão de resumos": "Submissão de resumos",
        "submissão de artigos": "Submissão de artigos",
        "notificação final": "Notificação final",
        "notificação": "Notificação aos autores",
        "envio da versão final": "Versão final do artigo",
    }

    SPECIAL_CARD_LABELS = {
        "paper registration (abstract)": "Submissão de resumos",
        "paper registration abstract": "Submissão de resumos",
        "paper registration": "Submissão de resumos",
        "abstract registration": "Submissão de resumos",
        "abstract deadline": "Submissão de resumos",
        "abstract due": "Submissão de resumos",

        "submission deadline": "Prazo de submissão",
        "submission due": "Prazo de submissão",
        "paper submission deadline": "Prazo de submissão",
        "full paper submission deadline": "Prazo de submissão",
        "abstract submission deadline": "Submissão de resumos",
        "paper submission deadline (long and short papers)": "Prazo de submissão",
        "paper submission": "Submissão de artigos",
        "deadline for submission": "Prazo de submissão",

        "authors notification": "Notificação aos autores",
        "notification for authors": "Notificação aos autores",
        "notification to authors": "Notificação aos autores",

        "camera-ready versions due": "Versão final do artigo",
        "camera-ready version": "Versão final do artigo",
        "camera-ready copy due": "Versão final do artigo",
        "camera ready copy": "Versão final do artigo",
    }

    def extract(self, text: str, source_url: str, fallback_year: int | None = None) -> list[dict]:
        if not text:
            return []

        clean_text = self._clean_text(text)
        special_card_dates = self._extract_special_important_date_cards(
            clean_text, source_url)
        if special_card_dates:
            return self._remove_duplicates_and_obsolete_dates(special_card_dates)

        if fallback_year is None:
            fallback_year = self._infer_global_year(clean_text)

        important_dates = []
        important_dates.extend(
            self._extract_numeric_dates(clean_text, source_url))
        important_dates.extend(
            self._extract_english_month_dates(clean_text, source_url))
        important_dates.extend(self._extract_english_month_day_without_year(
            clean_text, source_url, fallback_year))
        important_dates.extend(self._extract_english_same_month_range_without_year(
            clean_text, source_url, fallback_year))
        important_dates.extend(
            self._extract_english_cross_month_ranges(clean_text, source_url))
        important_dates.extend(
            self._extract_english_day_month_ranges(clean_text, source_url))
        important_dates.extend(
            self._extract_english_same_month_ranges(clean_text, source_url))
        important_dates.extend(self._extract_portuguese_month_dates(
            clean_text, source_url, fallback_year))
        important_dates.extend(self._extract_portuguese_month_ranges(
            clean_text, source_url, fallback_year))
        important_dates.extend(self._extract_portuguese_multiple_days_same_month(
            clean_text, source_url, fallback_year))

        return self._remove_duplicates_and_obsolete_dates(important_dates)

    def _clean_text(self, text: str) -> str:
        """
        Limpa o HTML, remove conteúdos riscados e obsoletos, e normaliza o texto para facilitar a extração de datas.
        """
        text = html.unescape(text)
        text = self._remove_crossed_out_content(text)
        text = re.sub(
            r"<script.*?</script>",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        text = re.sub(
            r"<style.*?</style>",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        text = re.sub(
            r"</(p|div|li|h1|h2|h3|h4|h5|h6|tr|td|section|article|span)>",
            "\n",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"<br\s*/?>",
            "\n",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(r"<[^>]+>", " ", text)

        text = re.sub(
            r"(\d+)(st|nd|rd|th)",
            r"\1",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)

        return text.strip()

    def _remove_crossed_out_content(self, text: str) -> str:
        """
        Remove conteúdos riscados e obsoletos antes de limpar o HTML.
        """

        text = re.sub(
            r"~~.*?~~",
            " ",
            text,
            flags=re.DOTALL
        )

        text = re.sub(
            r"<\s*(s|del|strike)\b[^>]*>.*?<\s*/\s*\1\s*>",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        text = re.sub(
            r"<[^>]*style\s*=\s*['\"][^'\"]*(line-through|text-decoration\s*:\s*line-through)[^'\"]*['\"][^>]*>.*?</[^>]+>",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        text = re.sub(
            r"<[^>]*class\s*=\s*['\"][^'\"]*(old|past|previous|strike|strikethrough|line-through|deprecated)[^'\"]*['\"][^>]*>.*?</[^>]+>",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        return text

    def _extract_special_important_date_cards(
        self,
        text: str,
        source_url: str
    ) -> list[dict]:
        """
        Extrai datas importantes de páginas com cards, como BRACIS, STIL e ENIAC.
        """

        source_url_lower = source_url.lower()

        supported_domains = [
            "bracis.sbc.org.br",
        ]

        if not any(domain in source_url_lower for domain in supported_domains):
            return []

        occurrences = self._find_special_card_label_occurrences(text)

        if not occurrences:
            return []

        important_dates = []

        for index, occurrence in enumerate(occurrences):
            block_start = occurrence["start"]

            if index + 1 < len(occurrences):
                block_end = occurrences[index + 1]["start"]
            else:
                block_end = min(len(text), occurrence["end"] + 500)

            block = text[block_start:block_end]

            item = self._extract_confirmed_date_from_card_block(
                block=block,
                title=occurrence["title"],
                source_url=source_url
            )

            if item:
                important_dates.append(item)

        return important_dates

    def _find_special_card_label_occurrences(self, text: str) -> list[dict]:
        """
        Localiza rótulos de cards de datas importantes no texto.
        """

        occurrences = []

        for label, title in self.SPECIAL_CARD_LABELS.items():
            flexible_label = re.escape(label)
            flexible_label = flexible_label.replace(r"\ ", r"\s+")

            pattern = flexible_label

            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                occurrences.append({
                    "start": match.start(),
                    "end": match.end(),
                    "label": label,
                    "title": title,
                })

        occurrences.sort(
            key=lambda item: (
                item["start"],
                -(item["end"] - item["start"])
            )
        )

        filtered_occurrences = []
        last_end = -1

        for occurrence in occurrences:
            if occurrence["start"] < last_end:
                continue

            filtered_occurrences.append(occurrence)
            last_end = occurrence["end"]

        return filtered_occurrences

    def _extract_confirmed_date_from_card_block(self, block: str, title: str, source_url: str) -> dict | None:
        """
        Extrai a data confirmada de um card.

        Escolhe a maior data antes de grace period.
        """

        block_without_grace = re.split(
            r"grace\s+period\s*:?",
            block,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0]

        date_candidates = self._extract_english_dates_from_text(
            block_without_grace
        )

        if not date_candidates:
            date_candidates = self._extract_portuguese_dates_from_text(
                block_without_grace
            )

        if not date_candidates:
            return None

        confirmed_date = max(date_candidates)

        return {
            "title": title,
            "date": confirmed_date,
            "time": None,
            "source_url": source_url,
            "confidence": 0.95,
            "ignore": False,
        }

    def _extract_english_dates_from_text(self, text: str) -> list[str]:
        """
        Extrai datas em inglês com ano explícito de um bloco menor.
        """

        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}}),?\s+(\d{{4}})\b"

        dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            month = self.ENGLISH_MONTHS[match.group(1).lower()]
            day = int(match.group(2))
            year = int(match.group(3))

            iso_date = self._build_iso_date(year, month, day)

            if iso_date:
                dates.append(iso_date)

        return dates

    def _extract_portuguese_dates_from_text(self, text: str) -> list[str]:
        """
        Extrai datas em português com ano explícito de um bloco menor.
        """

        month_names = "|".join(self.PORTUGUESE_MONTHS.keys())
        pattern = rf"\b(\d{{1,2}})\s+de\s+({month_names})(?:\s+de\s+|\s*,?\s*)(\d{{4}})\b"

        dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            day = int(match.group(1))
            month = self.PORTUGUESE_MONTHS[match.group(2).lower()]
            year = int(match.group(3))

            iso_date = self._build_iso_date(year, month, day)

            if iso_date:
                dates.append(iso_date)

        return dates

    def _infer_global_year(self, text: str) -> int | None:
        """
        Tenta inferir o ano global da página.
        """

        patterns = [
            r"all dates refer to the year\s+(\d{4})",
            r"dates refer to the year\s+(\d{4})",
            r"todas as datas.*?(\d{4})",
            r"ano\s+(\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))

        years = re.findall(r"\b(20\d{2})\b", text)

        if years:
            return int(years[0])

        return None

    def _extract_numeric_dates(self, text: str, source_url: str) -> list[dict]:
        """
        Essa função é chamada apenas para extrair datas numéricas, e não para extrair datas de cards especiais, para evitar falsos positivos.
        """
        important_dates = []

        for pattern in self.NUMERIC_DATE_PATTERNS:
            for match in re.finditer(pattern, text):
                iso_date = self._build_iso_date(
                    int(match.group(3)),
                    int(match.group(2)),
                    int(match.group(1))
                )

                if not iso_date:
                    continue

                item = self._build_date_item(
                    text,
                    match.start(),
                    match.end(),
                    iso_date,
                    source_url
                )

                if not item["ignore"]:
                    important_dates.append(item)

        return important_dates

    def _extract_english_month_dates(self, text: str, source_url: str) -> list[dict]:
        """
        Essa função é chamada apenas para extrair datas com mês escrito, e não para extrair datas de cards especiais, para evitar falsos positivos.
        """
        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}}),?\s+(\d{{4}})\b"

        important_dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            month = self.ENGLISH_MONTHS[match.group(1).lower()]
            day = int(match.group(2))
            year = int(match.group(3))

            iso_date = self._build_iso_date(year, month, day)

            if not iso_date:
                continue

            item = self._build_date_item(
                text,
                match.start(),
                match.end(),
                iso_date,
                source_url
            )

            if not item["ignore"]:
                important_dates.append(item)

        return important_dates

    def _extract_english_month_day_without_year(self, text: str, source_url: str, fallback_year: int | None) -> list[dict]:
        """
        Extrai datas em inglês sem ano explícito.
        """

        if fallback_year is None:
            return []

        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}})\.?\b(?!\s*,?\s*\d{{4}})"

        important_dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            month_name = match.group(1).lower()
            day = int(match.group(2))
            month = self.ENGLISH_MONTHS[month_name]

            iso_date = self._build_iso_date(
                fallback_year,
                month,
                day
            )

            if not iso_date:
                continue

            item = self._build_date_item(
                text,
                match.start(),
                match.end(),
                iso_date,
                source_url
            )

            if not item["ignore"]:
                important_dates.append(item)

        return important_dates

    def _extract_english_same_month_range_without_year(self, text: str, source_url: str, fallback_year: int | None) -> list[dict]:
        """
        Extrai intervalos em inglês sem ano explícito.
        """

        if fallback_year is None:
            return []

        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}})\s*[-–]\s*(\d{{1,2}})\.?\b(?!\s*,?\s*\d{{4}})"

        important_dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            month = self.ENGLISH_MONTHS[match.group(1).lower()]
            start_day = int(match.group(2))
            end_day = int(match.group(3))

            start_date = self._build_iso_date(
                fallback_year,
                month,
                start_day
            )

            end_date = self._build_iso_date(
                fallback_year,
                month,
                end_day
            )

            if start_date and end_date:
                important_dates.extend(
                    self._build_range_items(
                        text,
                        match.start(),
                        match.end(),
                        start_date,
                        end_date,
                        source_url
                    )
                )

        return [
            item for item in important_dates
            if not item["ignore"]
        ]

    def _extract_english_cross_month_ranges(self, text: str, source_url: str) -> list[dict]:
        """
        Essa função extrai intervalos em inglês que cruzam meses, como "December 30 - January 2, 2024".
        """
        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}})\s*[-–]\s*({month_names})\s+(\d{{1,2}}),?\s+(\d{{4}})\b"

        important_dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start_month = self.ENGLISH_MONTHS[match.group(1).lower()]
            start_day = int(match.group(2))
            end_month = self.ENGLISH_MONTHS[match.group(3).lower()]
            end_day = int(match.group(4))
            year = int(match.group(5))

            start_date = self._build_iso_date(year, start_month, start_day)
            end_date = self._build_iso_date(year, end_month, end_day)

            if start_date and end_date:
                important_dates.extend(
                    self._build_range_items(
                        text,
                        match.start(),
                        match.end(),
                        start_date,
                        end_date,
                        source_url
                    )
                )

        return [
            item for item in important_dates
            if not item["ignore"]
        ]

    def _extract_english_day_month_ranges(self, text: str, source_url: str) -> list[dict]:
        """
        Extrai intervalos em inglês no formato:
        """

        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = (
            rf"\b(\d{{1,2}})\s+({month_names})\s*[-–]\s*"
            rf"(\d{{1,2}})\s+({month_names}),?\s+(\d{{4}})\b"
        )

        important_dates = []
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start_day = int(match.group(1))
            start_month = self.ENGLISH_MONTHS[match.group(2).lower()]
            end_day = int(match.group(3))
            end_month = self.ENGLISH_MONTHS[match.group(4).lower()]
            year = int(match.group(5))

            start_date = self._build_iso_date(year, start_month, start_day)
            end_date = self._build_iso_date(year, end_month, end_day)
            if start_date and end_date:
                important_dates.extend(
                    self._build_range_items(text, match.start(), match.end(), start_date, end_date, source_url))

        return [item for item in important_dates if not item["ignore"]]

    def _extract_english_same_month_ranges(self, text: str, source_url: str) -> list[dict]:
        """
        Essa função extrai intervalos em inglês no formato "January 10-12, 2024", onde o mês é escrito e o ano é explícito, mas o dia é um intervalo.
        """
        month_names = "|".join(self.ENGLISH_MONTHS.keys())
        pattern = rf"\b({month_names})\s+(\d{{1,2}})\s*[-–]\s*(\d{{1,2}}),?\s+(\d{{4}})\b"
        important_dates = []

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            month = self.ENGLISH_MONTHS[match.group(1).lower()]
            start_day = int(match.group(2))
            end_day = int(match.group(3))
            year = int(match.group(4))

            start_date = self._build_iso_date(year, month, start_day)
            end_date = self._build_iso_date(year, month, end_day)

            if start_date and end_date:
                important_dates.extend(
                    self._build_range_items(text, match.start(), match.end(), start_date, end_date, source_url))

        return [item for item in important_dates if not item["ignore"]]

    def _extract_portuguese_month_dates(self, text: str, source_url: str, fallback_year: int | None) -> list[dict]:
        """
        Essa função é chamada apenas para extrair datas com mês escrito, e não para extrair datas de cards especiais, para evitar falsos positivos.
        """
        month_names = "|".join(self.PORTUGUESE_MONTHS.keys())
        pattern = rf"\b(\d{{1,2}})\s+de\s+({month_names})(?:\s+de\s+|\s*,?\s*)(\d{{4}})?\b"

        important_dates = []
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            day = int(match.group(1))
            month = self.PORTUGUESE_MONTHS[match.group(2).lower()]
            year_text = match.group(3)

            if year_text:
                year = int(year_text)

            elif fallback_year:
                year = fallback_year

            else:
                continue

            iso_date = self._build_iso_date(year, month, day)

            if not iso_date:
                continue

            item = self._build_date_item(
                text, match.start(), match.end(), iso_date, source_url)

            if not item["ignore"]:
                important_dates.append(item)

        return important_dates

    def _extract_portuguese_month_ranges(self, text: str, source_url: str, fallback_year: int | None) -> list[dict]:
        """
        Essa função extrai intervalos em português no formato "10 a 12 de Janeiro de 2024", em que o mês é escrito e o ano é explícito, mas o dia é um intervalo. 
        Ela também lida com variações como "10 a 12 de Janeiro" (sem ano) e "10 a 12 de Janeiro, 2024".
        """
        month_names = "|".join(self.PORTUGUESE_MONTHS.keys())
        pattern = rf"\b(\d{{1,2}})\s+a\s+(\d{{1,2}})\s+de\s+({month_names})(?:\s+de\s+|\s*,?\s*)(\d{{4}})?\b"

        important_dates = []
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start_day = int(match.group(1))
            end_day = int(match.group(2))
            month = self.PORTUGUESE_MONTHS[match.group(3).lower()]
            year_text = match.group(4)

            if year_text:
                year = int(year_text)

            elif fallback_year:
                year = fallback_year

            else:
                continue

            start_date = self._build_iso_date(year, month, start_day)
            end_date = self._build_iso_date(year, month, end_day)
            if start_date and end_date:
                important_dates.extend(self._build_range_items(
                    text, match.start(), match.end(), start_date, end_date, source_url))

        return [item for item in important_dates if not item["ignore"]]

    def _extract_portuguese_multiple_days_same_month(self, text: str, source_url: str, fallback_year: int | None) -> list[dict]:
        """
        Essa função extrai intervalos em português no formato "10, 11 e 12 de Janeiro de 2024", em que o mês é escrito e o ano é explícito, mas o dia é uma lista de dias. 
        Ela também lida com variações como "10, 11 e 12 de Janeiro" (sem ano) e "10, 11 e 12 de Janeiro, 2024".
        """
        month_names = "|".join(self.PORTUGUESE_MONTHS.keys())
        pattern = rf"\b(\d{{1,2}}),\s*(\d{{1,2}})\s+e\s+(\d{{1,2}})\s+de\s+({month_names})(?:\s+de\s+|\s*,?\s*)(\d{{4}})?\b"

        important_dates = []
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            days = [int(match.group(1)), int(
                match.group(2)), int(match.group(3))]

            month = self.PORTUGUESE_MONTHS[match.group(4).lower()]
            year_text = match.group(5)
            if year_text:
                year = int(year_text)

            elif fallback_year:
                year = fallback_year

            else:
                continue

            start_date = self._build_iso_date(year, month, min(days))
            end_date = self._build_iso_date(year, month, max(days))
            if start_date and end_date:
                important_dates.extend(self._build_range_items(
                    text, match.start(), match.end(), start_date, end_date, source_url))

        return [item for item in important_dates if not item["ignore"]]

    def _build_date_item(self, text: str, start: int, end: int, iso_date: str, source_url: str) -> dict:
        """
        Essa função constrói o item de data importante, inferindo o título, extraindo a hora (se houver), calculando a confiança e verificando se a data deve ser ignorada.
        """
        context = self._get_context(text, start, end)
        title = (self._infer_title_after_date(text, end) or self._infer_title_near_date(
            text, start, end) or self._infer_title(context))
        time = self._extract_time(context)
        confidence = self._calculate_confidence(context, title, time)
        ignore = self._should_ignore_date(text, start, end, title)

        return {
            "title": title,
            "date": iso_date,
            "time": time,
            "source_url": source_url,
            "confidence": confidence,
            "ignore": ignore,
        }

    def _build_range_items(self, text: str, start: int, end: int, start_date: str, end_date: str, source_url: str) -> list[dict]:
        """
        Essa função constrói os itens de data importante para intervalos, inferindo o título, calculando a confiança e verificando se as datas devem ser ignoradas.
        """
        context = self._get_context(text, start, end)

        base_title = (self._infer_title_after_date(text, end) or self._infer_title_near_date(
            text, start, end) or self._infer_title(context))
        confidence = self._calculate_confidence(context, base_title, None)
        ignore = self._should_ignore_date(text, start, end, base_title)

        if base_title in {"Data importante", "Datas importantes", "Data do evento"}:
            start_title = "Início do evento"
            end_title = "Fim do evento"

        else:
            start_title = f"Início - {base_title}"
            end_title = f"Fim - {base_title}"

        return [
            {
                "title": start_title,
                "date": start_date,
                "time": None,
                "source_url": source_url,
                "confidence": min(confidence + 0.05, 0.95),
                "ignore": ignore,
            },
            {
                "title": end_title,
                "date": end_date,
                "time": None,
                "source_url": source_url,
                "confidence": min(confidence + 0.05, 0.95),
                "ignore": ignore,
            }
        ]

    def _should_ignore_date(self, text: str, start: int, end: int, title: str) -> bool:
        """
        Determina se uma data deve ser ignorada com base em palavras-chave próximas e no título inferido.
        """
        near_before = text[max(0, start - 100):start].lower()
        near_after = text[end:min(len(text), end + 100)].lower()
        near_text = f"{near_before} {near_after}"

        ignored_terms = [
            "grace period",
            "grace period:",
            "período de tolerância",
            "periodo de tolerancia",
            "prazo de tolerância",
            "prazo de tolerancia",
        ]

        return any(term in near_text for term in ignored_terms)

    def _infer_title_after_date(self, text: str, match_end: int) -> str | None:
        """
        Infere o título quando o rótulo aparece depois da data.
        """

        after_context = text[match_end:min(len(text), match_end + 140)]
        after_context = after_context.split("\n")[0]
        after_context = re.sub(r"^[\s\.\-–:]+", "", after_context)
        after_context = re.sub(r"\s+", " ", after_context).strip().lower()
        if not after_context:
            return None

        for label, translation in self.LABEL_TRANSLATIONS.items():
            if label in after_context:
                return translation

        for label, translation in self.KEYWORDS.items():
            if label in after_context:
                return translation

        return None

    def _infer_title_near_date(self, text: str, match_start: int, match_end: int) -> str | None:
        """
        Essa função tenta inferir o título da data importante procurando por rótulos próximos antes da data, dando prioridade para os mais próximos. Se não encontrar, tenta inferir a partir da linha.
        """
        before_context = text[max(0, match_start - 240):match_start].lower()
        before_context = re.sub(r"\s+", " ", before_context)

        all_labels = {
            **self.KEYWORDS,
            **self.LABEL_TRANSLATIONS
        }

        best_title = None
        best_position = -1

        for label, title in all_labels.items():
            label_lower = label.lower()
            position = before_context.rfind(label_lower)

            if position > best_position:
                best_position = position
                best_title = title

        if best_title:
            return best_title

        return self._infer_title_from_line(text, match_start)

    def _infer_title_from_line(self, text: str, match_start: int) -> str | None:
        """
        Essa função tenta inferir o título a partir da linha em que a data foi encontrada, dando prioridade para o texto antes da data. Se não encontrar, tenta usar as linhas anteriores.
        """
        lines = text.splitlines()
        current_position = 0

        for index, line in enumerate(lines):
            line_start = current_position
            line_end = current_position + len(line)

            if line_start <= match_start <= line_end:
                candidates = []

                current_line_before_date = line[:max(
                    0, match_start - line_start)].strip()

                if current_line_before_date:
                    candidates.append(current_line_before_date)

                if index > 0:
                    candidates.append(lines[index - 1].strip())

                if index > 1:
                    candidates.append(lines[index - 2].strip())

                for candidate in candidates:
                    title = self._normalize_label(candidate)
                    if title:
                        return title

                return None

            current_position += len(line) + 1

        return None

    def _normalize_label(self, candidate: str) -> str | None:
        """
        Essa função normaliza um candidato a título, removendo excesso de espaços, convertendo para minúsculas e verificando se contém rótulos conhecidos ou se é um título plausível. Ela também descarta candidatos muito longos ou que contenham anos, para evitar falsos positivos.
        """
        candidate = re.sub(r"\s+", " ", candidate).strip()
        candidate_lower = candidate.lower()

        if not candidate_lower:
            return None

        for label, translation in self.LABEL_TRANSLATIONS.items():
            if label in candidate_lower:
                return translation

        if len(candidate) > 80:
            return None

        if re.search(r"\d{4}", candidate):
            return None

        return None

    def _infer_title(self, context: str) -> str:
        """
        Essa função tenta inferir o título da data importante a partir do contexto, procurando por palavras-chave que indiquem o tipo de data. Ela dá prioridade para as palavras-chave mais específicas e mais próximas da data.
        """
        normalized_context = context.lower()

        priority_phrases = sorted(
            self.KEYWORDS.keys(),
            key=len,
            reverse=True
        )

        for phrase in priority_phrases:
            if phrase in normalized_context:
                return self.KEYWORDS[phrase]

        return "Data importante"

    def _extract_time(self, context: str) -> str | None:
        """
        Essa função tenta extrair a hora do contexto, procurando por padrões como "14h30" ou "14:30". Ela retorna a hora no formato "HH:MM".
        """
        match = re.search(
            r"\b(\d{1,2})h(\d{2})?\b|\b(\d{1,2}):(\d{2})\b", context)

        if not match:
            return None

        if match.group(1):
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            return f"{hour:02d}:{minute:02d}"

        hour = int(match.group(3))
        minute = int(match.group(4))

        return f"{hour:02d}:{minute:02d}"

    def _calculate_confidence(self, context: str, title: str, time: str | None) -> float:
        """
        Essa função calcula a confiança da data importante com base no título inferido, na presença de hora e em palavras-chave no contexto. 
        Ela começa com uma confiança base de 0.50 e adiciona pontos para cada evidência encontrada, limitando a confiança máxima a 0.95 para evitar 
        falsos positivos com confiança total.
        """
        confidence = 0.50

        if title != "Data importante":
            confidence += 0.30

        if time:
            confidence += 0.10

        if any(word in context for word in [
            "oficial",
            "official",
            "programação",
            "schedule",
            "cronograma",
            "calendar",
            "agenda",
            "important dates",
            "datas importantes",
            "deadline",
            "due",
            "submission",
            "submissão"
        ]):
            confidence += 0.10

        return min(confidence, 0.95)

    def _build_iso_date(self, year: int, month: int, day: int) -> str | None:
        """
        Essa função tenta construir uma data ISO a partir de componentes numéricos, validando se a data é real. Se a data for inválida, ela retorna None.
        """
        try:
            parsed_date = datetime(year, month, day).date()
            return parsed_date.isoformat()

        except ValueError:
            return None

    def _get_context(self, text: str, start: int, end: int, window: int = 220) -> str:
        """
        Essa função extrai um contexto ao redor da data encontrada, com um tamanho definido pela janela. Ela é usada para inferir o título, extrair a hora e calcular a confiança da data importante. O contexto é convertido para minúsculas para facilitar a busca por palavras-chave.
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)

        return text[context_start:context_end].lower()

    def _remove_duplicates_and_obsolete_dates(self, dates: list[dict]) -> list[dict]:
        """
        Essa função remove datas duplicadas e obsoletas, dando prioridade para as datas com maior confiança e para as datas mais recentes quando os títulos são iguais. Ela também remove as datas marcadas para serem ignoradas. O resultado é uma lista de datas importantes únicas, ordenadas cronologicamente.
        """
        filtered_dates = [
            item for item in dates if not item.get("ignore", False)]

        exact_unique = {}

        for item in filtered_dates:
            clean_item = {
                key: value
                for key, value in item.items()
                if key != "ignore"
            }

            key = (
                clean_item["title"],
                clean_item["date"],
                clean_item.get("time")
            )

            if key not in exact_unique:
                exact_unique[key] = clean_item
                continue

            if clean_item["confidence"] > exact_unique[key]["confidence"]:
                exact_unique[key] = clean_item

        latest_by_title = {}

        for item in exact_unique.values():
            title = item["title"]

            if title.startswith("Início - ") or title.startswith("Fim - "):
                latest_by_title[f"{title}:{item['date']}"] = item
                continue

            if title not in latest_by_title:
                latest_by_title[title] = item
                continue

            current_item = latest_by_title[title]

            if item["date"] > current_item["date"]:
                latest_by_title[title] = item
                continue

            if (
                item["date"] == current_item["date"]
                and item["confidence"] > current_item["confidence"]
            ):
                latest_by_title[title] = item

        return sorted(
            latest_by_title.values(),
            key=lambda item: item["date"]
        )
