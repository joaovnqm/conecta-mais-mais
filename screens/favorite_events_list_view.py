from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll

class FavoriteEventsList(Screen):
    def __init__(self, user_id: int):
        self.user_id = user_id
    
    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll():
                yield Static("Esses são os eventos favoritados.")