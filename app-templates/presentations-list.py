from flask import Flask, render_template, abort, request, redirect, url_for, \
    flash
import json
import re

range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)

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
    
    is_valid_submission, errors = validate_onsubmit()
    
    if is_valid_submission:
        
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
        for field in ["title", "presenters", "scheduled", "time_range", "notes"]:
            new_pres[field] = request.form[field]
        
        presentations.append(new_pres)
        
        # write back to "database"
        with open(app.config['presentations_path'], 'w') as f:
            json.dump(presentations, f, indent=4)
        
        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', errors=errors)

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
    