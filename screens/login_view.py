from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Label
from textual.containers import Center, Vertical, Horizontal

from services.users import login
from services.validations import valid_email, password_error_message
from screens.register_view import RegisterView
from screens.main_page_view import MainPageView
from screens.forgot_password_view import ForgotPasswordView
from services.password_toggle import toggle_password_visibility


AUTH_CSS = """
Screen {
    align: center middle;
    background: $surface;
}

#auth-box {
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

Input {
    width: 100%;
    margin-top: 1;
}

Input.invalid {
    border: tall $error;
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

#password-row {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#password-row Input {
    width: 1fr;
    margin-top: 0;
}

#toggle_password {
    width: 12;
    min-width: 12;
    margin-top: 0;
    margin-left: 1;
}

#password-row Button {
    margin-top: 0;
}
"""

class LoginView(Screen):
    """
    Classe responsável pela tela de login. Ela é a primeira tela exibida para o usuário, e permite que ele faça login na plataforma
    utilizando seu e-mail e senha.
    """
    CSS = AUTH_CSS

    # Monta a interface de login com campos de e-mail e senha
    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth-box"):
                yield Static("Conecta++", id="title")
                yield Static("Faça login para continuar", classes="subtitle")

                yield Input(
                    placeholder="Digite seu e-mail...",
                    id="email"
                )

                with Horizontal(id="password-row"):
                    yield Input(
                        placeholder="Digite sua senha...",
                        id="password",
                        password=True
                    )
                    yield Button("Mostrar", id="toggle_password")

                yield Label("", id="message")

                yield Button("Entrar", id="button_login", variant="primary")
                yield Button("Esqueci minha senha", id="button_forgot_password")
                yield Button("Cadastrar", id="button_register_view")

    def reset_form(self) -> None:
        """
        Função auxiliar para resetar os campos do formulário de login. Ela limpa os valores dos campos de e-mail e senha, remove as 
        classes de campo inválido, limpa a mensagem de resposta, e foca o campo de e-mail para facilitar uma nova tentativa de login. 
        """
        email_input = self.query_one("#email", Input)
        password_input = self.query_one("#password", Input)
        message_label = self.query_one("#message", Label)

        email_input.value = ""
        password_input.value = ""

        email_input.remove_class("invalid")
        password_input.remove_class("invalid")

        message_label.update("")
        email_input.focus()    

    def _set_invalid_if_needed(self, input_widget: Input, is_invalid: bool) -> None:
        """
        Função auxiliar para adicionar ou remover a classe de campo inválido em um widget de input, com base no resultado da validação.
        Ela recebe o widget de input a ser atualizado e um booleano indicando se o campo é inválido ou não. Se o campo for inválido, a 
        classe "invalid" é adicionada ao widget, caso contrário, a classe é removida.
        """
        if is_invalid:
            input_widget.add_class("invalid")
        else:
            input_widget.remove_class("invalid")

    def _validate_email_field(self) -> None:
        """
        Função auxiliar para validar o campo de e-mail em tempo real. Ela coleta o valor do campo de e-mail, e se o campo não estiver vazio,
        ela chama a função valid_email para verificar se o e-mail é válido. Com base no resultado da validação, ela chama a função 
        _set_invalid_if_needed para atualizar a classe de campo inválido do widget de input.
        """
        email_input = self.query_one("#email", Input)
        value = email_input.value.strip()

        if not value:
            email_input.remove_class("invalid")
            return

        self._set_invalid_if_needed(email_input, not valid_email(value))

    def _validate_password_field(self) -> None:
        """
        Função auxiliar para validar o campo de senha em tempo real. Ela coleta o valor do campo de senha, e se o campo não estiver vazio,
        ela chama a função password_error_message para verificar se a senha atende aos critérios de segurança.
        """
        password_input = self.query_one("#password", Input)
        value = password_input.value

        if not value:
            password_input.remove_class("invalid")
            return

        error_message = password_error_message(value)
        self._set_invalid_if_needed(password_input, error_message is not None)

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Função que lida com os eventos de mudança nos campos de input. Ela verifica qual campo foi alterado, e chama a função de 
        validação correspondente para validar o campo em tempo real e atualizar a interface de acordo com o resultado da validação.
        """
        if event.input.id == "email":
            self._validate_email_field()
        elif event.input.id == "password":
            self._validate_password_field()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Função que lida com os eventos de clique nos botões da tela. Ela verifica qual botão foi clicado, e executa a ação correspondente:
        - Se for o botão de login, ela coleta os valores dos campos de e-mail e senha, chama a função de login, e se o login for bem-sucedido, 
        ela navega para a tela principal. Caso contrário, ela exibe a mensagem de erro retornada pela função de login.
        - Se for o botão de esqueci minha senha, ela navega para a tela de recuperação de senha.
        - Se for o botão de cadastrar, ela navega para a tela de registro. 
        - Se for o botão de toggle de senha, ela chama a função toggle_password_visibility para alternar a visibilidade da senha.
        """
        response = self.query_one("#message", Label)

        if event.button.id == "toggle_password":
            toggle_password_visibility(self, "password", "toggle_password")
            return

        if event.button.id == "button_login":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value

            success, message, name, user_id = login(email, password)

            if success:
                self.app.push_screen(MainPageView(user_id, name))
            else:
                response.update(message)

        elif event.button.id == "button_forgot_password":
            self.app.push_screen(ForgotPasswordView())

        elif event.button.id == "button_register_view":
            self.app.push_screen(RegisterView())