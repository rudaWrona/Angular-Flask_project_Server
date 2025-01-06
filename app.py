from flask import Flask, request, jsonify, session, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from flask_cors import CORS #pozwala na komunikację między apką Ionic i serwerem we flasku

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = True #session will  be concluded when conncetion terminates.
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Wymagane dla żądań cross-origin, Chrome się burzy, jak ciasteczko nie ma tych nagłówków.
app.config['SESSION_COOKIE_SECURE'] = True    # Wymaga HTTPS, ale w sumie moje testowanie nie jest HTTPS i jakoś działa.

Session(app)
CORS(app, supports_credentials=True)

db = SQL("sqlite:///baza_danych.db")

@app.route("/", methods=['GET', 'POST'])
def index():
     return "Serwer działa"


@app.route("/rejestracja", methods=['GET', 'POST'])
def rejestracja():

    if request.method == 'POST':
        data = request.json
        nazwa = data.get('nazwa')
        haslo = data.get('haslo')

        haslo_hash = generate_password_hash(haslo)

        try:
            db.execute("INSERT INTO uzytkownicy (nazwa, haslo) VALUES (?, ?)", nazwa, haslo_hash)
            komunikat = "Rejestracja zakończona sukcesem"
            return jsonify(komunikat), 200
        # cs50.SQL.execute will treat a duplicate username as an ValueError due to UNIQUE INDEX on username column
        except ValueError:
            komunikat = "Nazwa użytkownika niedostępna"
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
        response = make_response({'komunikat': "Zalogowaleś się jako " + session['uzytkownik']})
        return response

     
@app.route('/sesja-status', methods=['GET'])
def sesja_status():

    if 'uzytkownik' in session:
        # Flask automatycznie dopasowuje `session` do ciasteczka w żądaniu
        return jsonify({
            'zalogowany': True,
            'uzytkownik_id': session['uzytkownik_id'],
            'uzytkownik': session['uzytkownik']
        })
    return jsonify({'zalogowany': False})#, 401

    
@app.route('/wylogowanie', methods=['GET', 'POST'])
def wylogowanie():

    session.clear()
    response = make_response(jsonify({'komunikat': 'Wylogowanie zakończyło się sukcesem'}))
    response.set_cookie('session_id', '', expires=0)  # Usunięcie ciasteczka sesji
    return response


@app.route('/gry', methods=['GET', 'POST'])
def wyszukajGry():

    if request.method == 'POST':
    
        data = request.json
        tytul = data.get('tytul')


        gry = db.execute("SELECT * FROM gry WHERE name LIKE ?", ('%' + tytul + '%',))

        print(gry)

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
        
if __name__ == '__main__':
    app.run(debug=True)