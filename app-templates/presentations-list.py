from flask import Flask, render_template, abort
import json

app = Flask(__name__)
app.config['presentations_path'] = 'presentations.json'

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
    
    
    