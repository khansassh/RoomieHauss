from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner1 TEXT NOT NULL,
        partner2 TEXT NOT NULL,
        pin TEXT NOT NULL,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner1 TEXT NOT NULL,
        partner2 TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()
    print("Database checked / created successfully.")

@app.route('/budget-page')
def budget_page():
    if 'partner1' in session and 'partner2' in session:
        status = session.get('status')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''SELECT description, amount, date 
             FROM budget 
             WHERE partner1 = ? AND partner2 = ? AND type = 'income' ''',
          (session['partner1'], session['partner2']))
        income_data = c.fetchall()

        c.execute('''SELECT description, amount, date 
             FROM budget 
             WHERE partner1 = ? AND partner2 = ? AND type = 'outcome' ''',
          (session['partner1'], session['partner2']))
        outcome_data = c.fetchall()


        c.execute('''SELECT description, amount, date, type
                     FROM budget 
                     WHERE partner1 = ? AND partner2 = ?''',
                  (session['partner1'], session['partner2']))
        budget_data = c.fetchall()

        c.execute('''SELECT COALESCE(SUM(amount), 0)
                     FROM budget 
                     WHERE partner1 = ? AND partner2 = ? AND type = 'income' ''',
                  (session['partner1'], session['partner2']))
        total_income = c.fetchone()[0]

        c.execute('''SELECT COALESCE(SUM(amount), 0)
                     FROM budget 
                     WHERE partner1 = ? AND partner2 = ? AND type = 'outcome' ''',
                  (session['partner1'], session['partner2']))
        total_outcome = c.fetchone()[0]

        conn.close()

        balance = total_income - total_outcome

        if status == 'girl':
            return render_template('girlandgirlpage.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status,
                                   budget_data=budget_data,
                                   total_income=total_income,
                                   total_outcome=total_outcome,
                                   balance=balance,
                                    income_data=income_data,
                                   outcome_data=outcome_data)
        
        elif status == 'boy':
            return render_template('boyandboypage.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status,
                                   budget_data=budget_data,
                                   total_income=total_income,
                                   total_outcome=total_outcome,
                                   balance=balance,
                                   income_data=income_data,
                           outcome_data=outcome_data)
        
        elif status == 'married':
            return render_template('married.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status,
                                   budget_data=budget_data,
                                   total_income=total_income,
                                   total_outcome=total_outcome,
                                   balance=balance,
                                   income_data=income_data,
                           outcome_data=outcome_data)
        
        else:
            flash("Unknown status.")
            return redirect(url_for('landing_page'))
    
    else:
        return redirect(url_for('login_page'))

@app.route('/add-income', methods=['POST'])
def add_income():
    if 'partner1' in session and 'partner2' in session:
        description = request.form['description']
        amount = int(request.form['amount'])
        date_now = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO budget (partner1, partner2, type, description, amount, date) VALUES (?, ?, ?, ?, ?, ?)',
                  (session['partner1'], session['partner2'], 'income', description, amount, date_now))
        conn.commit()
        conn.close()

        flash("Income added successfully.")
        return redirect(url_for('budget_page'))
    else:
        return redirect(url_for('login_page'))

@app.route('/add-outcome', methods=['POST'])
def add_outcome():
    if 'partner1' in session and 'partner2' in session:
        description = request.form['description']
        amount = int(request.form['amount'])
        date_now = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO budget (partner1, partner2, type, description, amount, date) VALUES (?, ?, ?, ?, ?, ?)',
                  (session['partner1'], session['partner2'], 'outcome', description, amount, date_now))
        conn.commit()
        conn.close()

        flash("Outcome added successfully.")
        return redirect(url_for('budget_page'))
    else:
        return redirect(url_for('login_page'))

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    partner1 = request.form['partner1']
    partner2 = request.form['partner2']
    pin = request.form['pin']
    status = request.form.get('status', '')

    if not partner1 or not partner2 or not pin:
        return render_template('register.html', error='Please fill out all fields.')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (partner1, partner2, pin, status) VALUES (?, ?, ?, ?)', 
              (partner1, partner2, pin, status))
    conn.commit()
    conn.close()

    return render_template('register.html', success='You\'re successfully registered!')

@app.route('/login', methods=['POST'])
def login():
    partner1 = request.form['partner1']
    partner2 = request.form['partner2']
    pin = request.form['pin']

    if not partner1 or not partner2 or not pin:
        return render_template('login.html', error='Please fill out all fields.')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE partner1 = ? AND partner2 = ? AND pin = ?', 
              (partner1, partner2, pin))
    user = c.fetchone()
    conn.close()

    if user:
        session['partner1'] = partner1
        session['partner2'] = partner2
        session['status'] = user[4]
        return redirect(url_for('landing_page'))
    else:
        return render_template('login.html', error='Invalid partner1, partner2, or pin.')

@app.route('/landing-page')
def landing_page():
    if 'partner1' in session and 'partner2' in session:
        return render_template('landingpage.html', 
                               partner1=session['partner1'], 
                               partner2=session['partner2'],
                               status=session.get('status'))
    else:
        return redirect(url_for('login_page'))

@app.route('/inside-page')
def inside_page():
    if 'partner1' in session and 'partner2' in session:
        status = session.get('status')
        if status == 'girl':
            return render_template('insidegirl.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status)
        elif status == 'boy':
            return render_template('insideboy.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status)
        elif status == 'married':
            return render_template('insidemarried.html',
                                   partner1=session['partner1'],
                                   partner2=session['partner2'],
                                   status=status)
        else:
            flash("Unknown status.")
            return redirect(url_for('landing_page'))
    else:
        return redirect(url_for('login_page'))


# @app.route('/marriage-page')
# def marriage_page():
#     if 'partner1' in session and 'partner2' in session:
#         return render_template('married.html', 
#                                partner1=session['partner1'], 
#                                partner2=session['partner2'],
#                                status=session.get('status'))
#     else:
#         return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
