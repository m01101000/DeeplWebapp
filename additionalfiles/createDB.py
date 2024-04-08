import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('user.db')
cursor = connection.cursor()

# Tabellen erstellen, wenn sie nicht existieren
cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
