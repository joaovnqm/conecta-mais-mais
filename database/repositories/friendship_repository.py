import sqlite3
from typing import List, Optional


class FriendshipServices:
    """
    Classe responsável pelas operações sociais de amizade:
    - criar tabela de amizades;
    - enviar solicitação
    - aceitar solicitação
    - recusar solicitação
    - listar amigos
    - listar solicitações pendentes.
    """

    def __init__(self, database_path: str = "connecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()
