from flask import Flask, render_template, abort, request, redirect, url_for, \
    flash
import json
from forms import PresentationForm

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

    
