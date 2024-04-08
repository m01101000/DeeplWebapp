from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'dABSADFV64F4DY3V1<SDFSDA36V14SD<6FXCGDdybgsdvs<cfsaVSFGBH+6SF5B6S1DV'

# Define the upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS










# Funktion zum Überprüfen der Anmeldeinformationen
def authenticate(username, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session and 'password' in session:
        username = session['username']
        password = session['password']
        user = authenticate(username, password)
        if user:
            return render_template('dashboard.html', username=username)
    return redirect(url_for('login'))

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
            if request.method == 'POST':
                # Überprüfen, ob die POST-Anfrage ein Dateiobjekt enthält
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                # Überprüfen, ob eine Datei hochgeladen wurde
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    # Sicheres Speichern der Datei
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('File successfully uploaded')
                    return redirect(url_for('ea1'))
                else:
                    flash('Invalid file extension')
                    return redirect(request.url)
            return render_template('EA1.html')
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

if __name__ == '__main__':
    app.run(port=2000, debug=True)
