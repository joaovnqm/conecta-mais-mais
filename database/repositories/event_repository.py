import sqlite3
from typing import Optional, List
from database.repositories.interest_repository import interest_services
from models.event import Event
from utils.validations import validation_services

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

    def create_event(self, name: str, description: str, event_location: Optional[str], date: Optional[str], hour: Optional[str], creator_id: int, interest = "Social"):
        """
        Função que cria um evento. Ela valida os dados e retorna mensagens de erro específicas caso haja algum problema. 
        Se tudo estiver correto, o evento é criado. Se houver algum erro, a função retorna False, mensagem de erro, None.
        """
        name = name.strip()
        description = description.strip()
        if not validation_services.valid_name_events(name):
            return False, "O nome precisa ter pelo menos 2 caracteres."
        
        if not validation_services.valid_description(description):
            return False, "A descrição precisa ter entre 30 e 500 caracteres."
        
        if event_location:
            event_location = event_location.strip()

        if date:
            date = date.strip()
            if not validation_services.valid_date(date):
                return False, "O formato da data está errado. Por favor, siga o padrão dd-mm-aaaa e tenha certeza que a data ainda não passou."

        if hour:
            if date == "":
                return False, "Você precisa adicionar uma data para que a hora seja válida."
            
            date = date.strip()
            hour = hour.strip()
            if not validation_services.valid_hour(date, hour):
                return False, "O formato da hora está errado. Por favor, siga o padrão hh:mm e tenha certeza que colocou uma data e uma hora que ainda não passaram."
        
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
        
        interest_id = interest_services.index_interest(interest)
        self.cursor.execute(
            "INSERT INTO events_interests VALUES(?, ?)",
            (event_id, interest_id)
        )
        self.connection.commit()

        return True, "Evento criado com sucesso!"

    def check_events_by_interests(self, user_id: int) -> List[Event]:
        """
        Essa função retorna uma lista de eventos com base nos interesses do usuário. Ela primeiro obtém os interesses do usuário, 
        depois busca os eventos relacionados a esses interesses e retorna uma lista de objetos "Event" com (event_id, name, description). 
        A função também garante que não haja eventos duplicados na lista final.
        """
        interests = interest_services.check_user_interests(user_id)
        events = []
        seen_ids = set()

        for interest in interests:
            self.cursor.execute(
                "SELECT event_id FROM events_interests WHERE interest_id = ?",
                (interest.interest_id,)
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
        interest_id = interest_services.index_interest(selected_interest)
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
    
    def check_events_by_social(self, user_id: int):
        """
        Essa função retorna uma lista de eventos criados por amigos do usuário. Ela primeiro obtém a lista de amigos do usuário,
        depois busca os eventos criados por esses amigos e retorna uma lista de objetos "Event" com (event_id, name, description).
        """
        events = []
        friends = set()
        self.cursor.execute(
            "SELECT user_low_id from friendships WHERE user_high_id = ?",
            (user_id,)
        )

        result_low_id = self.cursor.fetchall()
        for friend in result_low_id:
            friends.add(friend[0])
        
        self.cursor.execute(
            "SELECT user_high_id from friendships WHERE user_low_id = ?",
            (user_id,)
        )

        result_high_id = self.cursor.fetchall()
        for friend in result_high_id:
            friends.add(friend[0])

        for friend in friends:
            self.cursor.execute(
                    "SELECT event_id, name, description FROM events WHERE creator_id = ?",
                    (friend,)
                )

            result = self.cursor.fetchall()
            for event in result:
                events.append(Event(event[0], event[1], event[2]))

        return events
    
    def check_events_by_user(self, user_id: int):
        """
        Essa função retorna uma lista de eventos criados pelo usuário. Ela busca os eventos criados por esse usuário e retorna uma lista de objetos "Event" com (event_id, name, description).
        """
        events = []
        self.cursor.execute(
            "SELECT event_id, name, description FROM events WHERE creator_id = ?",
            (user_id,)
        )

        result = self.cursor.fetchall()
        for event in result:
            events.append(Event(event[0], event[1], event[2]))

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