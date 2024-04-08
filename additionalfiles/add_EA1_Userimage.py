import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('ea1_Userimages.db')
cursor = connection.cursor()

# Daten einfügen
cursor.execute("INSERT INTO userimages (username, filename) VALUES (?, ?)", ("Test", "Test"))

# Daten abrufen
cursor.execute('SELECT * FROM userimages')
data = cursor.fetchall()
print(data)

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
