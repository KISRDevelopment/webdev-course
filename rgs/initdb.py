import sqlite3
import sys
import os

instance_path = sys.argv[1]

# 1. create directories recursively
uploads_path = os.path.join(instance_path, 'uploads')
if not os.path.exists(uploads_path):
    os.makedirs(uploads_path)

# 2. initialize database
db_path = os.path.join(instance_path, 'db.sqlite')
db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
script = open('schema.sql', 'r').read()
db.executescript(script)
db.close()

# 3. generate strong key
secret_key = os.urandom(16)
#print(secret_key)

# 4. create basic configuration file
config_path = os.path.join(instance_path, 'application.cfg')
with open(config_path, 'w') as f:
    f.write('DB_PATH = %s\n' % repr('db.sqlite'))
    f.write('UPLOADS_PATH = %s\n' % repr('uploads'))
    f.write('SECRET_KEY = %s\n' % repr(secret_key))
    