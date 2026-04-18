from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, Vertical

from services.users import get_user_profile

PROFILE_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#profile_box {
    width: 60%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#profile_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

.profile_label {
    margin-top: 1;
    text-style: bold;
}

.profile_value {
    color: $text-muted;
    margin-bottom: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class ProfileView(Screen):
    CSS = PROFILE_CSS
    
    # Recebe o user_id para saber qual perfil mostrar
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        
    # Monta a interface da tela de perfil
    def compose(self) -> ComposeResult:
        profile = get_user_profile(self.user_id)
        
        with Center():
            with Vertical(id="profile_box"):
                yield Static("Meu perfil", id="profile_title")
                
                if profile is None:
                    yield Static("Usuário não encontrado", id="name_value", classes="profile_value")
                else:
                    yield Static("Nome:", classes="profile_label")
                    yield Static(profile["name"], id="name_value", classes="profile_value")
                    yield Button("Alterar senha", id="button_edit_name")
                    
                    yield Static("Senha", classes="profile_label")
                    yield Static("••••••••", classes="profile_value")
                    yield Button("Alterar senha", id="button_change_password")
                    
                    yield Static("E-mail:", classes="profile_label")
                    yield Static(profile["email"], id="email_value", classes="profile_value")
                
                yield Button("Voltar", id="button_back", variant="error")