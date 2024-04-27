import sqlite3

SAVE_confidence = '0.55'
SAVE_label = 'kite'
evaluation = 'incorrect'
usernme_imagepath = 'static/images/taube.jpg'

# Verbindung zur Datenbank herstellen
connection = sqlite3.connect('ea1_exampleimages.db')
cursor = connection.cursor()

# Daten einfügen
#cursor.execute("INSERT INTO imagedata (SAVE_confidence, SAVE_label, evaluation, usernme_imagepath) VALUES (?, ?, ?, ?)", (SAVE_confidence, SAVE_label, evaluation, usernme_imagepath))

# Daten abrufen
cursor.execute('SELECT * FROM imagedata')
data = cursor.fetchall()
print(data)

# Änderungen speichern
connection.commit()

# Verbindung schließen
cursor.close()
connection.close()
