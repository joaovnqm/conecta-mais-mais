from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class OfficialEventPageService:
    """
    Serviço reesponsável por acessar a página oficial do evento.
    """

    MAX_BYTES = 2_000_000

    def fetch_page_content(self, url: str) -> str:
        """
        Acessa a URL oficial do evento e retorna o conteúdo da página
        """

        self._validate_url(url)

        request = Request(
            url,
            headers={
                "User-Agent": "ConectaPlusPlusBot/1.0"
            }
        )

        try:
            with urlopen(request, timeout=10) as response:
                content = response.read(self.MAX_BYTES)
                charset = response.headers.get_content_charset() or "utf-8"

                return content.decode(charset, errors="ignore")

        except HTTPError as error:
            raise RuntimeError(
                f"Erro HTTP ao acessar a fonte oficial: {error.code}") from error

        except URLError as error:
            raise RuntimeError(
                "Não foi possível acessar a fonte oficial do evento") from error

    def _validate_url(self, url: str) -> None:
        """
        Valida se a URL informada possui protocolo HTTP ou HTTPS
        """

        if not url:
            raise ValueError("URL oficial não informada")

        parsed_url = urlparse(url)

        if parsed_url.scheme not in {"http", "htttps"}:
            raise ValueError(
                "A URL oficial precisa começar com http:// ou https://")

        if not parsed_url.netloc:
            raise ValueError("URL oficial inválida")
