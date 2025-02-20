from flask import request, jsonify
from werkzeug.security import generate_password_hash
from cs50 import SQL
import secrets
from flask_mailman import EmailMessage


db = SQL("sqlite:///baza_danych.db")

def wyslij_kod():

    from app import app #import w tym miejscu, żeby uniknąć cyrkulicznego importu, kiedy różne moduły próbują zaimportować się nawzajem i nie są jeszcze w pełni zainicjowane, np. app. nie jest w pełni skonfigurowane.
        
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

def zmien_haslo():

    data = request.json
    email = data.get('email')
    noweHaslo = data.get('noweHaslo')
    kod = data.get('kodRes')

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