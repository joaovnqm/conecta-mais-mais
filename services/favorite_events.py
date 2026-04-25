import sqlite3
from services.events import check_event

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Criando a tabela de eventos favoritados caso não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS favorite_events (" \
    "user_id INTEGER NOT NULL, " \
    "event_id INTEGER NOT NULL, " \
    "PRIMARY KEY(user_id, event_id), " \
    "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, " \
    "FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE)"
    )

def favorite_event(user_id, event_id):
    """
    Função que adiciona um evento à lista de favoritos do usuário. Ela verifica se o evento já foi favoritado e, se não, 
    adiciona o evento à lista de favoritos.
    """
    if check_favorite_event(user_id, event_id):
        return False, "Você já favoritou esse evento."
    
    cursor.execute(
        "INSERT INTO favorite_events VALUES (?, ?)",
        (user_id, event_id,)
    )

    connection.commit()
    return True, "Evento favoritado com sucesso."

def remove_from_favorite_event(user_id, event_id):
    """
    Função que remove um evento da lista de favoritos do usuário. Ela verifica se o evento já foi desfavoritado e, se não,
    remove o evento da lista de favoritos.
    """
    if check_favorite_event(user_id, event_id) == False:
        return False, "Você já desfavoritou esse evento."
    
    cursor.execute(
        "DELETE FROM favorite_events WHERE user_id = ? AND event_id = ?",
        (user_id, event_id,)
    )

    connection.commit()
    return True, "Evento desfavoritado com sucesso."

def check_favorite_event(user_id, event_id) -> bool:
    """
    Função que verifica se um evento já foi favoritado pelo usuário. Ela retorna True se o evento estiver na lista de favoritos do usuário,
    e False caso contrário.
    """
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM favorite_events WHERE user_id = ? AND event_id = ?)",
        (user_id, event_id,)
    )

    return bool(cursor.fetchone()[0])

def check_favorited_events(user_id):
    """
    Essa função retorna uma lista de eventos que foram favoritados por um usuário específico. 
    Ela consulta a tabela de eventos favoritados para obter os ids dos eventos,
    depois usa a função check_event para obter os detalhes de cada evento e retorna uma lista de tuplas 
    contendo as informações dos eventos favoritados.
    """
    events_list = []
    cursor.execute(
        "SELECT event_id FROM favorite_events WHERE user_id = ?",
        (user_id,)
    )

    events = cursor.fetchall()
    for event in events:
        event = check_event(event[0])
        events_list.append(event)

    return events_list