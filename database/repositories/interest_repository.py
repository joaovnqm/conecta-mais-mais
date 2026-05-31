import sqlite3
from models.interest import Interest

class InterestServices:
    """Classe responsável por operações relacionadas aos interesses e pela conexão com o DB."""
    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """ Cria as tabelas "interests", "users_interests" e "events_interests" caso elas não existam.
        interests: tabela que armazena os interesses disponíveis no sistema.
        users_interests: tabela que relaciona os usuários com seus interesses.
        events_interests: tabela que relaciona os eventos com seus interesses.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interests(
                interest_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, 
                name NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_interests(
                user_id INTEGER,
                interest_id INTEGER,
                PRIMARY KEY(user_id, interest_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (interest_id) REFERENCES interests(interest_id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events_interests(
                event_id INTEGER,
                interest_id INTEGER,
                PRIMARY KEY(event_id, interest_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
                FOREIGN KEY (interest_id) REFERENCES interests(interest_id) ON DELETE CASCADE
            )
        """)

    def index_interest(self, interest: str) -> int:
        """
        Essa função retorna o id de um interesse. Se o interesse não existir, ele é criado e o id é retornado.
        """
        self.cursor.execute(
            "SELECT interest_id FROM interests WHERE name = ?",
            (interest,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        self.cursor.execute(
            "INSERT INTO interests (name) VALUES (?)",
            (interest,)
        )
        self.connection.commit()
        
        return self.cursor.lastrowid
    
    def name_interest(self, interest_id: int) -> str | None:
        """
        Essa função retorna o nome de um interesse a partir do seu id.
        """
        self.cursor.execute(
            "SELECT name FROM interests WHERE interest_id = ?",
            (interest_id,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        return None

    def add_interests(self, user_id, interest):
        """
        Essa função adiciona um interesse à lista de interesses do usuário. Ela verifica se o interesse já foi adicionado e, se não,
        adiciona o interesse à lista de interesses do usuário.
        """
        interest_id = self.index_interest(interest)
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users_interests WHERE user_id = ? AND interest_id = ?)",
            (user_id, interest_id,)
        )
        interest_registered = bool(self.cursor.fetchone()[0])

        if interest_registered:
            return "Algum desses interesses já foi cadastrado.", False
        
        self.cursor.execute(
            "INSERT INTO users_interests VALUES (?, ?)", (user_id, interest_id,)
        )
        self.connection.commit()

        return "Interesse(s) adicionado(s) com sucesso!", True
    
    def remove_interests(self, user_id, interest):
        """
        Essa função remove um interesse da lista de interesses do usuário. Ela verifica se o interesse já foi removido e, se não,
        remove o interesse da lista de interesses do usuário.
        """
        interest_id = self.index_interest(interest)
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users_interests WHERE user_id = ? AND interest_id = ?)",
            (user_id, interest_id,)
        )
        interest_registered = bool(self.cursor.fetchone()[0])

        if not interest_registered:
            return "Algum desses interesses já foi deletado.", False
        
        self.cursor.execute(
            "DELETE FROM users_interests WHERE user_id = ? AND interest_id = ?", (user_id, interest_id,)
        )
        self.connection.commit()

        return "Interesse(s) deletado(s) com sucesso!", True
    
    def check_user_interests(self, user_id) -> list[Interest]:
        """
        Essa função consulta a tabela de users_interests para obter os ids dos interesses
        e os nomes dos interesses correspondentes, e retorna uma lista de objetos de interesses do usuário.
        """
        user_id = str(user_id)
        user_interests = []
        self.cursor.execute(
            "SELECT interest_id FROM users_interests WHERE user_id = ?",
            (user_id,)
            )
        user_interests_id = self.cursor.fetchall()
        for interest_id in user_interests_id:
            self.cursor.execute(
                "SELECT name FROM interests WHERE interest_id = ?",
                (interest_id[0],)
            )
            user_interests_name = self.cursor.fetchone()
            user_interests.append(Interest(interest_id[0], user_interests_name[0]))

        return user_interests

    def check_all_interests(self) -> tuple:
        """
        Essa função retorna uma tupla de todos os interesses cadastrados. Ela consulta a tabela de interesses e retorna 
        uma tupla contendo os nomes de todos os interesses cadastrados.
        """
        interests = []
        self.cursor.execute(
            "SELECT interest_id, name FROM interests"
        )
        interests_tuples = self.cursor.fetchall()
        for interest in interests_tuples:
            interests.append(Interest(interest[0], interest[1]))

        return interests

    def check_event_interests(self, event_id) -> list[Interest] | None:
        """
        Essa função consulta a tabela de events_interests para obter os ids dos interesses
        e os nomes dos interesses correspondentes, e retorna uma lista de objetos de interesses do evento.
        """
        event_id = str(event_id)
        event_interests = []
        self.cursor.execute(
            "SELECT interest_id FROM events_interests WHERE event_id = ?",
            (event_id,)
            )
        event_interests_id = self.cursor.fetchall()

        if not event_interests_id:
            return None

        for interest_id in event_interests_id:
            name = self.name_interest(interest_id[0])
            event_interests.append(Interest(interest_id[0], name))

        return event_interests


interest_services = InterestServices()