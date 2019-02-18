from flask import Flask, render_template, abort, request, redirect, url_for, flash, \
    send_from_directory
import json
import sqlite3
import re
from forms import PresentationForm
import random
import os
from werkzeug.utils import secure_filename
import string

range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)

app = Flask(__name__)
app.config['db_path'] = 'db.sqlite'
app.secret_key = b'xYFRlEs3@a'
app.config['uploads_path'] = './uploads/'
@app.route('/')
def home():
    
    db = connect_db()
    
    presentations = db.execute("select * from presentation")
    
    output = render_template('home.html', presentations=presentations)
    
    db.close()
    
    return output
    
@app.route('/presentation/<int:pid>')
def details(pid):
    
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    attachments = db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,))
    
    presentation['attachments'] = list(attachments)
    
    db.close()
    
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET', 'POST'))
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
        db.close()
        
        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)
   
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
def edit(pid):
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
        db.execute("""update presentation set title = ?, presenters = ?,
            scheduled = ?, time_range = ?, notes = ? where id=?""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')] + [pid])
        db.commit()
        db.close()
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    db.close()
    return render_template('edit.html', form=form, pid=pid)
    
@app.route('/delete/<int:pid>', methods=('POST',))
def delete(pid):
    db = connect_db()
    db.execute("""delete from presentation where id=?""", (pid,))
    db.commit()
    db.close()
    flash('Presentation deleted.')
    return redirect(url_for('home'))
    
@app.route('/getfile/<int:aid>', methods=('GET',))
def getfile(aid):
    db = connect_db()
    attachment = db.execute("""select * from attachment a where a.id = ?""", (aid,)).fetchone()

    if attachment is None:
        abort(404)
        
    return send_from_directory(app.config['uploads_path'], attachment['filename'], as_attachment=True)
    
def connect_db():
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    db = sqlite3.connect(app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = dict_factory
    return db

def validate_onsubmit():
    if request.method == 'GET':
        return False, []
    
    f = request.form
    
    errors = []
    
    if len(f['title']) < 4:
        errors.append('Title has to be at least 4 characters long')
    if len(f['presenters']) < 4 or re.search(r'\d', f['presenters']):
        errors.append('Presenters has to be at least 4 alphabetical characters long')
    if not re.match(r'\d{4}\-\d{2}\-\d{2}', f['scheduled']):
        errors.append('Date needs to be YYYY-MM-DD')
    if not range_regex.match(f['time_range']):
        errors.append('Time range should be like 9-10am, 9:30-11:40, etc.')
    
    is_valid_submission = len(errors) == 0
    return is_valid_submission, errors
    
def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

# from stackoverflow ...
def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))