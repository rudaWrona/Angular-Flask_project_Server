from flask import request, jsonify, session
from cs50 import SQL
from datetime import date, datetime

db = SQL("sqlite:///baza_danych.db")

def zapisz_wydarzenie():

    try:
        data = request.json
        nazwa = data.get('name')
        dzien = data.get('date')
        czas = data.get('time')
        miejsce = data.get('place')
        sloty = data.get('slots')
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


def wydarzenia():

    wydarzenia = db.execute("SELECT * FROM wydarzenia")

    aktualne_wydarzenia = [
        wydarzenie for wydarzenie in wydarzenia 
        if datetime.strptime(wydarzenie['dzien'], "%d.%m.%Y").date() >= date.today()
    ]

    wydarzenia = aktualne_wydarzenia

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
    
    #Konwertuje na tablice, żeby zachować kolejność. JSON niestety nie gwarantuje, że elementy będą widoczne w przeglądarce w tej samej kolejności
    wydarzeniaDoPrzeslaniaPosortowane = dict(sorted(wydarzeniaDoPrzeslania.items(), key=lambda item: datetime.strptime(item[1]["date"], "%d.%m.%Y"), reverse=True))

    def konwertujNaTablice(objekt):
        resultat = []      
        for key, value in objekt.items():
            event = value.copy()
            event['id'] = key
            resultat.append(event)   
        return resultat

    wydarzeniaDoPrzeslaniaPosortowane = konwertujNaTablice(wydarzeniaDoPrzeslaniaPosortowane)
    
    return jsonify(wydarzeniaDoPrzeslaniaPosortowane)


def zapisz_do_gry():

    try:
        data = request.json
        wydarzenie_id = data.get('eventId')
        preferowanaGra = data.get('selectedGame')
        gracz_id = session['uzytkownik_id']

        db.execute("INSERT INTO zapisy (uzytkownik_id, wydarzenie_id, preferowana_gra) VALUES (?, ?, ?)", gracz_id, wydarzenie_id, preferowanaGra)

        db.execute("UPDATE ankiety SET punkty = punkty + 1 WHERE wydarzenie_id = ? AND gra = ?", wydarzenie_id, preferowanaGra)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas zapisywania na wydarzenie: {e}'})

    return jsonify({'komunikat' : 'Użytkownik pomyślnie zapisany na wydarzenie'})


def usun_mnie_z_gry():

    try:
        data = request.json
        wydarzenie_id = data.get('eventId')
        gracz_id = session['uzytkownik_id']
        preferowanaGra = db.execute("SELECT preferowana_gra FROM zapisy WHERE uzytkownik_id = ? AND wydarzenie_id = ?", gracz_id, wydarzenie_id)[0]['preferowana_gra']

        db.execute("DELETE FROM zapisy WHERE wydarzenie_id = ? AND uzytkownik_id = ?", wydarzenie_id, gracz_id)

        db.execute("UPDATE ankiety SET punkty = punkty - 1 WHERE wydarzenie_id = ? AND gra = ?", wydarzenie_id, preferowanaGra)

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas wypisywania z wydarzenie: {e}'})

    return jsonify({'komunikat' : 'Użytkownik pomyślnie wypisany z wydarzenia'})


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
            return jsonify({'blad' : 'Nie jesteś organizatorem tego wydarzenia.'}), 401

    except Exception as e:
        return jsonify({'blad' : f'Błąd podczas usuwania wydarzenia: {e}'})

    return jsonify({'komunikat' : 'Wydarzenie zostało pomyślnie usunięte'})


def modyfikuj_wydarzenie():

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