#
# Database access routines
#
import sqlite3
from flask import g, current_app

PRESENTATION_COLS = ['title', 'presenters', 'scheduled', 'time_range', 'notes']
ATTACHMENT_COLS = ['presentation_id', 'filename']

def connect_db():
    """ creates a new connection to a database, if one does not
    exist already within the current request"""
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    if 'db' not in g:
        g.db = db = sqlite3.connect(current_app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = dict_factory
    
    return g.db

def close_db(error):
    """ closes the connection to the database, if one exists """
    db = g.pop('db', None)
    if db:
        db.commit() # save changes
        db.close()

def get_presentations_summary():
    presentations = connect_db().execute("select * from presentation")
    return presentations

def get_presentation(pid):
    presentation = connect_db().execute("select * from presentation p where p.id = ?", (pid,)).fetchone()
    if presentation is None:
        return None 
    
    presentation['attachments'] = get_attachments(pid)

    return presentation

def create_presentation(presentation):
    pid = _insert('presentation', presentation, PRESENTATION_COLS)
    
    for a in presentation['attachments']:
        a['presentation_id'] = pid
        _insert('attachment', a, ATTACHMENT_COLS)
    

def update_presentation(presentation):
    _update('presentation', presentation, PRESENTATION_COLS)

    # insert attachments which have no ID
    for a in presentation['attachments']:
        if 'id' not in a:
            a['presentation_id'] = presentation['id']
            _insert('attachment', a, ATTACHMENT_COLS)

def delete_presentation(pid):
    connect_db().execute("delete from attachment where presentation_id = ?", (pid,))
    connect_db().execute("delete from presentation where id = ?", (pid,))

def get_attachments(pid):
    attachments = connect_db().execute("select * from attachment a where a.presentation_id = ?", (pid,))
    return list(attachments)

def get_attachment(aid):
    attachment = connect_db().execute("select * from attachment a where a.id=?", (aid,)).fetchone()
    return attachment

def delete_attachment(aid):
    connect_db().execute("delete from attachment where id=?", (aid,))

def get_user(username):
    return connect_db().execute("select * from user u where u.username = ?", (username,)).fetchone()

def _insert(table, r, columns=None):
    """ helper function for writing insert queries """
    if not columns:
        columns = list(r.keys())
    
    columns_str = ','.join(columns)
    placeholders_str = ','.join(['?'] * len(columns))

    query = "insert into %s(%s) values(%s)" % (table, columns_str, placeholders_str)

    vals = [r[c] for c in columns]

    db = connect_db()
    cursor = db.execute(query, vals)
    
    pid = cursor.lastrowid

    return pid

def _update(table, r, columns=None):
    """ helper function for writing update queries """
    if not columns:
        columns = [c for c in list(r.keys()) if c != 'id']

    columns_str = ', '.join(['%s=?' % (c) for c in columns])

    query = "update %s set %s where id=%d" % (table, columns_str, r['id'])

    vals = [r[c] for c in columns]

    connect_db().execute(query, vals)

