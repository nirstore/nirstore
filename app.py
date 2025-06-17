from flask import Flask, request, redirect, url_for, render_template, flash
import os
from werkzeug.utils import secure_filename
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
app.secret_key = 'secret'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = None  # מאפשר העלאת כל סוגי הקבצים

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

# 👇 החלף בזה את ה־ID של תיקיית store המשותפת
STORE_FOLDER_ID = '1NfAOvPFJCssjB7iNwkBMgOjCEJUsZ3aa'

def allowed_file(filename):
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('לא נבחר קובץ')
            return redirect(request.url)
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(local_path)
            f = drive.CreateFile({'title': filename, 'parents': [{'id': STORE_FOLDER_ID}]})
            f.SetContentFile(local_path)
            f.Upload()
            flash('✅ הקובץ הועלה לתיקיית Google Drive בשם "store"')
            return redirect(url_for('upload_file'))
    return render_template('upload.html')
