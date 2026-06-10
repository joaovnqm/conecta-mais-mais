import asyncio
import sqlite3
from textual.app import App
from database.repositories.important_dates_schema import important_dates_repository
from screens.auth.login_view import LoginView
from services.background_important_dates_updater import BackgroundImportantDatesUpdater


DATABASE_PATH = "conecta++.db"


class MinhaApp(App):
    TITLE = "Conecta++"

    def on_mount(self) -> None:
        """
        Inicializa a aplicação, prepara a estrutura de datas importantes
        e inicia o atualizador em segundo plano.
        """

        self.connection = sqlite3.connect(DATABASE_PATH)
        self.connection.execute("PRAGMA foreign_keys = ON;")

        important_dates_repository.initialize_important_dates_feature(self.connection)

        self.important_dates_updater = BackgroundImportantDatesUpdater(
            database_path=DATABASE_PATH,
            interval_seconds=60
        )

        asyncio.create_task(self.important_dates_updater.start())

        self.push_screen(LoginView())

    def on_unmount(self) -> None:
        """
        Para o atualizador e fecha a conexão principal ao encerrar o app.
        """

        if hasattr(self, "important_dates_updater"):
            self.important_dates_updater.stop()

        if hasattr(self, "connection"):
            self.connection.close()


if __name__ == "__main__":
    app = MinhaApp()
    app.run()
