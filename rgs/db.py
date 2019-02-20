import sqlite3
from flask import g

def connect_db():
    """ creates a new connection to a database, if one does not
    exist already within the current request"""
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    if 'db' not in g:
        g.db = db = sqlite3.connect(app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = dict_factory
    
    return g.db

def close_db():
    """ closes the connection to the database, if one exists """
    db = g.pop('db', None)
    if db:
        db.close()

def get_presentations_summary():
    """ gets list of all presentations, without attachments list"""
    presentations = connect_db().execute("select * from presentation")
    return presentations

def get_presentation(pid):
    """ gets a presentation by id along with notes """
    presentation = connect_db().execute("select * from presentation p where p.id = ?", (pid,)).fetchone()
    if presentation is None:
        return None 
    
    attachments = connect_db().execute("select * from attachment a where a.presentation_id = ?", (pid,))
    presentation['attachments'] = list(attachments)

    return presentation

def create_presentation(presentation):
    """ adds the given presentation to the database """
    db = connect_db()
    
    pid = _insert('presentation', presentation, ['title', 'presenters', 'scheduled', 'time_range', 'notes'])
    
    for a in attachments:
        a['presentation_id'] = pid
        _insert('attachment', a, ['presentation_id', 'filename'])
    
    db.commit()

def update_presentation(presentation):
    """ updates an existing presentation """


def delete_presentation(presentation):
    pass

def get_attachment(aid):
    pass

def delete_attachment(aid):
    pass

def get_user(username):
    pass

def _insert(table, r, columns=None):

    if not columns:
        columns = list(r.keys())
    
    columns_str = ','.join(columns)
    placeholders_str = ','.join(['?'] * len(columns))

    query = "insert into %s(%s) values(%s)" % (table, columns_str, placeholders_str)

    vals = [r[k] for k in columns]

    db = connect_db()
    cursor = db.execute(query, vals)
    
    pid = cursor.lastrowid

    return pid

def _update(table, r, columns=None):

    