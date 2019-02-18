from flask import Flask, render_template, abort
import json
import sqlite3

app = Flask(__name__)
app.config['db_path'] = 'db.sqlite'

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
    
    db.close()
    
    return render_template('details.html', p=presentation)
    
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