import sqlite3

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

    def check_interests_id(self, user_id) -> tuple:
        """
        Essa função retorna uma tupla de interesses com base no id do usuário. Ela consulta a tabela de interesses dos 
        usuários para obter os ids dos interesses, e retorna uma tupla contendo os ids dos interesses do usuário.
        """
        user_id = str(user_id)
        self.cursor.execute(
            "SELECT interest_id FROM users_interests WHERE user_id = ?",
            (user_id,)
            )
        user = self.cursor.fetchall()
        user_interests = user

        return user_interests

    def check_interests_name(self, user_id) -> tuple:
        """
        Essa função retorna uma tupla de interesses com base no id do usuário. Ela consulta a tabela de interesses dos 
        usuários para obter os ids dos interesses, depois consulta a tabela de interesses para obter os nomes
        dos interesses, e retorna uma tupla contendo os nomes dos interesses do usuário.
        """
        interests_id = self.check_interests_id(user_id)
        interests_names = []
        for interest in interests_id:
            self.cursor.execute(
                "SELECT name FROM interests WHERE interest_id = ?",
                (interest[0],)
                )
            interest_result = self.cursor.fetchone()
            interests_names.append(interest_result[0])

        return interests_names

    def check_all_interests(self) -> tuple:
        """
        Essa função retorna uma tupla de todos os interesses cadastrados. Ela consulta a tabela de interesses e retorna 
        uma tupla contendo os nomes de todos os interesses cadastrados.
        """
        self.cursor.execute(
            "SELECT name FROM interests"
        )
        interests = self.cursor.fetchall()

        return interests
    
interest_services = InterestServices()