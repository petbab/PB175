import secrets
from flask import Flask, render_template, request, redirect, url_for, session
import database as db

app = Flask(__name__, static_folder='static')
app.secret_key = secrets.token_hex(16)


database = db.Database('data/data.db')
database.setup()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        customer_id, valid = db.login(database, request.form['email'], request.form['password'])
        if valid:
            session['customer_id'] = customer_id
            return redirect(url_for('place_order'))
        error = 'Invalid email/password'

    return render_template('login.html', error=error)


@app.route('/place-order', methods=['GET', 'POST'])
def place_order():
    error = None
    if request.method == 'POST':
        error = 'Invalid email/password'

    return render_template('place_order.html', error=error)


if __name__ == '__main__':
    app.run()
