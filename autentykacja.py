from flask import request, jsonify, session, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

db = SQL("sqlite:///baza_danych.db")

def rejestracja():

    if request.method == 'POST':

        data = request.json        
        nazwa = data.get('nazwa')
        haslo = data.get('haslo')
        email = data.get('email')

        haslo_hash = generate_password_hash(haslo)

        uzytkownik = db.execute("SELECT * FROM uzytkownicy WHERE nazwa = ?", nazwa)

        if uzytkownik:
            return jsonify({'blad': 'Nazwa użytkownika jest już zajęta'}), 401

        try:
            db.execute("INSERT INTO uzytkownicy (nazwa, haslo, email, avatarPath) VALUES (?, ?, ?, ?)", nazwa, haslo_hash, email, "pliki/avatary/avatar.png")
            return jsonify({'komunikat': 'Rejestracja zakończona sukcesem'}), 200
        # cs50.SQL.execute będzie traktował duplikat emaila jako ValueError ze zwględu na UNIQUE INDEX w tabeli
        except ValueError:
            return jsonify({'blad': 'email już przypisany do innego konta'}), 401

            
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

        response = make_response({'komunikat': "Zalogowaleś się jako " + session['uzytkownik']})
        return response


def sesja_status():

    if 'uzytkownik' in session:

        session['avatar'] = "https://www.vanilladice.pl/" + db.execute("SELECT avatarPath FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['avatarPath']
        session['uzytkownik_email'] = db.execute("SELECT email FROM uzytkownicy WHERE nazwa = ?", session['uzytkownik'])[0]['email']
        session['ulubione'] = []
        ulubione = db.execute("SELECT gra FROM ulubione WHERE uzytkownik_id = ?", session['uzytkownik_id'])
        for ulubiona in ulubione:
            session['ulubione'].append(ulubiona['gra'].title())

        # Flask automatycznie dopasowuje 'session' do ciasteczka w żądaniu
        return jsonify({
            'zalogowany': True,
            'uzytkownik_id': session['uzytkownik_id'],
            'uzytkownik': session['uzytkownik'],
            'avatar' : session['avatar'],
            'email' : session['uzytkownik_email'],
            'ulubione' : session['ulubione']
        })
    return jsonify({'zalogowany': False})


def wylogowanie():

    session.clear()
    response = make_response(jsonify({'komunikat': 'Wylogowanie zakończyło się sukcesem'}))
    response.set_cookie('session_id', '', expires=0)  # Usunięcie ciasteczka sesji
    return response