from flask import Flask, request, jsonify, session, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from cs50 import SQL
from flask_cors import CORS #pozwala na komunikację między apką Ionic i serwerem we flasku, które są na różnych domenach
import os
import time
import secrets
from flask_mailman import Mail, EmailMessage
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

# Konfiguracja email
app.config['MAIL_SERVER'] = 'mail.vanilladice.pl'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'szmuk@vanilladice.pl'
app.config['MAIL_PASSWORD'] = 'parNmqT2f&O4'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db = SQL("sqlite:///baza_danych.db")

mail = Mail()
mail.init_app(app)

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
    # Wymuszenie załadowania sesji, nawet dla multipart/form-data. Miało to pomóc przy przesyłaniu avatara, ale nie podziałało.
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

        uzytkownik = db.execute("SELECT * FROM uzytkownicy WHERE nazwa = ?", nazwa)
        print(uzytkownik)

        if uzytkownik:
            return jsonify({'blad': 'Nazwa użytkownika jest już zajęta'}), 401

        try:
            db.execute("INSERT INTO uzytkownicy (nazwa, haslo, email, avatarPath) VALUES (?, ?, ?, ?)", nazwa, haslo_hash, email, "pliki/avatary/avatar.png")
            return jsonify({'komunikat': 'Rejestracja zakończona sukcesem'}), 200
        # cs50.SQL.execute będzie traktował duplikat emaila jako ValueError ze zwględu na UNIQUE INDEX w tabeli
        except ValueError:
            return jsonify({'blad': 'email już przypisany do innego konta'}), 401

            
@app.route("/logowanie", methods=['GET', 'POST'])
def logowanie():

    session.clear()

    if request.method == 'POST':

        data = request.json

        nazwa = data.get('nazwa')
        haslo = data.get('haslo')

        check = db.execute("SELECT * FROM uzytkownicy WHERE nazwa = ?", nazwa)

        if len(check) != 1 or not check_password_hash(check[0]["haslo"], haslo):
            return jsonify({'blad': 'Niepoprawne dane logowania'}), 401

        session['uzytkownik'] = nazwa
        session['uzytkownik_id'] = db.execute("SELECT id FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['id']
        session['uzytkownik_email'] = db.execute("SELECT email FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['email']
        session['avatar'] = "https://www.vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['avatarPath']
        #session['avatar'] = "C:/Users/przem/Desktop/Aplikacje/STUDIA/Aplikacja zaliczeniowa/Angular-Flask-Logging/vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", nazwa)[0]['avatarPath']
        response = make_response({'komunikat': "Zalogowaleś się jako " + session['uzytkownik']})
        return response

     
@app.route('/sesja-status', methods=['GET'])
def sesja_status():

    if 'uzytkownik' in session:

        session['avatar'] = "https://www.vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['avatarPath']
        session['uzytkownik_email'] = db.execute("SELECT email FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['email']
        #session['avatar'] = "C:/Users/przem/Desktop/Aplikacje/STUDIA/Aplikacja zaliczeniowa/Angular-Flask-Logging/vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['avatarPath']

        # Flask automatycznie dopasowuje 'session' do ciasteczka w żądaniu
        return jsonify({
            'zalogowany': True,
            'uzytkownik_id': session['uzytkownik_id'],
            'uzytkownik': session['uzytkownik'],
            'avatar' : session['avatar'],
            'email' : session['uzytkownik_email']
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
            return jsonify({'blad': 'Błąd serwera'}), 500
        

@app.route('/dodaj-avatar', methods=['POST', 'GET'])
def upload_avatar():

    if request.method == 'POST':
        try:

            # Sprawdza czy plik został przesłany
            if 'avatar' not in request.files:
                return jsonify({'blad': 'Nie przesłano pliku'}), 400
            
            file = request.files['avatar']

            
            # Sprawdza czy plik został wybrany
            if file.filename == '':
                return jsonify({'blad': 'Nie wybrano pliku'}), 400

            # Sprawdza czy plik jest dozwolonego typu
            if not allowed_file(file.filename):
                return jsonify({'blad': 'Niedozwolony typ pliku'}), 400

            # Sprawdza rozmiar pliku
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Resetuje wskaźnik pliku
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'blad': 'Plik jest zbyt duży'}), 400

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
            
            return jsonify({'komunikat': 'Plik przesłany pomyślnie'})

        except Exception as e:
            return jsonify({'blad': str(e)}), 500
        

@app.route("/wyslij-kod", methods=["POST"])
def wyslij_kod():
        
    data = request.json
    email = data.get('email')

    uzytkownik = db.execute("SELECT * FROM uzytkownicy WHERE email = ?", email)

    if not uzytkownik:
        return jsonify({"blad": "Użytkownik z takim mailem nie istnieje"}), 404
    
    kod = ''.join(secrets.choice('0123456789') for _ in range(6))

    db.execute("INSERT INTO reset_hasel (uzytkownik_id, kod, uzyty) VALUES (?, ?, 0)", uzytkownik[0]["id"], kod)

    wiadomosc = EmailMessage(
    'Resetowanie hasła', #tytuł maila
    f"""
    Zawartość generowana automatycznie. Prosimy na nią nie odpowiadać.

    Twój kod do resetowania hasła to: 
    
    {kod}
    
    Wprowadź ten kod w aplikacji, aby ustawić nowe hasło.
        
    Jeśli nie prosiłeś o reset hasła, zignoruj tę wiadomość. 
    
    """,
    app.config['MAIL_USERNAME'], #od kogo
    [email] # do kogo
    )
    try:
        wiadomosc.send()
    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas wysyłania wiadomości z kodem: {e}'})
    
    return jsonify(({'komunikat': 'Wiadomość z kodem została wysłana na email'}))

@app.route("/zmiana-hasla", methods=["POST"])
def zmien_haslo():

    data = request.json
    email = data.get('email')
    noweHaslo = data.get('noweHaslo')
    kod = data.get('kodRes')

    print(email, noweHaslo, kod)

    uzytkownik = db.execute("SELECT * FROM uzytkownicy WHERE email = ?", email)

    if not uzytkownik:
        return jsonify({'blad': 'Użytkownik z takim mailem nie istnieje'}), 404

    reset_info = db.execute("SELECT * FROM reset_hasel WHERE uzytkownik_id = ? AND kod = ? AND uzyty = 0 ORDER BY czas DESC LIMIT 1", uzytkownik[0]["id"], kod)

    if not reset_info:
        return jsonify({'blad': 'Nieprawidłowy kod'}), 400

    haslo_hash = generate_password_hash(noweHaslo)

    db.execute("UPDATE uzytkownicy SET haslo = ? WHERE id = ?", haslo_hash, uzytkownik[0]["id"])

    db.execute("UPDATE reset_hasel SET uzyty = 1 WHERE id = ?", reset_info[0]["id"])

    return jsonify({'komunikat': 'Hasło zostało zmienione'})


@app.route("/zapisz-wydarzenie", methods=["POST"])
@login_required
def zapisz_wydarzenie():

    try:
        data = request.json
        nazwa = data.get('name')
        dzien = data.get('date')
        czas = data.get('time')
        miejsce = data.get('place')
        sloty = data.get('slots')
        organizator = data.get('owner')
        opis = data.get('details')

        dostepneGry = data.get('games')

        preferowanaGra = data.get('chosen_game')

        organizator_id = session['uzytkownik_id']

        db.execute("INSERT INTO wydarzenia (nazwa, dzien, czas, miejsce, sloty, organizator_id, opis) VALUES (?, ?, ?, ?, ?, ?, ?)", nazwa, dzien, czas, miejsce, sloty, organizator_id, opis)

        wydarzenie_id = db.execute("SELECT id FROM wydarzenia WHERE organizator_id = ? AND dzien = ? AND czas = ?", organizator_id, dzien, czas)[0]["id"]

        for gra in dostepneGry:
            db.execute("INSERT INTO ankiety (wydarzenie_id, gra) VALUES (?, ?)", wydarzenie_id, gra)
        
        db.execute("INSERT INTO zapisy (uzytkownik_id, wydarzenie_id, preferowana_gra) VALUES (?, ?, ?)", organizator_id, wydarzenie_id, preferowanaGra)

        db.execute("UPDATE ankiety SET punkty = punkty + 1 WHERE wydarzenie_id = ? AND gra = ?", wydarzenie_id, preferowanaGra)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas tworzenia wydarzenia: {e}'})

    return jsonify({'komunikat': 'Wydarzenie zostało pomyślnie utworzone'})


@app.route("/wydarzenia", methods=["GET"])
def wydarzenia():

    wydarzenia = db.execute("SELECT * FROM wydarzenia")

    wydarzeniaDoPrzeslania = {}

    for wydarzenie in wydarzenia:

        organizator = db.execute("SELECT nazwa FROM uzytkownicy WHERE id =?", wydarzenie['organizator_id'])[0]['nazwa']

        gry = db.execute("SELECT gra, punkty FROM ankiety WHERE wydarzenie_id = ?", wydarzenie['id'])
        
        gryDoPrzeslania = []
        for gra in gry:
            gryDoPrzeslania.append({"game" : gra['gra'], "votes" : gra['punkty']})


        gracze = db.execute("SELECT nazwa, avatarPath FROM uzytkownicy JOIN zapisy ON uzytkownicy.id=zapisy.uzytkownik_id WHERE wydarzenie_id = ?", wydarzenie['id'])
        graczeDoPrzeslania = []
        for gracz in gracze:
            #graczeDoPrzeslania.append(gracz['nazwa'])
            graczeDoPrzeslania.append({'player' : gracz['nazwa'], 'avatar' : "https://www.vanilladice.pl/" + gracz['avatarPath']})

        wydarzeniaDoPrzeslania[wydarzenie['id']] = {
            "date" : wydarzenie['dzien'],
            "time" : wydarzenie['czas'],
            "details" : wydarzenie['opis'],
            "name" : wydarzenie['nazwa'],
            "owner" : organizator,
            "place" : wydarzenie['miejsce'],
            "slots" : wydarzenie['sloty'],
            "games" : gryDoPrzeslania,
            "players" : graczeDoPrzeslania,

    }
        
    return jsonify(wydarzeniaDoPrzeslania)



@app.route("/zapisz-do-gry", methods=["POST"])
@login_required
def zapisz_do_gry():

    try:
        data = request.json
        wydarzenie_id = data.get('eventId')
        preferowanaGra = data.get('selectedGame')
        gracz = data.get('player')
        gracz_id = session['uzytkownik_id']

        db.execute("INSERT INTO zapisy (uzytkownik_id, wydarzenie_id, preferowana_gra) VALUES (?, ?, ?)", gracz_id, wydarzenie_id, preferowanaGra)

        db.execute("UPDATE ankiety SET punkty = punkty + 1 WHERE wydarzenie_id = ? AND gra = ?", wydarzenie_id, preferowanaGra)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas zapisywania na wydarzenie: {e}'})

    return jsonify({'komunikat' : 'Użytkownik pomyślnie zapisany na wydarzenie'})


@app.route("/usun-mnie-z-gry", methods=["POST"])
@login_required
def usun_mnie_z_gry():

    try:
        data = request.json
        wydarzenie_id = data.get('eventId')
        gracz_id = session['uzytkownik_id']
        preferowanaGra = db.execute("SELECT preferowana_gra FROM zapisy WHERE uzytkownik_id = ? AND wydarzenie_id = ?", gracz_id, wydarzenie_id)[0]['preferowana_gra']

        print(wydarzenie_id, gracz_id)

        db.execute("DELETE FROM zapisy WHERE wydarzenie_id = ? AND uzytkownik_id = ?", wydarzenie_id, gracz_id)

        db.execute("UPDATE ankiety SET punkty = punkty - 1 WHERE wydarzenie_id = ? AND gra = ?", wydarzenie_id, preferowanaGra)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas wypisywania z wydarzenie: {e}'})

    return jsonify({'komunikat' : 'Użytkownik pomyślnie wypisany z wydarzenia'})


@app.route("/usun-wydarzenie", methods=["POST"])
@login_required
def usun_wydarzenie():

    try:
        data = request.json
        wydarzenie_id = data.get('eventId')
        gracz_id = session['uzytkownik_id']

        wydarzenieDoUsuniecia = db.execute("SELECT * FROM wydarzenia WHERE id = ?", wydarzenie_id)

        #Sprawdza, czy zalogowany uzytkownik to organizator wydarzenia
        if gracz_id == wydarzenieDoUsuniecia[0]['organizator_id']:
            db.execute("DELETE FROM ankiety WHERE wydarzenie_id = ?", wydarzenie_id)
            db.execute("DELETE FROM zapisy WHERE wydarzenie_id = ?", wydarzenie_id)
            db.execute("DELETE FROM wydarzenia WHERE id = ?", wydarzenie_id)
        else:
            return jsonify({'blad' : 'Nie jesteś organizatorem tego wydarzenia.'})

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas usuwania wydarzenia: {e}'})

    return jsonify({'komunikat' : 'Wydarzenie zostało pomyślnie usunięte'})


@app.route("/modyfikuj-wydarzenie", methods=["POST", "PUT"])
@login_required
def modyfikuj_wydarzenie():

    #print("Otrzymane dane JSON:", request.get_json())

    try:
        data = request.json
        wydarzenie_id = data.get('id')
        nazwa = data.get('name')
        dzien = data.get('date')
        czas = data.get('time')
        miejsce = data.get('place')
        sloty = data.get('slots')
        opis = data.get('details')

        if nazwa:
            db.execute("UPDATE wydarzenia SET nazwa = ? WHERE id = ?", nazwa, wydarzenie_id)
        if dzien:
            db.execute("UPDATE wydarzenia SET dzien = ? WHERE id = ?", dzien, wydarzenie_id)
        if czas:
            db.execute("UPDATE wydarzenia SET czas = ? WHERE id = ?", czas, wydarzenie_id)
        if miejsce:
            db.execute("UPDATE wydarzenia SET miejsce = ? WHERE id = ?", miejsce, wydarzenie_id)
        if sloty:
            db.execute("UPDATE wydarzenia SET sloty = ? WHERE id = ?", sloty, wydarzenie_id)
        if opis:
            db.execute("UPDATE wydarzenia SET opis = ? WHERE id = ?", opis, wydarzenie_id)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas modyfikacji wydarzenia: {e}'})
    
    return jsonify({'komunikat' : 'Wydarzenie zostało pomyślnie zmodyfikowane'})

if __name__ == '__main__':
    app.run(debug=True)