
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
app.secret_key = 'dev_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
MAX_STORAGE_BYTES = 10 * 1024 * 1024 * 1024  # 10GB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# התחברות לגוגל דרייב
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
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
            if get_total_storage() + len(file.read()) > MAX_STORAGE_BYTES:
                flash('חרגת ממגבלת 10GB')
                return redirect(request.url)
            file.seek(0)
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(local_path)

            # העלאה לדרייב
            gfile = drive.CreateFile({'title': filename})
            gfile.SetContentFile(local_path)
            gfile.Upload()

            flash('הקובץ הועלה ונשמר בדרייב')
            return redirect(url_for('upload_file'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash('הקובץ נמחק')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
