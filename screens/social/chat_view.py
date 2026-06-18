from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static
from database.repositories.chat_repository import message_services

CONVERSATION_PAGE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box {
    width: 86;
    height: 40;
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

#back_button {
    width: 8;
    height: 3;
}

#top_title {
    content-align: center middle;
    height: 3;
    text-style: bold;
}

#messages_container {
    width: 100%;
    height: 1fr;
    border: round $primary;
    padding: 1;
    background: $surface;
    margin-bottom: 1;
}

.message_bubble {
    width: 100%;
    height: auto;
    min-height: 2;
    margin-bottom: 1;
}

.bubble_sent {
    content-align: right middle;
    color: $primary;
    text-style: bold;
}

.bubble_received {
    content-align: left middle;
    color: $text;
}

.bubble_time {
    color: $text-muted;
    content-align: right middle;
}

.empty_chat {
    content-align: center middle;
    color: $text-muted;
    height: 100%;
}

#input_bar {
    width: 100%;
    height: auto;
    layout: grid;
    grid-size: 2;
    grid-columns: 1fr 12;
    height: 3;
}

#message_input {
    width: 1fr;
    height: 3;
}

#send_button {
    width: 12;
    height: 3;
}

#status_message {
    min-height: 1;
    color: $error;
    content-align: center middle;
    margin-top: 1;
}
"""

class ConversationView(Screen):
    """
    Tela de conversa individual entre o usuário logado e um parceiro.
    Exibe:
    - histórico completo de mensagens em ordem cronológica;
    - campo de texto e botão para enviar novas mensagens;
    - mensagens enviadas destacadas à direita, recebidas à esquerda.
    As mensagens recebidas são marcadas como lidas ao abrir esta tela.
    """
    CSS = CONVERSATION_PAGE_CSS

    def __init__(self, user_id: int, partner_id: int, partner_name: str) -> None:
        """
        Inicializa a tela de conversa.
        Parâmetros:
        - user_id: ID do usuário logado.
        - partner_id: ID do parceiro de conversa.
        - partner_name: nome do parceiro (usado no título).
        """
        super().__init__()
        self.user_id = user_id
        self.partner_id = partner_id
        self.partner_name = partner_name

    def compose(self) -> ComposeResult:
        """Monta a estrutura visual da tela de conversa."""
        with Center():
            with Vertical(id="main_box"):
                with Horizontal(id="top_bar"):
                    yield Button("←", id="back_button", variant="primary")
                    yield Static(self.partner_name, id="top_title")
                    yield Static("")

                with VerticalScroll(id="messages_container"):
                    yield Static(
                        "Carregando mensagens...",
                        classes="empty_chat",
                        id="loading_label",
                    )

                with Horizontal(id="input_bar"):
                    yield Input(
                        placeholder="Digite uma mensagem...",
                        id="message_input",
                    )
                    yield Button("Enviar", id="send_button", variant="success")

                yield Static("", id="status_message")

    async def on_mount(self) -> None:
        """Carrega o histórico e marca mensagens recebidas como lidas."""
        message_services.mark_conversation_as_read(self.user_id, self.partner_id)
        await self._reload_messages()

    async def on_screen_resume(self) -> None:
        """Recarrega as mensagens ao retornar para esta tela."""
        message_services.mark_conversation_as_read(self.user_id, self.partner_id)
        await self._reload_messages()

    async def _reload_messages(self) -> None:
        """Limpa e repopula o container de mensagens com o histórico atualizado."""
        container = self.query_one("#messages_container")
        await container.remove_children()
        messages = message_services.get_conversation(self.user_id, self.partner_id)
        if not messages:
            await container.mount(
                Static("Nenhuma mensagem ainda. Diga olá! 👋", classes="empty_chat")
            )
            return

        for message in messages:
            await container.mount(self._build_message_bubble(message))

        container.scroll_end(animate=False)

    def _build_message_bubble(self, message) -> Vertical:
        """
        Monta o widget de exibição de uma mensagem.
        Mensagens enviadas pelo usuário logado aparecem em azul (direita).
        Mensagens recebidas aparecem em texto padrão (esquerda).
        """
        is_sent = message.sender_id == self.user_id
        time_str = ""
        if message.sent_at and len(message.sent_at) >= 16:
            time_str = message.sent_at[11:16]

        prefix = "Você" if is_sent else self.partner_name
        bubble_class = "bubble_sent" if is_sent else "bubble_received"
        content_text = f"{prefix}: {message.content}"
        return Vertical(
            Static(content_text, classes=f"message_bubble {bubble_class}"),
            Static(time_str, classes="bubble_time"),
            classes="message_bubble",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques nos botões da tela de conversa."""
        status = self.query_one("#status_message", Static)
        if event.button.id == "back_button":
            self.app.pop_screen()

        elif event.button.id == "send_button":
            await self._send_message(status)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Envia a mensagem ao pressionar Enter no campo de texto."""
        if event.input.id == "message_input":
            status = self.query_one("#status_message", Static)
            await self._send_message(status)

    async def _send_message(self, status: Static) -> None:
        """
        Valida e envia a mensagem digitada pelo usuário.
        Atualiza a tela com a nova mensagem ao enviar com sucesso.
        """
        input_widget = self.query_one("#message_input", Input)
        content = input_widget.value.strip()
        if not content:
            status.update("Digite uma mensagem antes de enviar.")
            return

        result = message_services.send_message(
            sender_id=self.user_id,
            receiver_id=self.partner_id,
            content=content,
        )

        if result is None:
            status.update("Não foi possível enviar a mensagem.")
            return

        input_widget.value = ""
        status.update("")
        await self._reload_messages()