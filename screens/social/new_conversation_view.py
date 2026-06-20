from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static
from database.repositories.friendship_repository import friendship_services
from screens.social.chat_view import ConversationView

NEW_CONVERSATION_PAGE_CSS = """
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

#friends_list_container {
    width: 100%;
    height: auto;
}

.main_subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.section_hint {
    color: $text-muted;
    margin-bottom: 1;
}

.friend_row {
    width: 100%;
    height: auto;
    min-height: 5;
    border: round $primary;
    padding: 0 1;
    background: $surface;
}

.friend_info {
    width: 1fr;
    content-align: left middle;
}

.start_chat_button {
    width: 22;
    height: 3;
}

#button_return {
    width: 100%;
    margin-top: 1;
}
"""

class NewConversationView(Screen):
    """
    Tela para iniciar uma nova conversa com um amigo.
    Exibe a lista de amigos do usuário logado. Ao lado do nome
    de cada amigo há um botão verde para iniciar uma conversa.
    """
    CSS = NEW_CONVERSATION_PAGE_CSS
    def __init__(self, user_id: int) -> None:
        """Inicializa a tela de nova conversa para o usuário logado."""
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        """Monta a estrutura visual da tela de nova conversa."""
        friends = friendship_services.list_friends(self.user_id)
        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Nova Conversa", id="top_title")
                    yield Static("")

                yield Static("Selecione um amigo para iniciar uma conversa.", classes="section_hint")
                with VerticalScroll(id="friends_list_container"):
                    if friends:
                        for friend in friends:
                            yield self._build_friend_row(friend)

                    else:
                        yield Static("Você ainda não possui amigos. Adicione amigos na tela de Amigos!", classes="main_subtitle")

                yield Button("Voltar", id="button_return", variant="primary")

    def _build_friend_row(self, friend) -> Horizontal:
        """
        Monta uma linha de amigo exibindo:
        - nome completo e username do amigo num Static com Rich Text;
        - botão verde para iniciar a conversa.
        """
        username_display = (f"@{friend.username}" if friend.username else friend.email)
        friend_text = Text(f"{friend.name}\n")
        friend_text.append(username_display, style="dim")
        return Horizontal(
            Static(friend_text, classes="friend_info"),
            Button("Iniciar conversa", id=f"start_{friend.user_id}", classes="start_chat_button", variant="success"),
            classes="friend_row",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques nos botões da tela de nova conversa."""
        if event.button.id == "home_button":
            while self.app.screen is not self.app.screen_stack[2]:
                self.app.pop_screen()

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id and event.button.id.startswith("start_"):
            partner_id = int(event.button.id.split("_")[1])
            friends = friendship_services.list_friends(self.user_id)
            partner_name = next((f.name for f in friends if f.user_id == partner_id), f"Usuário #{partner_id}")
            self.app.push_screen(ConversationView(self.user_id, partner_id, partner_name))