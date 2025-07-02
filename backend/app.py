from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner1 TEXT NOT NULL,
        partner2 TEXT NOT NULL,
        pin TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    partner1 = request.form['partner1']
    partner2 = request.form['partner2']
    pin = request.form['pin']

    if not partner1 or not partner2 or not pin:
        return render_template('register.html', error='Please fill out all fields.')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (partner1, partner2, pin) VALUES (?, ?, ?)', (partner1, partner2, pin))
    conn.commit()
    conn.close()

    return render_template('register.html', success='You\'re successfully registered!')

if __name__ == "__main__":
    init_db()  # if you use this
    app.run(host="0.0.0.0", port=5000, debug=True)
