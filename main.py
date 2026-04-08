from textual.app import App
from screens.login_view import LoginView


class MinhaApp(App):
    TITLE = "Conecta++"

    def on_mount(self) -> None:
        self.push_screen(LoginView())


if __name__ == "__main__":
    app = MinhaApp()
    app.run()
