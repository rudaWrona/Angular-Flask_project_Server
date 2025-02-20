from flask import Flask, session
from flask_session import Session
from cs50 import SQL
from flask_cors import CORS #pozwala na komunikację między apką Ionic i serwerem we flasku, które są na różnych domenach
from flask_mailman import Mail
from dekoratory import login_required
from autentykacja import logowanie, rejestracja, wylogowanie, sesja_status
from gry import wyszukajGry
from avatar import upload_avatar
from zmiana_hasla import wyslij_kod, zmien_haslo
from wydarzenia import wydarzenia, usun_mnie_z_gry, usun_wydarzenie, modyfikuj_wydarzenie, zapisz_wydarzenie, zapisz_do_gry
from ulubione import dodaj_do_ulubionych, usun_z_ulubionych

app = Flask(__name__)

# Konfiguracja email
app.config['MAIL_SERVER'] = 'mail.vanilladice.pl'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'szmuk@vanilladice.pl'
app.config['MAIL_PASSWORD'] = 'parNmqT2f&O4'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail()
mail.init_app(app)

#app.config['APPLICATION_ROOT'] = '/bg-test'
app.config["SESSION_PERMANENT"] = True #Sesja nie będzie wyłączana po zamknięcu przeglądarki
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super_secret_key' #żywany do podpisywania ciasteczek sesyjnych
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Wymagane dla żądań cross-origin, Chrome się burzy, jak ciasteczko nie ma tych nagłówków.
app.config['SESSION_COOKIE_SECURE'] = True    # Wymaga HTTPS, ale w sumie moje testowanie nie jest HTTPS i jakoś działa.

Session(app)
CORS(app, supports_credentials=True, origins=[
    "https://planszowki-62c41.web.app",  #frontend jest hostowany na serwerze
    "capacitor://localhost",   # Dla aplikacji na Android/iOS zbudowanej w Capacitor
    "http://localhost",        # Dla testów na emulatorze lub w przeglądarce
    "http://localhost:8100",    # Dla testów w aplikacji Ionic na komputerze (`ionic serve`)
    "ionic://localhost",        # Alternatywny scheme dla Ionic
    "app://localhost",          # Dla aplikacji natywnych
    "file://",                  # Dla aplikacji mobilnych (bardzo ważne!)
    "*"                         #Zostawiam to, bo żadna inna pozycja z listy nie daje dostępu aplikacji moblinej na Androidzie.
]) #Cross-Origin Resource Sharing. Przeglądarki stosują politykę Same-Origin Policy (SOP), która domyślnie blokuje takie żądania ze względów bezpieczeństwa. Potencjalnie może 

db = SQL("sqlite:///baza_danych.db")

@app.before_request
def ensure_session():
    # Wymuszenie załadowania sesji, nawet dla multipart/form-data. Miało to pomóc przy przesyłaniu avatara, ale nie podziałało.
    session.modified = True


#Odpowiedzi nie są cashowane i zawsze przesyłane są świeże dane
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
def index():
     return "Serwer działa"


@app.route("/rejestracja", methods=['GET', 'POST'])
def rejestracja_route():
    return rejestracja()

            
@app.route("/logowanie", methods=['GET', 'POST'])
def logowanie_route():
    return logowanie()

     
@app.route('/sesja-status', methods=['GET'])
def sesja_status_route():
    return sesja_status()

    
@app.route('/wylogowanie', methods=['GET', 'POST'])
def wylogowanie_route():
    return wylogowanie()


@app.route('/gry', methods=['GET', 'POST'])
@login_required
def wyszukajGry_route():
    return wyszukajGry()
        

@app.route('/dodaj-avatar', methods=['POST', 'GET'])
@login_required
def upload_avatar_route():
    return upload_avatar()


@app.route("/wyslij-kod", methods=["POST"])
def wyslij_kod_route():
    return wyslij_kod()


@app.route("/zmiana-hasla", methods=["POST"])
def zmien_haslo_route():
    return zmien_haslo()


@app.route("/zapisz-wydarzenie", methods=["POST"])
@login_required
def zapisz_wydarzenie_route():
    return zapisz_wydarzenie()


@app.route("/wydarzenia", methods=["GET"])
def wydarzenia_route():
    return wydarzenia()


@app.route("/zapisz-do-gry", methods=["POST"])
@login_required
def zapisz_do_gry_route():
    return zapisz_do_gry()


@app.route("/usun-mnie-z-gry", methods=["POST"])
@login_required
def usun_mnie_z_gry_route():
    return usun_mnie_z_gry()


@app.route("/usun-wydarzenie", methods=["POST"])
@login_required
def usun_wydarzenie_route():
    return usun_wydarzenie()


@app.route("/modyfikuj-wydarzenie", methods=["POST", "PUT"])
@login_required
def modyfikuj_wydarzenie_route():
    return modyfikuj_wydarzenie()


@app.route("/dodaj-do-ulubionych", methods=['POST'])
@login_required
def dodaj_do_ulubionych_route():
    return dodaj_do_ulubionych()

@app.route("/usun-z-ulubionych", methods=['POST'])
@login_required
def usun_z_ulubionych_route():
    return usun_z_ulubionych()


if __name__ == '__main__':
    app.run(debug=True)