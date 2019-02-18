import json
from flask import current_app, g
import datetime

def get_db():
    
    if 'db' not in g:
        with open(current_app.config['presentations_path'], 'r') as f:
            g.db = json.load(f)

        # convert date string into an actual datetime object
        for p in g.db:    
            p['scheduled'] = datetime.datetime.strptime(p['scheduled'], '%Y-%m-%d').date()
    
    return g.db

def close_db(error):
    # removes an attribute by name
    db = g.pop('db', None)
    
    if db is None:
        return

    # back to a string ... 
    for p in db:
        p['scheduled'] = p['scheduled'].strftime('%Y-%m-%d')

    # commit transactions
    if db is not None:
        with open(current_app.config['presentations_path'], 'w') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
    
def get_presentations():    
    db = get_db()
    return db

def get_presentation(pid):
    db = get_db()
    
    presentation = next((p for p in db if p['id'] == pid), None)

    return presentation


def create_presentation(new_pres):

    db = get_db()
    
    # compute next id to use
    next_id = 1
    if len(db) > 0:
        next_id = db[-1]["id"] + 1
    
    new_pres['id'] = next_id
    
    db.append(new_pres)

def update_presentation(pres):
    db = get_db()
    for i in range(len(db)):
        p = db[i]
        if p['id'] == pres['id']:
            db[i] = pres
            break

def delete_presentation(pid):
    db = get_db()
    for i in range(len(db)):
        if db[i]['id'] == pid:
            p = db[i]            
            del db[i]
            return p
    return None

def delete_attachment(pid, aid):
    pres = get_presentation(pid)
    if not pres or aid < 0 or aid >= len(pres['attachments']):
        return None
    fname = pres['attachments'][aid]

    del pres['attachments'][aid]

    return fname

def get_attachment(pid, aid):
    pres = get_presentation(pid)
    if not pres or aid < 0 or aid >= len(pres['attachments']):
        return None
    return pres['attachments'][aid]
    
