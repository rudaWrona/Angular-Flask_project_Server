from flask import request, jsonify
from cs50 import SQL

db = SQL("sqlite:///baza_danych.db")

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
            return jsonify({'blad': 'Błąd serwera'}), 500