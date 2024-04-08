import sqlite3

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('user.db')
cursor = connection.cursor()

# Daten einfügen
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("Test", "Test"))

# Daten abrufen
cursor.execute('SELECT * FROM users')
data = cursor.fetchall()
print(data)

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
