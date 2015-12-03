from flask import Flask
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config.from_object('app.config')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16 MB file-size limit
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static')
app.config['BACKUP_FOLDER'] = os.path.join(basedir, 'static/backups')


app.config['SECRET_KEY'] = 'abracadabara'

from app import views
