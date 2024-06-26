from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify, send_file, make_response
import os
from werkzeug.utils import secure_filename
import sqlite3
import shutil
import plotly.graph_objs as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = 'abcdefgLUL'

# Verzeichnis für hochgeladene Bilder festlegen
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funktion zum Überprüfen der Anmeldeinformationen
def authenticate(username, password):
    conn = sqlite3.connect('static/sysdata/user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

##############################################################

@app.route('/', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password
        user = authenticate(username, password)
        if user:
            # Authentifizierung erfolgreich
            return redirect(url_for('dashboard'))
        else:
            # Authentifizierung fehlgeschlagen
            error = True
    return render_template('login.html',
                           error=error)

##############################################################

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('user_file_name', None)
    session.pop('EA1_temp_file_path', None)
    return redirect(url_for('login'))

##############################################################

analyzedimages = 0
averageconfidence = 0

@app.route('/dashboard')
def dashboard():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            analyzedimages = 0
            averageconfidence = 0
            db_path = 'static/userfiles/EA1/' + username + '/imagedata/' + (username + '_imagedata.db')

            if os.path.exists(db_path):
                # Verbindung zur Datenbank herstellen
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                # Daten abrufen
                cursor.execute('SELECT * FROM imagedata')
                data = cursor.fetchall()
                
                #Anzahl der Bilder
                analyzedimages = len(data)

                # Initialize sum of second elements
                sum_second_elements = 0

                # Iterate through the tuples and sum up the second elements
                for tup in data:
                    sum_second_elements += tup[1]  # Assuming the second element is always at index 1

                # Calculate the average
                averageconfidence = sum_second_elements / len(data)
                # Begrenzung auf zwei Nachkommastellen
                averageconfidence = round(averageconfidence, 2)

                # Änderungen speichern
                connection.commit()
                # Verbindung schließen
                cursor.close()
                # connection.close()
            else:
                print("No images saved.")

            return render_template('dashboard.html',
                                   username=username,
                                   analyzedimages=analyzedimages,
                                   averageconfidence=averageconfidence)

    return redirect(url_for('login'))

##############################################################

@app.route('/tutorials')
def tutorials():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            return render_template('tutorials.html')
    return redirect(url_for('login'))

@app.route('/tutorials/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/tutorials', filename)

##############################################################

@app.route('/EA1', methods=['GET', 'POST'])
def ea1():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            user_file_name = session.get('user_file_name')
            path = session.get('path')
            if 'user_file_name' not in session:
                user_file_name = ""
            if 'path' not in session:
                path = ""

            sysdata = 'static/sysdata/ea1_exampleimages.db'
            # Verbindung zur Datenbank herstellen
            connection = sqlite3.connect(sysdata)
            cursor = connection.cursor()

            # Daten abrufen
            cursor.execute('SELECT * FROM imagedata WHERE evaluation = "correct"')
            saved_correct = cursor.fetchall()

            # Daten abrufen
            cursor.execute('SELECT * FROM imagedata WHERE evaluation = "incorrect"')
            saved_incorrect = cursor.fetchall()

            # Änderungen speichern
            connection.commit()

            # Verbindung schließen
            cursor.close()
            connection.close()

            # Define the path to the database file
            db_path = 'static/userfiles/EA1/' + username + '/imagedata/' + (username + '_imagedata.db')
            saved_correct_Images = ''
            saved_incorrect_Images = ''

            # Check if the file exists
            if os.path.exists(db_path):
                # Verbindung zur Datenbank herstellen
                saved_correct_Images = ''
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                # Daten abrufen
                cursor.execute('SELECT * FROM imagedata WHERE evaluation = "correct"')
                saved_correct_Images = cursor.fetchall()
                # Daten abrufen
                cursor.execute('SELECT * FROM imagedata WHERE evaluation = "incorrect"')
                saved_incorrect_Images = cursor.fetchall()

                # Änderungen speichern
                connection.commit()
                # Verbindung schließen
                cursor.close()
                # connection.close()
            else:
                print("No images saved.")

            # Standardwert für den Balken (0.19 entspricht 19%)
            default_value = 0

            # to display results and documentation
            evaluator = "evaluator" if username == "Gers" else "placeholder"

            return render_template('EA1.html',
                                   evaluator=evaluator,
                                   saved_correct=saved_correct,
                                   saved_incorrect= saved_incorrect,
                                   defaultValue=default_value,
                                   username=username,
                                   user_file_name=user_file_name,
                                   path=path,
                                   saved_correct_Images=saved_correct_Images,
                                   saved_incorrect_Images=saved_incorrect_Images)

    return redirect(url_for('login'))

@app.route('/EA1upload', methods=['POST'])
def upload():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:

            # Check if 'image' is in request.files
            if 'image' not in request.files:
                session.pop('user_file_name', None)
                return redirect(url_for('ea1'))

            file = request.files['image']
            uploadBy = request.form['uploadBy']

            # Check if a file is selected
            if file.filename == '':
                session.pop('user_file_name', None)
                return redirect(url_for('ea1'))

            # Ensure the file has an allowed extension
            if file and allowed_file(file.filename):
                # Set the filename as username_file.ext
                filename = secure_filename(uploadBy + '_' + file.filename)
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], uploadBy)

                # Create the user's folder if it doesn't exist
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)

                file_path = os.path.join(user_folder, filename)

                # Check if a file with the same username prefix already exists, if so, remove it
                existing_files = [f for f in os.listdir(user_folder) if f.startswith(uploadBy + '_')]
                for existing_file in existing_files:
                    os.remove(os.path.join(user_folder, existing_file))

                # Save the file
                file.save(file_path)
                session['EA1_temp_file_path'] = file_path

                print(file_path)

                # Update session with the filename
                session['user_file_name'] = filename
                return redirect(url_for('ea1'))
            else:
                return 'fehler'

        return render_template('EA1.html')

def allowed_file(filename):
    # Prüfen, ob die Dateiendung zulässig ist
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/EA1storage', methods=['GET', 'POST'])
def ea1storage():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            SAVE_label = request.form['SAVE_label']
            SAVE_confidence = request.form['SAVE_confidence']
            evaluation = request.form['evaluation']
            EA1_temp_file_path = session['EA1_temp_file_path']

            # Check if the file exists
            if not os.path.exists(EA1_temp_file_path):
                return jsonify({'error': 'File does not exist'}), 404

            # Überprüfen, ob der Ordner mit dem Benutzernamen existiert
            user_directory = 'static/userfiles/EA1/' + username + '/'
            if not os.path.exists(user_directory):
                # Wenn der Ordner nicht existiert, erstelle ihn
                os.makedirs(user_directory)

            # Definieren des Zielverzeichnisses, in dem das Bild gespeichert werden soll
            destination_directory = user_directory

            # Copy the file to the destination directory
            shutil.copy(EA1_temp_file_path, destination_directory)

            # Lösche die Datei nach dem Kopieren
            os.remove(EA1_temp_file_path)

            # Überprüfen, ob der Ordner mit dem Benutzernamen existiert
            user_directory_imagedata = 'static/userfiles/EA1/' + username + '/imagedata/'
            if not os.path.exists(user_directory_imagedata):
                # Wenn der Ordner nicht existiert, erstelle ihn
                os.makedirs(user_directory_imagedata)

            # Verbindung zur Datenbank herstellen
            connection = sqlite3.connect('static/userfiles/EA1/' + username + '/imagedata/' + (username + '_imagedata.db'))
            cursor = connection.cursor()

            user_file_name = session['user_file_name']

            user_directory_imagedata12 = (user_directory_imagedata.replace('static/', ''))
            user_directory_imagedata1 = (user_directory_imagedata12.replace('/imagedata/', '/'))
            usernme_imagepath = (user_directory_imagedata1 + user_file_name)

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

            # Verbindung zur Datenbank herstellen
            connection = sqlite3.connect('static/userfiles/EA1/' + username + '/imagedata/' + (username + '_imagedata.db'))
            cursor = connection.cursor()
            # Daten einfügen
            cursor.execute("INSERT INTO imagedata (SAVE_confidence, SAVE_label, evaluation, usernme_imagepath) VALUES (?, ?, ?, ?)", (SAVE_confidence, SAVE_label, evaluation, usernme_imagepath))
            # Daten abrufen
            cursor.execute('SELECT * FROM imagedata')
            data = cursor.fetchall()
            print(data)
            # Änderungen speichern
            connection.commit()
            # Verbindung schließen
            cursor.close()
            connection.close()

            session.pop('user_file_name', None)
            session.pop('EA1_temp_file_path', None)

            return redirect(url_for('ea1'))
        else:
            return redirect(url_for('login'))
        
@app.route('/EA1discard', methods=['GET', 'POST'])
def ea1discard():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            session.pop('user_file_name', None)
            session.pop('EA1_temp_file_path', None)
            return redirect(url_for('ea1'))
        else:
            return redirect(url_for('login'))
        
@app.route('/EA1report', methods=['GET', 'POST'])
def ea1report():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            def create_pdf(file_name):
                doc = SimpleDocTemplate(file_name, pagesize=letter)
                styles = getSampleStyleSheet()

                # Inhalte für die PDF
                flowables = []

                # Füge Titel hinzu
                title = Paragraph(('Report EA1 - User: ' + username), styles['Title'])
                flowables.append(title)

                # Füge eine Spacer-Komponente ein
                spacer = Spacer(1, 20)
                flowables.append(spacer)

                # Define the path to the database
                reportdata = f"static/userfiles/EA1/{username}/imagedata/{username}_imagedata.db"
                
                # Check if the database exists
                # Check if the database exists
                if os.path.exists(reportdata):
                    # Verbindung zur Datenbank herstellen
                    connection = sqlite3.connect(reportdata)
                    cursor = connection.cursor()

                    # Füge eine Spacer-Komponente ein
                    spacer = Spacer(1, 20)
                    flowables.append(spacer)

                    # Füge Absatz nach dem Seitenumbruch hinzu
                    text = "YOUR CORRECT CLASSIFIED IMAGES"
                    paragraph = Paragraph(text, styles['Normal'])
                    flowables.append(paragraph)

                    spacer = Spacer(1, 20)
                    flowables.append(spacer)

                    # Daten abrufen
                    cursor.execute('SELECT * FROM imagedata WHERE evaluation = "correct"')
                    saved_correct = cursor.fetchall()

                    if saved_correct:
                        # Tabellenspaltennamen festlegen
                        column_names = ['image no.', 'confidence', 'label', 'status', 'image']

                        # Tabelle erstellen und Spaltennamen hinzufügen
                        table_data1 = [column_names]

                        for row1 in saved_correct:
                            table_row1 = []
                            for cell in row1:
                                if isinstance(cell, str) and (cell.endswith('.jpg') or cell.endswith('.png')):
                                    # Wenn die Zelle eine Bild-URL ist, füge das Bild ein
                                    img = Image("static/" + cell)
                                    img.drawHeight = 50  # Größe des Bildes anpassen
                                    img.drawWidth = 50
                                    table_row1.append(img)
                                else:
                                    table_row1.append(str(cell))
                            table_data1.append(table_row1)
                        table1 = Table(table_data1)

                        # Tabellenstil festlegen
                        table1.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Schwarze Linien zwischen den Zellen
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Hintergrundfarbe für Spaltenüberschriften
                        ]))
                        
                        flowables.append(table1)
                    else:
                        flowables.append(Paragraph("No correct images found.", styles['Normal']))

                    # Füge eine Spacer-Komponente ein
                    spacer = Spacer(1, 20)
                    flowables.append(spacer)

                    # Füge Absatz nach dem Seitenumbruch hinzu
                    text = "YOUR INCORRECT CLASSIFIED IMAGES"
                    paragraph = Paragraph(text, styles['Normal'])
                    flowables.append(paragraph)

                    spacer = Spacer(1, 20)
                    flowables.append(spacer)

                    # Daten abrufen
                    cursor.execute('SELECT * FROM imagedata WHERE evaluation = "incorrect"')
                    saved_incorrect = cursor.fetchall()

                    if saved_incorrect:
                        # Tabellenspaltennamen festlegen
                        column_names = ['image no.', 'confidence', 'label', 'status', 'image']

                        # Tabelle erstellen und Spaltennamen hinzufügen
                        table_data2 = [column_names]

                        for row2 in saved_incorrect:
                            table_row2 = []
                            for cell in row2:
                                if isinstance(cell, str) and (cell.endswith('.jpg') or cell.endswith('.png')):
                                    # Wenn die Zelle eine Bild-URL ist, füge das Bild ein
                                    img = Image("static/" + cell)
                                    img.drawHeight = 50  # Größe des Bildes anpassen
                                    img.drawWidth = 50
                                    table_row2.append(img)
                                else:
                                    table_row2.append(str(cell))
                            table_data2.append(table_row2)
                        table2 = Table(table_data2)

                        # Tabellenstil festlegen
                        table2.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Schwarze Linien zwischen den Zellen
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Hintergrundfarbe für Spaltenüberschriften
                        ]))

                        flowables.append(table2)
                    else:
                        flowables.append(Paragraph("No incorrect images found.", styles['Normal']))

                    # Änderungen speichern
                    connection.commit()
                    # Verbindung schließen
                    cursor.close()
                    connection.close()
                else:
                    # Füge Absatz nach dem Seitenumbruch hinzu
                    nodata = "You have not saved any uploaded images."
                    nodata_paragraph = Paragraph(nodata, styles['Normal'])
                    flowables.append(nodata_paragraph)

                # Erzeuge PDF
                doc.build(flowables)

            # Überprüfen, ob der Ordner mit dem Benutzernamen existiert
            path = 'static/userfiles/EA1/' + username
            if not os.path.exists(path):
                    # Wenn der Ordner nicht existiert, erstelle ihn
                os.makedirs(path)

            # Erstelle die PDF-Datei
            create_pdf(f"{path}/{username}_EA1_report.pdf")

            pdf_path = f"{path}/{username}_EA1_report.pdf"

            if os.path.exists(pdf_path):
                response = make_response(send_file(pdf_path, as_attachment=True))
                response.headers["Content-Disposition"] = f"attachment; filename={username}_EA1_report.pdf"
                response.headers["Content-Type"] = "application/pdf"
                return response
            else:
                return redirect(url_for('ea1'))
        else:
            return redirect(url_for('login'))

##############################################################

@app.route('/imprint')
def imprint():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            return render_template('imprint.html')
    return redirect(url_for('login'))

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(port=5000, debug=False, threaded=True)