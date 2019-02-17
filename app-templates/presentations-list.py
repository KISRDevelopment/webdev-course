from flask import Flask, render_template, abort, request, redirect, url_for, \
    flash
import json
from forms import PresentationForm
import datetime

app = Flask(__name__)
app.config['presentations_path'] = 'presentations.json'
app.secret_key = b'xYFRlEs3@a'

@app.route('/')
def home():
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f)
    
    return render_template('home.html', presentations=presentations)
    
    
@app.route('/presentation/<int:pid>')
def details(pid):
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f)
        
    # find the first presentation that matches pid, otherwise return None
    presentation = next((p for p in presentations if p['id'] == pid), None)
    
    if presentation is None:
        abort(404)
    
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET','POST'))
def create():
    
    form = PresentationForm()
    
    if form.validate_on_submit():
        
        with open(app.config['presentations_path'], 'r') as f:
            presentations = json.load(f) 
            
        # compute next id to use
        next_id = 1
        if len(presentations) > 0:
            next_id = presentations[-1]["id"] + 1
        
        # create new presentation record
        new_pres = {
            "id" : next_id,
            "attachments" : []
        }
        for fname in ["title", "presenters", "scheduled", "time_range", "notes"]:
            new_pres[fname] = getattr(form, fname).data
        new_pres['scheduled'] = new_pres['scheduled'].strftime('%Y-%m-%d')

        presentations.append(new_pres)
        
        # write back to "database"
        with open(app.config['presentations_path'], 'w') as f:
            json.dump(presentations, f, indent=4)
        
        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)

@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
def edit(pid):
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f) 
    
    presentation = next((p for p in presentations if p['id'] == pid), None)
    presentation['scheduled'] = datetime.datetime.strptime(presentation['scheduled'], '%Y-%m-%d').date()
    
    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
    
        for fname in ["title", "presenters", "scheduled", "time_range", "notes"]:
            presentation[fname] = getattr(form, fname).data
        presentation['scheduled'] = presentation['scheduled'].strftime('%Y-%m-%d')
        
        # write back to "database"
        with open(app.config['presentations_path'], 'w') as f:
            json.dump(presentations, f, indent=4)
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
        
    return render_template('edit.html', form=form, pid=pid)
    
@app.route('/delete/<int:pid>', methods=('POST',))
def delete(pid):
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f) 
    
    presentations = [p for p in presentations if p['id'] != pid]
    
    # write back to "database"
    with open(app.config['presentations_path'], 'w') as f:
        json.dump(presentations, f, indent=4)
       
    flash('Presentation deleted.')
    return redirect(url_for('home'))
    