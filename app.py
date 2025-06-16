from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session, flash
import os
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# הגדרות בסיסיות
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
USERNAME = 'com@nir.org.il'
PASSWORD = 'Comadmin-1,'
MAX_STORAGE_BYTES = 10 * 1024 * 1024 * 1024  # 10GB

# הגדרות מייל לשחזור סיסמה
EMAIL_SENDER = 'nirstore.sender@gmail.com'
EMAIL_PASSWORD = 'rkhu nvoy jyss popp'
EMAIL_RECEIVER = 'com@nir.org.il'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_total_storage():
    total = 0
    for f in os.listdir(UPLOAD_FOLDER):
        total += os.path.getsize(os.path.join(UPLOAD_FOLDER, f))
    return total

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload_file'))
        else:
            flash('שם משתמש או סיסמה שגויים')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/files', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
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
            if get_total_storage() + len(file.read()) > MAX_STORAGE_BYTES:
                flash('חרגת ממגבלת 10GB')
                return redirect(request.url)
            file.seek(0)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('הקובץ הועלה בהצלחה')
            return redirect(url_for('upload_file'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash('הקובץ נמחק')
    return redirect(url_for('upload_file'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        temp_password = PASSWORD  # או תיצור סיסמה זמנית אקראית
        try:
            send_reset_email(email, temp_password)
            flash('הסיסמה נשלחה למייל שלך')
        except Exception as e:
            flash('שליחת המייל נכשלה: ' + str(e))
        return redirect('/forgot-password')
    return render_template('forgot_password.html')

def send_reset_email(to_email, temp_password):
    msg = MIMEText(f'הסיסמה שלך היא: {temp_password}')
    msg['Subject'] = 'איפוס סיסמה - Nirstore'
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# החלק החשוב לתמיכה ב-Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
