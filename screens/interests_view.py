from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Checkbox, Label
from textual.containers import Center, Vertical
from screens.main_page_view import MainPageView
from services.interests import add_interests

AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#interest_box {
    width: 52;
    height: auto;
    border: round $primary;
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

#message {
    height: 2;
    margin-top: 1;
    color: $warning;
}
"""

class InterestsView(Screen):
    CSS = AUTH_CSS

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="interest_box"):
                yield Static("Conecta++", id="title")
                yield Static("Selecione os seus interesses abaixo", classes="subtitle")
                yield Checkbox("Inteligência Artificial", id="ia", classes="interests")
                yield Checkbox("Engenharia de Software", id="eng_software", classes="interests")
                yield Checkbox("Cibersegurança", id="cyber", classes="interests")
                yield Checkbox("Empreendedorismo", id="empreendedorismo", classes="interests")
                yield Checkbox("Ciência de Dados", id="ciencia_dados", classes="interests")
                yield Button("Definir interesses", id="button_register_interests", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "button_register_interests":
                checkboxes = self.query(".interests")
                for checkbox in checkboxes:
                    if checkbox.value == True:
                        add_interests(self.user_id, str(checkbox.label))

                    else:
                        continue

                self.notify("Interesse(s) adicionado(s) com sucesso!")
                self.app.push_screen(MainPageView(self.user_id, self.user_name))