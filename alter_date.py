import sqlite3
connection = sqlite3.connect("conecta++.db")
cursor = connection.cursor()
cursor.execute("UPDATE events SET date = '16-05-2026' WHERE event_id = 28")
connection.commit()