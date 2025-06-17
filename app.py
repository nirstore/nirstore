from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session, flash
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
MAX_STORAGE_BYTES = 10 * 1024 * 1024 * 1024  # 10GB

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_total_storage():
    total = 0
    for f in os.listdir(UPLOAD_FOLDER):
        total += os.path.getsize(os.path.join(UPLOAD_FOLDER, f))
    return total

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('לא נבחר קובץ')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('לא נבחר קובץ')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            file.seek(0)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            f = drive.CreateFile({'title': filename})
            f.SetContentFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f.Upload()

            flash('הקובץ הועלה ל־Google Drive')
            return redirect(url_for('upload_file'))

    return render_template('upload.html')

@app.route('/logout')
def logout():
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
