from flask import Flask, render_template, abort, request, redirect, url_for, \
    flash, send_from_directory
import json
from forms import PresentationForm
import datetime
import random
import os
from werkzeug.utils import secure_filename
import string
import db

app = Flask(__name__)
app.config['presentations_path'] = 'presentations.json'
app.config['uploads_path'] = './uploads/'
app.secret_key = b'xYFRlEs3@a'
app.teardown_appcontext(db.close_db)

@app.route('/')
def home():
    presentations = db.get_presentations()
    return render_template('home.html', presentations=presentations)
    
    
@app.route('/presentation/<int:pid>')
def details(pid):
    presentation = db.get_presentation(pid)
    if presentation is None:
        abort(404)
    
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET','POST'))
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

        # create new presentation record
        new_pres = {
            "attachments" : attachments
        }
        for fname in ["title", "presenters", "scheduled", "time_range", "notes"]:
            new_pres[fname] = getattr(form, fname).data
        db.create_presentation(new_pres)        

        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)

@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
def edit(pid):
    presentation = db.get_presentation(pid)
    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
        
        attachments = presentation['attachments']
        if 'attachments' in request.files:
            for f in request.files.getlist('attachments'):
                filename = generate_file_name(f.filename)
                f.save(os.path.join(app.config['uploads_path'], filename))
                attachments.append(filename)

        for fname in ["title", "presenters", "scheduled", "time_range", "notes"]:
            presentation[fname] = getattr(form, fname).data
        
        db.update_presentation(presentation)
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
        
    return render_template('edit.html', form=form, p=presentation)
    
@app.route('/delete/<int:pid>', methods=('POST',))
def delete(pid):
    pres = db.delete_presentation(pid)

    if pres:
        for a in pres['attachments']:
            _remove_file(a)

    flash('Presentation deleted.')
    return redirect(url_for('home'))
    
@app.route('/delete_attachment/<int:pid>/<int:aid>', methods=('POST',))
def delete_attachment(pid, aid):
    
    filename = db.delete_attachment(pid, aid)
    if not filename:
        abort(404)
    
    _remove_file(filename)
    
    flash('Attachment %s has been removed' % filename)    
    return redirect(url_for('edit', pid=pid))

@app.route('/getfile/<int:pid>/<int:aid>', methods=('GET',))
def getfile(pid, aid):
    
    attachment = db.get_attachment(pid, aid)
    if not attachment:
        abort(404)

    return send_from_directory(app.config['uploads_path'], attachment, as_attachment=True)

def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

def _remove_file(filename):
    path = os.path.join(app.config['uploads_path'], filename)
    if os.path.isfile(path):
        os.remove(path)
