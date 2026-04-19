import sqlite3

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

# Criando função que favorita um evento e salva na lista de eventos favoritos.
def favorite_event(user_id, event_id):
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM favorite_events WHERE user_id = ? AND event_id = ?)",
        (user_id, event_id,)
    )

    result = bool(cursor.fetchone()[0])

    if result:
        return False, "Você já favoritou esse evento."
    
    cursor.execute(
        "INSERT INTO favorite_events VALUES (?, ?)",
        (user_id, event_id,)
    )

    connection.commit()
    return True, "Evento favoritado com sucesso."