from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Center, VerticalScroll
from screens.event_details_view import EventDetailsView
from services.favorite_events import check_favorited_events

FAVORITE_EVENTS_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#main_box { 
    width: 60;
    height: auto;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#main_title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

#events_container {
    content-align: center middle;
}

.main_subtitle{
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

.event_buttons{
    content-align: center middle;
}

Button {
    width: 100%;
    margin-top: 1;
}
"""

class FavoriteEventsList(Screen):
    CSS = FAVORITE_EVENTS_CSS

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
    
    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="main_box"):
                yield Static("Esses são os eventos favoritados.", id="main_title")
                yield VerticalScroll(id="events_container") 
                yield Button("Voltar", id="button_return", variant="error")
    
    async def update_events(self) -> None:
        container = self.query_one("#events_container")
        await container.query("*").remove()
        events = check_favorited_events(self.user_id)
        if events:
            for event in events:
                await container.mount(
                    Button(event[1], id=f"event_{event[0]}", classes="event_buttons")
                )
        else:
            await container.mount(
                Static("Nenhum evento favoritado encontrado.", classes="main_subtitle")
            )

    async def on_mount(self) -> None:
        await self.update_events()

    async def on_screen_resume(self) -> None:
        await self.update_events()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("event_buttons"):
            button_id = event.button.id
            if button_id:
                event_id = str(button_id.split("_")[1])
                self.app.push_screen(EventDetailsView(self.user_id, event_id))
        
        elif event.button.id == "button_return":
            self.app.pop_screen()