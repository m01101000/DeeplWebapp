import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('ea1_Userimages.db')
cursor = connection.cursor()

# Tabellen erstellen, wenn sie nicht existieren
cursor.execute('''
        CREATE TABLE IF NOT EXISTS userimages (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            filename TEXT NOT NULL
        )
    ''')

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
