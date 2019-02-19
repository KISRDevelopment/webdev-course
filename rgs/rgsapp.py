from flask import Flask, render_template, abort, request, redirect, url_for, flash, \
    send_from_directory, g
import json
import sqlite3
import re
from forms import PresentationForm, LoginForm
import random
import os
from werkzeug.utils import secure_filename
import string
import flask_login
from passlib.hash import pbkdf2_sha256
import functools

range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)

app = Flask(__name__)
app.config['db_path'] = 'db.sqlite'
app.secret_key = b'xYFRlEs3@a'
app.config['uploads_path'] = './uploads/'

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

render_template_old = render_template
def new_render_template(*args, **kwargs):
    kwargs['user'] = flask_login.current_user
    return render_template_old(*args,**kwargs)
render_template = new_render_template

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    db = connect_db()

    user_row = db.execute("select * from user u where u.username = ?", (username,)).fetchone()
    if user_row is None:
        return
    
    user = User()
    user.id = username
    user.role = user_row['user_role']

    return user


def requires_role(role):
    def decorator(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                abort(401)
            
            u = flask_login.current_user
            
            # if you are an admin, you have access to anything
            # otherwise, make sure your role is the same as the
            # required role
            if  u.role != 'admin' and u.role != role:
                abort(401)
            return func(*args, **kwargs)
        return f
    return decorator


@app.route('/')
@flask_login.login_required
def home():
    
    db = connect_db()
    
    presentations = db.execute("select * from presentation")
    
    output = render_template('home.html', presentations=presentations)

    return output
    
@app.route('/presentation/<int:pid>')
@flask_login.login_required
def details(pid):
    
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    attachments = db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,))
    
    presentation['attachments'] = list(attachments)
    
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET', 'POST'))
@flask_login.login_required
@requires_role('admin')
def create():
    form = PresentationForm()
    
    if form.validate_on_submit():
        
        # upload attachments
        attachments = []
        if 'attachments' in request.files:
           for f in request.files.getlist('attachments'):
               filename = generate_file_name(f.filename)
               f.save(os.path.join(app.config['uploads_path'], filename))
               attachments.append(filename)
        
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""insert into presentation(title, presenters, scheduled, time_range, notes)
            values(?, ?, ?, ?, ?)""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')])
        
        # need to know the newly inserted presentation id
        pid = cursor.lastrowid
        
        for a in attachments:
            cursor.execute("""insert into attachment(presentation_id, filename)
             values(?, ?)""", (pid, a))
        
        db.commit()
        
        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)
   
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
@flask_login.login_required
@requires_role('admin')
def edit(pid):
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    attachments = list(db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,)))
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
        # upload attachments
        attachments = []
        if 'attachments' in request.files:
           for f in request.files.getlist('attachments'):
               filename = generate_file_name(f.filename)
               f.save(os.path.join(app.config['uploads_path'], filename))
               attachments.append(filename)
        
        db.execute("""update presentation set title = ?, presenters = ?,
            scheduled = ?, time_range = ?, notes = ? where id=?""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')] + [pid])
            
        for a in attachments:
            db.execute("""insert into attachment(presentation_id, filename)
             values(?, ?)""", (pid, a))
        
        db.commit()
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    db.close()
    return render_template('edit.html', form=form, pid=pid, attachments=attachments)
    
@app.route('/delete/<int:pid>', methods=('POST',))
@flask_login.login_required
@requires_role('admin')
def delete(pid):
    db = connect_db()

    # remove attachments
    attachments = db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,))
    for a in attachments:
        path = os.path.join(app.config['uploads_path'], a['filename'])
        if os.path.isfile(path):
            os.remove(path)
    db.execute("delete from attachment where presentation_id=?", (pid,))
    
    db.execute("""delete from presentation where id=?""", (pid,))
    
    
    db.commit()
    
    flash('Presentation deleted.')
    return redirect(url_for('home'))
    
@app.route('/getfile/<int:aid>', methods=('GET',))
@flask_login.login_required
def getfile(aid):
    db = connect_db()
    attachment = db.execute("""select * from attachment a where a.id = ?""", (aid,)).fetchone()

    if attachment is None:
        db.close()
        abort(404)
        
    return send_from_directory(app.config['uploads_path'], attachment['filename'], as_attachment=True)
    
@app.route('/delete_attachment/<int:aid>', methods=('POST',))
@flask_login.login_required
@requires_role('admin')
def delete_attachment(aid):
    db = connect_db()
    attachment = db.execute("""select * from attachment a where a.id = ?""", (aid,)).fetchone()

    if attachment is None:
        db.close()
        abort(404)
    
    path = os.path.join(app.config['uploads_path'], attachment['filename'])
    if os.path.isfile(path):
        os.remove(path)
    
    db.execute("""delete from attachment where id=?""", (aid,))
    db.commit()
    
    flash('Attachment %s has been removed' % attachment['filename'])    
    return redirect(url_for('edit', pid=attachment['presentation_id']))
    
@app.route('/login', methods=('GET', 'POST'))
def login():

    db = connect_db()
    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user_row = db.execute("select * from user u where u.username = ?", (username,)).fetchone()
        
        if user_row is not None and pbkdf2_sha256.verify(password, user_row['password_hash']):
            user = User()
            
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
        flash('Incorrect Credentials')
    
    return render_template('login.html', form=form)
    
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

def connect_db():
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    if 'db' not in g:
        g.db = db = sqlite3.connect(app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = dict_factory
    
    return g.db

@app.teardown_appcontext
def close_db(error):
    # removes an attribute by name
    db = g.pop('db', None)

    if db:
        db.close()

def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

# from stackoverflow ...
def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))





