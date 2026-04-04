from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Input, Label
from textual.containers import Center
from database import register, login

# Tela 1


class InitialView(Screen):

    CSS = """
    Screen {
        align: center middle;
    }

    #middle {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Static(
                "Bem-vindo ao Conecta++\n\nSelecione a opção desejada.\n\n", id="middle")
        )
        yield Center(
            Button("Cadastro", id="button_register_view")
        )
        yield Center(
            Button("Login", id="button_login_view")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_register_view":
            self.app.push_screen(RegisterView())
        elif event.button.id == "button_login_view":
            self.app.push_screen(LoginView())

# Tela 2


class RegisterView(Screen):

    CSS = """
    Screen {
        align: center middle;
    }

    #middle {
        width: auto;
    }
    """

    CSS = """
    Input.register_login {
        border: tall $success 60%;
    }
    Input.register_login {
        border: tall $success;
    }
    Input {
        width: 40;
        margin: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Static(
                "Página de cadastro.\n\nPor favor, insira suas informações abaixo.", id="middle")
        )
        yield Center(
            Input(
                placeholder="Insira seu nome...", id="name", classes="register_login"
            )
        )
        yield Center(
            Input(
                placeholder="Insira seu e-mail...", id="email", classes="register_login"
            )
        )
        yield Center(
            Input(
                placeholder="Insira sua senha...", id="password", classes="register_login"
            )
        )
        yield Center(
            Input(
                placeholder="Confirme sua senha...", id="re_password", classes="register_login"
            )
        )
        yield Center(
            Input(
                placeholder="Escreva sua palavra de recuperação...", id="recovery_word", classes="register_login"
            )
        )
        yield Center(
            Button("Cadastrar", id="button_register")
        )
        yield Center(
            Button("Voltar", id="button_back")
        )
        yield Center(
            Label("Texto", id="response")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_register":
            name_input = self.query_one("#name", Input)
            email_input = self.query_one("#email", Input)
            password_input = self.query_one("#password", Input)
            re_password_input = self.query_one("#re_password", Input)
            recovery_word_input = self.query_one("#recovery_word", Input)
            name = name_input.value
            email = email_input.value
            password = password_input.value
            re_password = re_password_input.value
            recovery_word = recovery_word_input.value

            if password == re_password:
                alert = register(name, email, password, recovery_word)
                self.query_one("#response", Label).update(f", {alert}!")

            else:
                return

        elif event.button.id == "button_back":
            self.app.pop_screen()

# Tela 3


class LoginView(Screen):

    CSS = """
    Screen {
        align: center middle;
    }

    #middle {
        width: auto;
    }
    """

    CSS = """
    Input.register_login {
        border: tall $success 60%;
    }
    Input.register_login {
        border: tall $success;
    }
    Input {
        width: 40;
        margin: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Static(
                "Página de login.\n\nPor favor, insira suas informações abaixo.", id="middle")
        )
        yield Center(
            Input(
                placeholder="Insira seu e-mail...", id="email", classes="register_login"
            )
        )
        yield Center(
            Input(
                placeholder="Insira sua senha...", id="password", classes="register_login"
            )
        )
        yield Center(
            Button("Logar", id="button_login")
        )
        yield Center(
            Button("Voltar", id="button_back")
        )
        yield Center(
            Label("Texto", id="response")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button_login":
            email_input = self.query_one("#email", Input)
            password_input = self.query_one("#password", Input)
            email = email_input.value
            password = password_input.value
            name = login(email, password)
            self.query_one("#response", Label).update(f"Bem-vindo, {name}!")

        elif event.button.id == "button_back":
            self.app.pop_screen()

# -------- App principal --------


class MinhaApp(App):
    TITLE = "Conecta++"

    def on_mount(self) -> None:
        self.push_screen(InitialView())


if __name__ == "__main__":
    app = MinhaApp()
    app.run()
