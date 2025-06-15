
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
MAX_SIZE = 10 * 1024 * 1024 * 1024  # 10GB

USERNAME = 'com@nir.org.il'
PASSWORD = 'Comadmin-1'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload_file'))
        flash('שם משתמש או סיסמה לא נכונים')
    return render_template('login.html')

@app.route('/files', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            if get_folder_size(UPLOAD_FOLDER) + len(file.read()) <= MAX_SIZE:
                file.seek(0)
                file.save(filepath)
                flash('קובץ הועלה בהצלחה')
            else:
                flash('חרגת ממגבלת 10GB')
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('upload.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    flash('קובץ נמחק')
    return redirect(url_for('upload_file'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def get_folder_size(path='.'):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
    return total

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
   import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

