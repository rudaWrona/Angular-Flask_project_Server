from flask import session, jsonify
from functools import wraps

#login function from cs50 finance, secures the view from unregistered user
def login_required(f):
    """
    Dekoruje ścieżki, wymagając zalogowania

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f) #przechowuje atrybuty oryginalnej funkcji
    #ta funkcja będzie wywołana zamiast oryginalnej funkcji. Po weryfikacji zwraca oryginalną funkcję, którą dekoruje
    def decorated_function(*args, **kwargs):
        if session.get("uzytkownik") is None:
            return jsonify({'error': 'Unauthorized', 'komunikat': 'Musisz sie zalogowac.'}), 401
        return f(*args, **kwargs)

    return decorated_function