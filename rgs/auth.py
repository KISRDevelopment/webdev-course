import flask_login
import db
import functools
from passlib.hash import pbkdf2_sha256
from flask import abort

# just an alias ...
login_required = flask_login.login_required

# This class represents the currently logged in user
class User(flask_login.UserMixin):
    pass

def init(app, login_view):
    login_manager = flask_login.LoginManager()
    login_manager.login_view = login_view
    login_manager.user_loader(user_loader)
    login_manager.init_app(app)

def current_user():
    return flask_login.current_user

def user_loader(username):
    """ given a user name, return a User object representing
    the logged in user, or None if no such username exists. """
    user_row = db.get_user(username)
    
    if not user_row:
        return None

    user = User()
    user.id = username
    user.role = user_row['user_role']

    return user

def requires_role(role):
    """ requires that a user have a specific role to access
    the view """
    def decorator(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                abort(401)
            
            u = flask_login.current_user
            
            if  u.role != 'admin' and u.role != role:
                abort(401)
            return func(*args, **kwargs)
        return f
    return decorator

def authenticate(username, password):
    user_row = db.get_user(username)
    if user_row is None:
        return False
    return pbkdf2_sha256.verify(password, user_row['password_hash'])

def login_user(username):
    user = User()
    user.id = username
    flask_login.login_user(user)

def logout_user():
    flask_login.logout_user()
