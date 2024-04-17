import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('ea1_exampleimages.db')
cursor = connection.cursor()

# Tabellen erstellen, wenn sie nicht existieren
cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagedata (
                        id INTEGER PRIMARY KEY,
                        SAVE_confidence REAL,
                        SAVE_label TEXT NOT NULL,
                        evaluation TEXT NOT NULL,
                        usernme_imagepath TEXT NOT NULL
                    )
    ''')

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
