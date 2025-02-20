from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import time
from cs50 import SQL

db = SQL("sqlite:///baza_danych.db")

# Konfiguracja pod awatara
UPLOAD_FOLDER = '../vanilladice.pl/pliki/avatary'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit

#Sprawdza czy rozszerzenie pliku jest dozwolone
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

            
            # Zapisuje plik
            file.save(filepath)
            
            # URL do pliku (do użycia w aplikacji frontendowej i zapisania do tabeli)
            file_url = f"pliki/avatary/{unique_filename}"

            user_id = request.form.get("uzytkownik_id")

            user = db.execute("SELECT * FROM uzytkownicy WHERE id = ?", user_id)
            
            if user:
                # Usuwa stary plik jeśli istnieje
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