import sqlite3
from services.interests import check_interests_id, index_interest
from services.validations import valid_name_events, valid_date, valid_hour

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Criando tabela eventos caso não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY AUTOINCREMENT, name NOT NULL, description NOT NULL, "
    "event_location, date, hour, creator_id INTEGER NOT NULL, FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE)"
    )

# Criando tabela de áreas de interesse dos eventos caso ela não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS events_interests(event_id INTEGER, interest_id INTEGER, PRIMARY KEY(event_id, interest_id), " \
    "FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE, FOREIGN KEY (interest_id) REFERENCES interests(interest_id) " \
    "ON DELETE CASCADE)"
    )

def create_event(name: str, description: str, event_location: str, date: str, hour: str, creator_id: int, *interests: list):
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
    
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM events WHERE name = ? AND creator_id = ?)",
        (name, creator_id,)
    )
    event_registered = bool(cursor.fetchone()[0])

    if event_registered:
        return False, "Esse evento já foi cadastrado.", None
    
    cursor.execute(
        "INSERT INTO events VALUES(?, ?, ?, ?, ?, ?, ?)",
        (None, name, description, event_location, date, hour, creator_id)
    )
    
    connection.commit()

    event_id = cursor.lastrowid

    for interest in interests:
        interest_id = index_interest(interest)
        cursor.execute(
            "INSERT INTO events_interests VALUES(?, ?)",
            (event_id, interest_id)
        )
        connection.commit()

def check_events_with_interests(user_id: int) -> list:
    """
    Essa função retorna uma lista de eventos com base nos interesses do usuário. Ela primeiro obtém os interesses do usuário, 
    depois busca os eventos relacionados a esses interesses e retorna uma lista de tuplas (event_id, event_name). 
    A função também garante que não haja eventos duplicados na lista final.
    """
    interests = check_interests_id(user_id)
    events = []
    seen_ids = set()

    for interest in interests:
        cursor.execute(
            "SELECT event_id FROM events_interests WHERE interest_id = ?",
            (interest[0],)
        )

        for row in cursor.fetchall():
            event_id = row[0]
            if event_id in seen_ids:
                continue

            cursor.execute(
                "SELECT name FROM events WHERE event_id = ?",
                (event_id,)
            )
            result = cursor.fetchone()
            if result:
                seen_ids.add(event_id)
                events.append([event_id, result[0]])

    return events

# Função que retorna uma lista de eventos por interesse.
def check_events_by_interest(selected_interest: str):
    """
    Essa função retorna uma lista de eventos com base em um interesse selecionado. Ela primeiro obtém o id do interesse,
    depois busca os eventos relacionados a esse interesse e retorna uma lista de tuplas (event_id, event_name).
    """
    events = []
    interest_id = index_interest(selected_interest)
    cursor.execute(
        "SELECT event_id FROM events_interests WHERE interest_id = ?",
        (interest_id,)
    )

    for row in cursor.fetchall():
        event_id = row[0]
        cursor.execute(
            "SELECT name FROM events WHERE event_id = ?",
            (event_id,)
        )
        result = cursor.fetchone()
        events.append([event_id, result[0]])

    return events

def check_event(event_id) -> tuple:
    """
    Essa função retorna os detalhes de um evento específico com base no id do evento. 
    Ela retorna uma tupla contendo todas as informações do evento, incluindo o nome, descrição, local, data, hora e id do criador.
    """
    cursor.execute(
        "SELECT * FROM events WHERE event_id = ?",
        (event_id,)
    )
    
    event = cursor.fetchone()

    return event