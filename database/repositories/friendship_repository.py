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

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                friendship_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                
                user_low_id INTEGER NOT NULL,
                user_high_id INTEGER NOT NULL,  
                
                    
                
                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'accepted', 'rejected', 'blocked')
                ),
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                update_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(user_low_id, user_high_id),
                
                FOREIGN KEY (user_low_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                
                FOREIGN KEY (user_high_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                    
                FOREIGN KEY (requester_id)
                    REFERENCES users(user_id)
                    ON DELETE  CASCADE,
                
                CHECK(user_low_id < user_high_id)
            )
            """)
        self.connection.commit()

    def make_user_pair(self, user_id_1: int, user_id_2: int) -> tuple[int, int]:
        if user_id_1 == user_id_2:
            raise ValueError("Usuário não pode adicionar a si mesmo")

        return min(user_id_1, user_id_2), max(user_id_1, user_id_2)
