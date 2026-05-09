import sqlite3
from dataclasses import dataclass
from typing import Optional, List
from services.interests import check_interests_id, index_interest
from services.validations import valid_name_events, valid_date, valid_hour

@dataclass
class Event:
    """Representa um evento no sistema. O decorador dataclass já constroi o __init__ de forma automática dentro do programa.

    Atributos:
    - event_id: Identificador único (None para eventos ainda não persistidos).
    - name: Nome do evento (string).
    - description: Descrição do evento (string).
    - event_location: Local do evento (string).
    - date: Data do evento (string).
    - hour: Hora do evento (string).
    - creator_id: Identificador do criador do evento (int).
    """
    event_id: Optional[int]
    name: str
    description: str
    event_location: Optional[str] = None
    date: Optional[str] = None
    hour: Optional[str] = None
    creator_id: int = None

class EventServices:
    """Classe responsável por operações relacionadas aos eventos e pela conexão com o banco de dados.

    Esta classe encapsula a criação da tabela, inserção e consultas de eventos.
    """

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """
        Cria a tabela "events" caso ela não exista.
        event_id: identificador único do evento
        name: nome do evento
        description: descrição do evento
        event_location: local do evento
        date: data do evento
        hour: hora do evento
        creator_id: identificador do criador do evento (chave estrangeira para a tabela users)
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events(
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                event_location TEXT,
                date TEXT,
                hour TEXT,
                creator_id INTEGER NOT NULL,
                FOREIGN KEY (creator_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()

    def create_event(self, name: str, description: str, event_location: Optional[str], date: Optional[str], hour: Optional[str], creator_id: int, *interests: list):
        """
        Função que cria um evento. Ela valida os dados e retorna mensagens de erro específicas caso haja algum problema. 
        Se tudo estiver correto, o evento é criado. Se houver algum erro, a função retorna False, mensagem de erro, None.
        """
        name = name.strip()
        description = description.strip()
        if not valid_name_events(name):
            return False, "O nome precisa ter pelo menos 2 caracteres."
        
        if description == None:
            return False, "Por favor, insira uma descrição para o evento."
        
        if event_location:
            event_location = event_location.strip()

        if date:
            date = date.strip()
            if not valid_date(date):
                return False, "O formato da data está errado. Por favor, siga o padrão dd-mm-aaaa."

        if hour:
            hour = hour.strip()
            if not valid_hour(hour):
                return False, "O formato da hora está errado. Por favor, siga o padrão hh:mm."
        
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM events WHERE name = ? AND creator_id = ?)",
            (name, creator_id,)
        )
        event_registered = bool(self.cursor.fetchone()[0])

        if event_registered:
            return False, "Esse evento já foi cadastrado.", None
        
        self.cursor.execute(
            "INSERT INTO events VALUES(?, ?, ?, ?, ?, ?, ?)",
            (None, name, description, event_location, date, hour, creator_id)
        )
        
        self.connection.commit()

        event_id = self.cursor.lastrowid

        for interest in interests:
            interest_id = index_interest(interest)
            self.cursor.execute(
                "INSERT INTO events_interests VALUES(?, ?)",
                (event_id, interest_id)
            )
            self.connection.commit()

    def check_events_with_interests(self, user_id: int) -> List[Event]:
        """
        Essa função retorna uma lista de eventos com base nos interesses do usuário. Ela primeiro obtém os interesses do usuário, 
        depois busca os eventos relacionados a esses interesses e retorna uma lista de objetos "Event" com (event_id, name, description). 
        A função também garante que não haja eventos duplicados na lista final.
        """
        interests = check_interests_id(user_id)
        events = []
        seen_ids = set()

        for interest in interests:
            self.cursor.execute(
                "SELECT event_id FROM events_interests WHERE interest_id = ?",
                (interest[0],)
            )

            for row in self.cursor.fetchall():
                event_id = row[0]
                if event_id in seen_ids:
                    continue

                self.cursor.execute(
                    "SELECT name, description FROM events WHERE event_id = ?",
                    (event_id,)
                )
                result = self.cursor.fetchone()
                if result:
                    seen_ids.add(event_id)
                    events.append(Event(event_id, result[0], result[1]))

        return events

    def check_events_by_interest(self, selected_interest: str):
        """
        Essa função retorna uma lista de eventos com base em um interesse selecionado. Ela primeiro obtém o id do interesse,
        depois busca os eventos relacionados a esse interesse e retorna uma lista de objetos "Event" com (event_id, name, description).
        """
        events = []
        interest_id = index_interest(selected_interest)
        self.cursor.execute(
            "SELECT event_id FROM events_interests WHERE interest_id = ?",
            (interest_id,)
        )

        for row in self.cursor.fetchall():
            event_id = row[0]
            self.cursor.execute(
                "SELECT name, description FROM events WHERE event_id = ?",
                (event_id,)
            )
            result = self.cursor.fetchone()
            events.append(Event(event_id, result[0], result[1]))

        return events

    def check_event(self, event_id) -> object:
        """
        Essa função retorna os detalhes de um evento específico com base no id do evento. 
        Ela retorna uma tupla contendo todas as informações do evento, incluindo o nome, descrição, local, data, hora e id do criador.
        """
        self.cursor.execute(
            "SELECT * FROM events WHERE event_id = ?",
            (event_id,)
        )
        
        event = self.cursor.fetchone()

        return Event(event[0], event[1], event[2], event[3], event[4], event[5], event[6])
    
event_services = EventServices()