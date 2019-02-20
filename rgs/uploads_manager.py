import os
from werkzeug.utils import secure_filename
from flask import request
import random
import string

class UploadsManager:

    def __init__(self, path, field_name):
        self.path = path
        self.field_name = field_name

    def save(self):
        filenames = []
        if self.field_name in request.files:
           for f in request.files.getlist(self.field_name):
                filename = generate_file_name(f.filename)
                f.save(os.path.join(self.path, filename))
                filenames.append(filename)
        return filenames

    def delete(self, attachment):
        path = os.path.join(self.path, attachment['filename'])
        if os.path.isfile(path):
            os.remove(path)
    
    def delete_all(self, attachments):
        for attachment in attachments:
            self.delete(attachment)

def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

# from stackoverflow ...
def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

