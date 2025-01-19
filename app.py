from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from cs50 import SQL
from flask_cors import CORS #pozwala na komunikację między apką Ionic i serwerem we flasku, które są na różnych domenach
import os
import time

from dekoratory import login_required

app = Flask(__name__)

#app.config['APPLICATION_ROOT'] = '/bg-test'
app.config["SESSION_PERMANENT"] = True #Sesja nie będzie wyłączana po zamknięcu przeglądarki
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Wymagane dla żądań cross-origin, Chrome się burzy, jak ciasteczko nie ma tych nagłówków.
app.config['SESSION_COOKIE_SECURE'] = True    # Wymaga HTTPS, ale w sumie moje testowanie nie jest HTTPS i jakoś działa.

Session(app)
CORS(app, supports_credentials=True)

db = SQL("sqlite:///baza_danych.db")

# Konfiguracja pod awatara
UPLOAD_FOLDER = '../vanilladice.pl/pliki/avatary'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit

#Sprawdza czy rozszerzenie pliku jest dozwolone
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def ensure_session():
    # Wymuszenie załadowania sesji, nawet dla multipart/form-data
    session.modified = True


#Odpowiedzi nie są cashowane i zawsze przesyłane są świeże dane
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
def index():
     return "Serwer działa"


@app.route("/rejestracja", methods=['GET', 'POST'])
def rejestracja():

    if request.method == 'POST':


        data = request.json        
        nazwa = data.get('nazwa')
        haslo = data.get('haslo')
        email = data.get('email')

        haslo_hash = generate_password_hash(haslo)
        email_hash = generate_password_hash(email)

        try:
            db.execute("INSERT INTO uzytkownicy (nazwa, haslo, email, avatarPath) VALUES (?, ?, ?, ?)", nazwa, haslo_hash, email_hash, "pliki/avatary/avatar.png")
            komunikat = "Rejestracja zakończona sukcesem"
            return jsonify(komunikat), 200
        # cs50.SQL.execute będzie traktował duplikat nazwy jako ValueError ze zwględu na UNIQUE INDEX w tabeli
        except ValueError:
            komunikat = "Nazwa użytkownika bądź emial niedostępne"
            return jsonify(komunikat=komunikat), 401

            
@app.route("/logowanie", methods=['GET', 'POST'])
def logowanie():

    session.clear()

    if request.method == 'POST':

        data = request.json

        nazwa = data.get('nazwa')
        haslo = data.get('haslo')

        check = db.execute("SELECT * FROM uzytkownicy WHERE nazwa = ?", nazwa)

        if len(check) != 1 or not check_password_hash(check[0]["haslo"], haslo):
            return jsonify({'komunikat': 'Niepoprawne dane logowania'}), 401

        session['uzytkownik'] = nazwa
        session['uzytkownik_id'] = db.execute("SELECT id FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['id']
        #session['avatar'] = "https://www.vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['avatarPath']
        session['avatar'] = "C:/Users/przem/Desktop/Aplikacje/STUDIA/Aplikacja zaliczeniowa/Angular-Flask-Logging/vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['avatarPath']
        response = make_response({'komunikat': "Zalogowaleś się jako " + session['uzytkownik']})
        return response

     
@app.route('/sesja-status', methods=['GET'])
def sesja_status():

    if 'uzytkownik' in session:

        #session['avatar'] = "https://www.vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['avatarPath']
        session['avatar'] = "C:/Users/przem/Desktop/Aplikacje/STUDIA/Aplikacja zaliczeniowa/Angular-Flask-Logging/vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['avatarPath']

        # Flask automatycznie dopasowuje 'session' do ciasteczka w żądaniu
        return jsonify({
            'zalogowany': True,
            'uzytkownik_id': session['uzytkownik_id'],
            'uzytkownik': session['uzytkownik'],
            'avatar' : session['avatar']
        })
    return jsonify({'zalogowany': False})#, 401

    
@app.route('/wylogowanie', methods=['GET', 'POST'])
def wylogowanie():

    session.clear()
    response = make_response(jsonify({'komunikat': 'Wylogowanie zakończyło się sukcesem'}))
    response.set_cookie('session_id', '', expires=0)  # Usunięcie ciasteczka sesji
    return response


@app.route('/gry', methods=['GET', 'POST'])
@login_required
def wyszukajGry():

    if request.method == 'POST':
    
        data = request.json
        tytul = data.get('tytul')

        gry = db.execute("SELECT * FROM gry WHERE name LIKE ?", ('%' + tytul + '%',))

        return jsonify(gry)

    else:
        try:

            tytul = request.args.get('q', '')

            if not tytul:
                return jsonify([])
            
            gry = db.execute("SELECT * FROM gry WHERE name LIKE ?", ('%' + tytul + '%',))

            return jsonify(gry)
        
        except Exception as e:
            
            print(f"Error during search: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        

@app.route('/dodaj-avatar', methods=['POST', 'GET'])
def upload_avatar():

    if request.method == 'POST':
        try:

            # Sprawdza czy plik został przesłany
            if 'avatar' not in request.files:
                return jsonify({'error': 'Nie przesłano pliku'}), 400
            
            file = request.files['avatar']

            
            # Sprawdza czy plik został wybrany
            if file.filename == '':
                return jsonify({'error': 'Nie wybrano pliku'}), 400

            # Sprawdza czy plik jest dozwolonego typu
            if not allowed_file(file.filename):
                return jsonify({'error': 'Niedozwolony typ pliku'}), 400

            # Sprawdza rozmiar pliku
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Resetuje wskaźnik pliku
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': 'Plik jest zbyt duży'}), 400

            # Zabezpiecza nazwę pliku
            filename = secure_filename(file.filename)
            # Dodaje timestamp do nazwy pliku aby uniknąć konfliktów
            unique_filename = f"{int(time.time())}_{filename}"
            # Tworzy pełną ścieżkę do pliku
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

            
            # Zapisujemy plik
            file.save(filepath)
            
            # URL do pliku (do użycia w aplikacji frontendowej i zapisanie do tabeli)
            file_url = f"pliki/avatary/{unique_filename}"

            user_id = request.form.get("uzytkownik_id")

            user = db.execute("SELECT * FROM uzytkownicy WHERE id = ?", user_id)
            
            if user:
                # Usuń stary plik jeśli istnieje
                old_avatar = db.execute("SELECT avatarPath FROM uzytkownicy WHERE id = ?", user_id)[0]['avatarPath']
                if old_avatar and old_avatar != "pliki/avatary/avatar.png":
                    old_filename = old_avatar.split('/')[-1]
                    old_filepath = os.path.join(UPLOAD_FOLDER, old_filename)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                     
            db.execute("UPDATE uzytkownicy SET avatarPath = ? WHERE id = ?", file_url, user_id)
            
            return jsonify({
                'message': 'Plik przesłany pomyślnie',
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)