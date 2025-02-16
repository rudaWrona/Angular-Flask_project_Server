from flask import redirect, render_template, request, session, jsonify
from functools import wraps

#login function from cs50 finance, secures the view from unregistered user
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f) #keeps the attributes of the original function
    #this function will be called in place of the original function, when verified returns the original function it is decorating
    def decorated_function(*args, **kwargs):
        if session.get("uzytkownik") is None:
            return jsonify({'error': 'Unauthorized', 'komunikat': 'Musisz sie zalogowac.'}), 401
        return f(*args, **kwargs)

    return decorated_function