from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static
from screens.social.new_conversation_view import NewConversationView
from screens.social.chat_view import ConversationView
from database.repositories.chat_repository import message_services

CHATS_PAGE_CSS = """
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
    grid-columns: 6 1fr 20;
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

#new_conversation_button {
    height: 3;
}

#conversations_container {
    width: 100%;
    height: auto;
}

.main_subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
    margin-top: 1;
}

.conversation_row {
    layout: grid;
    grid-size: 2;
    grid-columns: 1fr 10;
    height: auto;
    min-height: 5;
    margin-bottom: 1;
    border: round $primary;
    padding: 0 1;
    background: $surface;
}

.conversation_info {
    width: 100%;
    height: auto;
    padding: 1 0;
}

.conversation_partner {
    text-style: bold;
    height: auto;
    min-height: 1;
}

.conversation_preview {
    color: $text-muted;
    height: auto;
    min-height: 1;
}

.conversation_time {
    color: $text-muted;
    height: auto;
    min-height: 1;
}

.unread_badge {
    color: $success;
    text-style: bold;
    height: auto;
    min-height: 1;
}

.open_chat_button {
    width: 10;
    height: 3;
    margin: 1 0;
}

#button_return {
    width: 100%;
    margin-top: 2;
}
"""


class ChatsView(Screen):
    """
    Tela de listagem de conversas do usuário logado.

    Exibe:
    - botão de início (🏠) e botão para iniciar nova conversa na barra superior;
    - lista de conversas ativas, com nome do parceiro, prévia da última
      mensagem, horário e indicador de não lidas;
    - mensagem de estado vazio quando não há conversas.
    """

    CSS = CHATS_PAGE_CSS

    def __init__(self, user_id: int) -> None:
        """Inicializa a tela de conversas para o usuário logado."""
        super().__init__()
        self.user_id = user_id

    def compose(self) -> ComposeResult:
        """Monta a estrutura visual inicial da tela de conversas."""

        conversations = message_services.get_user_conversations(self.user_id)

        with Center():
            with VerticalScroll(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("🏠", id="home_button", variant="primary")
                    yield Static("Conversas", id="top_title")
                    yield Button(
                        "✉ Nova",
                        id="new_conversation_button",
                        variant="success",
                    )

                with VerticalScroll(id="conversations_container"):
                    if conversations:
                        for conversation in conversations:
                            yield self._build_conversation_row(conversation)
                    else:
                        yield Static(
                            "Nenhuma conversa ainda. Clique em '✉ Nova' para começar!",
                            classes="main_subtitle",
                        )

                yield Button("Voltar", id="button_return", variant="primary")

    async def on_screen_resume(self) -> None:
        """Recarrega a lista de conversas ao retornar para esta tela."""
        await self._reload_conversations()

    async def _reload_conversations(self) -> None:
        """Atualiza o container de conversas com os dados mais recentes."""

        container = self.query_one("#conversations_container")
        await container.remove_children()

        conversations = message_services.get_user_conversations(self.user_id)

        if conversations:
            for conversation in conversations:
                await container.mount(
                    self._build_conversation_row(conversation)
                )
        else:
            await container.mount(
                Static(
                    "Nenhuma conversa ainda. Clique em '✉ Nova' para começar!",
                    classes="main_subtitle",
                )
            )

    def _build_conversation_row(self, conversation) -> Horizontal:
        """
        Monta uma linha de conversa exibindo:
        - nome do parceiro;
        - prévia da última mensagem;
        - data/hora da última mensagem;
        - contador de não lidas (se houver);
        - botão para abrir a conversa.
        """

        preview_text = conversation.last_message or "Sem mensagens ainda."
        if len(preview_text) > 55:
            preview_text = preview_text[:52] + "..."

        time_text = ""
        if conversation.last_message_at:
            raw = conversation.last_message_at
            time_text = raw[11:16] if len(raw) >= 16 else raw

        unread_text = (
            f"● {conversation.unread_count} não lida(s)"
            if conversation.unread_count > 0
            else ""
        )

        info_column = Vertical(
            Static(conversation.partner_name, classes="conversation_partner"),
            Static(preview_text, classes="conversation_preview"),
            Static(time_text, classes="conversation_time"),
            Static(unread_text, classes="unread_badge"),
            classes="conversation_info",
        )

        open_button = Button(
            "Abrir",
            id=f"chat_{conversation.partner_id}",
            classes="open_chat_button",
            variant="primary",
        )

        return Horizontal(
            info_column,
            open_button,
            classes="conversation_row",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques nos botões da tela de conversas."""
        if event.button.id == "home_button":
            self.app.pop_screen()

        elif event.button.id == "new_conversation_button":
            self.app.push_screen(NewConversationView(self.user_id))

        elif event.button.id == "button_return":
            self.app.pop_screen()

        elif event.button.id and event.button.id.startswith("chat_"):
            partner_id = int(event.button.id.split("_")[1])

            conversations = message_services.get_user_conversations(self.user_id)
            partner_name = next(
                (c.partner_name for c in conversations if c.partner_id == partner_id),
                f"Usuário #{partner_id}",
            )

            self.app.push_screen(
                ConversationView(self.user_id, partner_id, partner_name)
            )