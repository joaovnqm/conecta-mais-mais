from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input
from textual.containers import Center, VerticalScroll, Horizontal, Vertical
from database.repositories.friendship_repository import friendship_services

class FriendsView(Screen):
    CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#friends_box {
    width: 86;
    height: 38;
    border: round $primary;
    padding: 1 2;
    background: $panel;
}

#title {
    content-align: center middle;
    text-style: bold;
    margin-bottom: 1;
}

#subtitle {
    content-align: center middle;
    color: $text-muted;
    margin-bottom: 1;
}

.section_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}

.section_title {
    text-style: bold;
    margin-bottom: 1;
}

.section_hint {
    color: $text-muted;
    margin-bottom: 1;
}

#message {
    min-height: 1;
    color: $warning;
    margin-top: 1;
    content-align: center middle;
}

Input {
    width: 100%;
    margin-top: 1;
}

#button_send_request {
    width: 100%;
    margin-top: 1;
}

#button_back {
    width: 100%;
    margin-top: 1;
}

#requests_container,
#friends_container {
    width: 100%;
    height: auto;
}

.request_row,
.friend_row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

.empty_state {
    color: $text-muted;
    margin-top: 1;
}

.small_button {
    width: 14;
    min-width: 14;
    margin-left: 1;
}

.request_card {
    width: 100%;
    height: auto;
    border: round $primary;
    padding: 1 2;
    margin-top: 1;
    background: $surface;
}

.request_actions {
    width: 100%;
    height: auto;
    margin-top: 1;
}

.request_actions Button {
    width: 1fr;
    margin-right: 1;
}

.person_text {
    width: 100%;
    content-align: left middle;
}

"""


    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        
    def compose(self) -> ComposeResult:
        with Center():
            with VerticalScroll(id="friends_box"):
                yield Static("Amigos", id="title")
                yield Static(
                    "Gerencie suas conexões sociais dentro do Conecta++.",
                    id="subtitle"
                )

                with Vertical(classes="section_card"):
                    yield Static("Adicionar amigo por e-mail", classes="section_title")
                    yield Static(
                        "Digite o e-mail de um usuário cadastrado para enviar uma solicitação.",
                        classes="section_hint"
                    )
                    yield Input(
                        placeholder="Exemplo: fulano@email.com",
                        id="friend_email"
                    )
                    yield Button(
                        "Enviar solicitação",
                        id="button_send_request",
                        variant="primary"
                    )

                yield Static("", id="message")

                with Vertical(classes="section_card"):
                    yield Static("Solicitações recebidas", classes="section_title")
                    yield Vertical(id="requests_container")

                with Vertical(classes="section_card"):
                    yield Static("Meus amigos", classes="section_title")
                    yield Vertical(id="friends_container")

                yield Button("Voltar", id="button_back", variant="primary")
                
    async def on_mount(self) -> None:
        await self.reload_social_data()

    async def on_screen_resume(self) -> None:
        await self.reload_social_data()
        
    async def reload_social_data(self) -> None:
        await self.reload_pending_requests()
        await self.reload_friends()

    async def reload_pending_requests(self) -> None:
        container = self.query_one("#requests_container")
        await container.remove_children()

        requests = friendship_services.list_pending_requests(self.user_id)

        if not requests:
            await container.mount(
                Static("Nenhuma solicitação pendente.", classes="empty_state")
            )
            return

        for request in requests:
            requester_id = request.requester_id
            name = request.requester_name
            email = request.requester_email

            request_card = Vertical(classes="request_card")
            await container.mount(request_card)

            await request_card.mount(
                Static(f"{name} - {email}", classes="person_text")
            )

            actions = Horizontal(classes="request_actions")
            await request_card.mount(actions)

            await actions.mount(
                Button(
                    "Aceitar",
                    id=f"accept_{requester_id}",
                    variant="success"
                )
            )

            await actions.mount(
                Button(
                    "Recusar",
                    id=f"reject_{requester_id}",
                    variant="error"
                )
            )
 

    async def reload_friends(self) -> None:
        container = self.query_one("#friends_container")
        await container.remove_children()

        friends = friendship_services.list_friends(self.user_id)

        if not friends:
            await container.mount(
                Static("Você ainda não possui amigos adicionados.", classes="empty_state")
            )
            return

        for friend in friends:
            friend_id = friend.user_id
            name = friend.name
            email = friend.email

            row = Horizontal(classes="friend_row")
            await container.mount(row)

            await row.mount(
                Static(f"{name} - {email}", classes="person_text")
            )

            await row.mount(
                Button(
                    "Remover",
                    id=f"remove_{friend_id}",
                    variant="error",
                    classes="small_button"
                )
            )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        message = self.query_one('#message', Static)
        
        if event.button.id == 'button_send_request':
            email = self.query_one('#friend_email', Input).value
            
            success, response_message = friendship_services.send_friend_request(
                self.user_id, email
            )
            
            message.update(response_message)
            
            if success:
                self.query_one('#friend_email', Input).value = ''
                
            await self.reload_social_data()
            return
        
        if event.button.id and event.button.id.startswith("accept_"):
            requester_id = int(event.button.id.split("_")[1])

            success, response_message = friendship_services.accept_friend_request(
                self.user_id,
                requester_id
            )

            message.update(response_message)
            await self.reload_social_data()
            return
        
        if event.button.id and event.button.id.startswith("reject_"):
            requester_id = int(event.button.id.split("_")[1])

            success, response_message = friendship_services.reject_friend_request(
                self.user_id,
                requester_id
            )

            message.update(response_message)
            await self.reload_social_data()
            return
        
        if event.button.id and event.button.id.startswith("remove_"):
            friend_id = int(event.button.id.split("_")[1])

            success, response_message = friendship_services.remove_friend(
                self.user_id,
                friend_id
            )

            message.update(response_message)
            await self.reload_social_data()
            return
        
        if event.button.id == 'button_back':
            self.app.pop_screen()