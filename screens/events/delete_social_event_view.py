from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical
from database.repositories.event_repository import event_services

DELETE_SOCIAL_EVENT_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#confirm_box {
    width: 86;
    height: auto;
    border: round $error;
    padding: 1 2;
    background: $panel;
}

#title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class DeleteSocialEventView(Screen):
    CSS = DELETE_SOCIAL_EVENT_CSS

    def __init__(self, event_id: int):
        super().__init__()
        self.event_id = event_id

    def compose(self) -> ComposeResult:
        """Essa função é responsável por compor a interface do usuário para a tela de confirmação de exclusão de evento social. 
        Ela cria uma caixa centralizada com um título, uma mensagem de confirmação e dois botões: um para confirmar a exclusão e outro 
        para cancelar e voltar à tela anterior."""
        with Center():
            with Vertical(id="confirm_box"):
                yield Static("Deletar evento", id="title")
                yield Static(
                    "Tem certeza que deseja deletar este evento?",
                    classes="subtitle"
                )
                yield Button("Sim, deletar", id="button_confirm_delete", variant="error")
                yield Button("Não, voltar", id="button_return")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Está função é chamada quando um botão é pressionado. Ela verifica qual botão foi pressionado e executa a ação correspondente."""
        if event.button.id == "button_confirm_delete":
            success, message = event_services.delete_event(self.event_id)
            
            if success:
                self.app.pop_screen()
                self.app.pop_screen()
                self.app.notify(message)

        elif event.button.id == "button_return":
            self.app.pop_screen()