import sqlite3
import sys

path = sys.argv[1]

db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
script = open('schema.sql', 'r').read()
db.executescript(script)
db.close()
