from flask import request, jsonify, session
from cs50 import SQL

db = SQL("sqlite:///baza_danych.db")

def dodaj_do_ulubionych():

    data = request.json        
    ulubiona = data.get('ulubiona').lower()
    uzytkownik_id = session['uzytkownik_id']

    ulubioneCheck = []
    ulubione = db.execute("SELECT gra FROM ulubione WHERE uzytkownik_id = ?", uzytkownik_id)
    for gra in ulubione:
        ulubioneCheck.append(gra['gra'])

    if ulubiona in ulubioneCheck:
        return jsonify({'blad' : f'Tę grę już posiadasz w ulubionych'}), 400

    try:
        db.execute("INSERT INTO ulubione (uzytkownik_id, gra) VALUES (?, ?)", uzytkownik_id, ulubiona)
    
    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas dodawania gry do ulubionych: {e}'}), 400
    
    return jsonify({'komunikat' : 'Gra została pomyślnie dodana do ulubionych'}), 200


def usun_z_ulubionych():

    data = request.json        
    ulubiona = data.get('ulubionaDoUsuniecia').lower()
    uzytkownik_id = session['uzytkownik_id']

    try:
        db.execute("DELETE FROM ulubione WHERE uzytkownik_id = ? AND gra = ?", uzytkownik_id, ulubiona)
    
    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas usuwania gry z ulubionych: {e}'}), 400
    
    return jsonify({'komunikat' : 'Gra została pomyślnieusunięta z ulubionych'}), 200