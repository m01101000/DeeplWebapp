from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'abcdefg'

# Verzeichnis für hochgeladene Bilder festlegen
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funktion zum Überprüfen der Anmeldeinformationen
def authenticate(username, password):
    conn = sqlite3.connect('user.db')
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
    return render_template('login.html', error=error)

##############################################################

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('user_file_name', None)
    return redirect(url_for('login'))

##############################################################

analyzedimages = '7'
averageconfidence = '0.19'

@app.route('/dashboard')
def dashboard():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            return render_template('dashboard.html', username=username, analyzedimages=analyzedimages, averageconfidence=averageconfidence)
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
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
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
            return render_template('EA1.html', username=username, user_file_name=user_file_name, path=path)
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

##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
##############################################################
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

if __name__ == '__main__':
    app.run(port=2000, debug=True)
