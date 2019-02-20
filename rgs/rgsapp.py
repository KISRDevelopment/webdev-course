from flask import Flask, render_template, abort, request, redirect, url_for, flash, \
    send_from_directory, g
from forms import PresentationForm, LoginForm
import db
import uploads_manager
import auth
import default_settings
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('default_settings')
app.config.from_pyfile('application.cfg', silent=True)
app.config['UPLOADS_PATH'] = os.path.join(app.instance_path, app.config['UPLOADS_PATH'])
app.config['DB_PATH'] = os.path.join(app.instance_path, app.config['DB_PATH'])

app.teardown_appcontext(db.close_db)
auth.init(app, 'login')

uploads = uploads_manager.UploadsManager(app.config['UPLOADS_PATH'], 'attachments')

render_template_old = render_template
def new_render_template(*args, **kwargs):
    kwargs['user'] = auth.current_user()
    return render_template_old(*args,**kwargs)
render_template = new_render_template

@app.route('/')
@auth.login_required
def home():
    
    presentations = db.get_presentations_summary()
    output = render_template('home.html', presentations=presentations)

    return output
    
@app.route('/presentation/<int:pid>')
@auth.login_required
def details(pid):
    presentation = db.get_presentation(pid)
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET', 'POST'))
@auth.login_required
@auth.requires_role('admin')
def create():
    form = PresentationForm()
    
    if form.validate_on_submit():
        
        filenames = uploads.save()
        
        presentation = form.data
        presentation['attachments'] = [{ 'filename' : a } for a in filenames]

        db.create_presentation(presentation)

        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)
   
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
@auth.login_required
@auth.requires_role('admin')
def edit(pid):
    
    presentation = db.get_presentation(pid)

    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():

        # upload attachments
        filenames = uploads.save()
        
        old_attachments = presentation['attachments']

        presentation = form.data
        presentation['id'] = pid
        presentation['attachments'] = old_attachments + [
            { 'filename' : a, 'presentation_id' : pid } 
            for a in filenames
        ]
        
        db.update_presentation(presentation)

        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    return render_template('edit.html', form=form, pid=pid, 
        attachments=presentation['attachments'])
    
@app.route('/delete/<int:pid>', methods=('POST',))
@auth.login_required
@auth.requires_role('admin')
def delete(pid):

    presentation = db.get_presentation(pid)
    if not presentation:
        abort(404)

    uploads.delete_all(presentation['attachments'])
    
    db.delete_presentation(pid)

    flash('Presentation deleted.')
    return redirect(url_for('home'))
    
@app.route('/getfile/<int:aid>', methods=('GET',))
@auth.login_required
def getfile(aid):
    attachment = db.get_attachment(aid)

    if attachment is None:
        abort(404)
        
    return send_from_directory(app.config['UPLOADS_PATH'], attachment['filename'], as_attachment=True)
    
@app.route('/delete_attachment/<int:aid>', methods=('POST',))
@auth.login_required
@auth.requires_role('admin')
def delete_attachment(aid):
    
    attachment = db.get_attachment(aid)

    if attachment is None:
        abort(404)
    
    uploads.delete(attachment)

    db.delete_attachment(aid)

    flash('Attachment %s has been removed' % attachment['filename'])    
    return redirect(url_for('edit', pid=attachment['presentation_id']))
    
@app.route('/login', methods=('GET', 'POST'))
def login():

    if not auth.current_user().is_anonymous:
        return redirect(url_for('home'))

    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        if auth.authenticate(username, password):
            auth.login_user(username)
            return redirect(url_for('home'))

        flash('Incorrect Credentials')
    
    return render_template('login.html', form=form)
    
@app.route('/logout')
def logout():
    auth.logout_user()
    return redirect(url_for('login'))
