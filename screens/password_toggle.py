from textual.screen import Screen
from textual.widgets import Button, Input

def toggle_password_visibility(screen: Screen, input_id: str, button_id: str) -> None:
    password_input = screen.query_one(f"#{input_id}", Input)
    toggle_button = screen.query_one(f"#{button_id}", Button)
    
    password_input.password = not password_input.password
    toggle_button.label = "Mostrar" if password_input.password else "Ocultar"