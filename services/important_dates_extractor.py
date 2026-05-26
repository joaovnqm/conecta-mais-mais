import re
from datetime import datetime


class ImportantDatesExtractor:
    """
    Serviço reesponsável por extrair datas importantes de um texto
    """

    DATE_PATTERNS = [
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b",
    ]

    KEYWORDS = {
        "inscrição": "Período de inscrição",
        "inscrições": "Período de inscrição",
        "inicio": "Início",
        "início": "Início",
        "começa": "Início",
        "começam": "Início",
        "fim": "Fim",
        "final": "Fim",
        "encerra": "Encerramento",
        "encerramento": "Encerramento",
        "evento": "Data do evento",
        "realização": "Data do evento",
        "resultado": "Resultado",
        "portões": "Abertura dos portões",
        "portoes": "Abertura dos portões",
        "credenciamento": "Credenciamento",
        "pagamento": "Prazo de pagamento",
        "cancelamento": "Prazo de cancelamento",
    }

    def extract(self, text: str, source_url: str) -> list[dict]:
        """
        Extrai datas do texto e retorna uma lista de dicionários estruturados
        """

        if not text:
            return []

        clean_text = self._clean_text(text)
        important_dates = []

        for pattern in self.DATE_PATTERNS:
            for match in re.finditer(pattern, clean_text):
                iso_date = self._convert_match_to_iso_date(match)

                if not iso_date:
                    continue

                context = self._get_context(
                    clean_text, match.start(), match.end())
                title = self._infer_title(context)
                time = self._extract_time(context)
                confidence = self._calculate_confidence(context, title, time)

                if confidence < 0.55:
                    continue

                important_dates.append({
                    "title": title,
                    "date": iso_date,
                    "time": time,
                    "source_url": source_url,
                    "confidence": confidence,
                })

            return self._remove_duplicates(important_dates)

    def _clean_text(self, text: str) -> str:
        """
        Remove scripts, estilos e tags HTML para facilitar a extração.
        """

        text = re.sub(r"<script.*?</script>", " ", text,
                      flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", " ", text,
                      flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _convert_match_to_iso_date(self, match: re.Match) -> str | None:
        """
        Converte uma data encontrada no teexto para o formato ISO: YYYY-MM-DD.
        """

        day, month, year = match.groups()

        try:
            parsed_date = datetime(
                int(year),
                int(month),
                int(day)
            ).date()

            return parsed_date.isoformat()

        except ValueError:
            return None

    def _get_context(self, text: str, start: int, end: int, window: int = 140) -> str:
        """
        Captura um trecho ao redor da data encontrada para entender o seu significado.
        """

        context_start = max(0, start - window)
        context_end = min(len(text), end + window)

        return text[context_start: context_end].lower()

    def _infer_title(self, context: str) -> str:
        """
        Infere o título da data com base em palavras próximas
        """

        for keyword, title in self.KEYWORDS.items():
            if keyword in context:
                return title

            return "Data importante"

    def _extract_time(self, context: str) -> str | None:
        """
        Extrai horário do contexto, se existir
        """

        match = re.search(
            r"\b(\d{1,2})h(\d{2})?\b|\b(\d{1,2}):(\d{2})\b",
            context
        )

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
        Calcula uma pontuação simples deee confiança para a data encontrada
        """

        confidence = 0.5

        if title != "Data importante":
            confidence += 0.3

        if time:
            confidence += 0.1

        if any(word in context for word in ["oficial", "programação", "cronograma", "agenda"]):
            confidence += 0.05

        return min(confidence, 0.95)

    def _remove_duplicates(self, dates: list[dict]) -> list[dict]:
        """
        Remove datas duplicadas, preservando a versão com mais confiança
        """

        unique_dates = {}

        for item in dates:
            key = (
                item["title"],
                item["date"],
                item["time"]
            )

            if key not in unique_dates:
                unique_dates[key] = item
                continue

            if item["confidence"] > unique_dates[key]["confidence"]:
                unique_dates[key] = item

        return list(unique_dates.values())
