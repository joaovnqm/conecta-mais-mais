from textual.screen import Screen
from textual.widgets import Button, Input

def toggle_password_visibility(screen: Screen, input_id: str, button_id: str) -> None:
    """
    Função auxiliar para alternar a visibilidade da senha em um campo de input. Ela recebe a tela onde os widgets estão localizados, 
    o ID do widget de input de senha, e o ID do botão de toggle. A função localiza os widgets correspondentes usando os IDs 
    fornecidos, e alterna a propriedade "password" do widget de input para mostrar ou ocultar a senha. Além disso, ela atualiza o 
    rótulo do botão de toggle para refletir o estado atual da visibilidade da senha.
    """
    password_input = screen.query_one(f"#{input_id}", Input)
    toggle_button = screen.query_one(f"#{button_id}", Button)
    
    password_input.password = not password_input.password
    toggle_button.label = "Mostrar" if password_input.password else "Ocultar"