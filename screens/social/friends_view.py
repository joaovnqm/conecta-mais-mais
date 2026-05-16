from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll, Horizontal

from database.repositories.friendship_repository import friendship_services

FRIENDS_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#friends_box {
    width: 70;
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

.section_title {
    margin-top: 1;
    text-style: bold;
}

#message {
    min-height: 1;
    color: $warning;
    margin-top: 1;
}

Input {
    width: 100%;
    margin-top: 1;
}

Button {
    width: 100%;
    margin-top: 1;
}

.request_row,
.friend_row {
    width: 100%
    height: auto;
    margin-top: 1;
}

.small_button {
    width: 16;
    margin-left: 1;
}
"""

CSS = FRIENDS_CSS

def __init__(self, user_id: int):
    super().__init__()
    self.user_id = user_id