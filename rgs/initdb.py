import sqlite3
db = sqlite3.connect('db.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
script = open('schema.sql', 'r').read()
db.executescript(script)
db.close()
