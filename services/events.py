import sqlite3
from services.interests import check_interests, index_interest
from services.validations import valid_name_events, valid_date, valid_hour

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Criando tabela eventos caso não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY AUTOINCREMENT, name NOT NULL, event_location NOT NULL, "
    "date NOT NULL, hour NOT NULL, creator_id INTEGER, FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE)"
    )

# Criando tabela de áreas de interesse dos eventos caso ela não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS events_interests(event_id INTEGER, interest_id INTEGER, PRIMARY KEY(event_id, interest_id), " \
    "FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE, FOREIGN KEY (interest_id) REFERENCES interests(interest_id) " \
    "ON DELETE CASCADE)"
    )

# Função que cria um evento e insere na tabela "events" do banco.
def create_event(name: str, event_location: str, date: str, hour: str, creator_id: int, *interests: list):
    name = name.strip()
    event_location = event_location.strip()
    date = date.strip()
    hour = hour.strip()
    if not valid_name_events(name):
        return False, "O nome precisa ter pelo menos 2 caracteres."
    if not valid_date(date):
        return False, "O formato da data está errado. Por favor, siga o padrão dd-mm-aaaa."
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
        "INSERT INTO events VALUES(?, ?, ?, ?, ?, ?)",
        (None, name, event_location, date, hour, creator_id)
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

# Função que retorna eventos com base nos interesses do usuário.
def check_events_with_interests(user_id: int):
    interests = check_interests(user_id)
    events = []
    seen_ids = set()  # controla duplicatas de forma mais simples

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