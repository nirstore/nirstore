from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx'}

USERNAME = "com@nir.org.il"
PASSWORD = "Comadmin-1"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect(url_for('upload_file'))
        else:
            flash('שם משתמש או סיסמה לא נכונים')
    return render_template('login.html')

@app.route('/files', methods=['GET', 'POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('לא נבחר קובץ')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('לא נבחר קובץ')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            if get_folder_size(UPLOAD_FOLDER) + len(file.read()) > 10 * 1024 * 1024 * 1024:
                flash('חרגת מהמגבלת 10GB')
            else:
                file.seek(0)
                file.save(filepath)
                flash('הקובץ הועלה בהצלחה')
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('upload.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    flash('הקובץ נמחק')
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

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
@app.route('/list')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('files.html', files=files)
