from flask import Flask, render_template, request, redirect, url_for
import src.database as db


app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if db.validate_login(request.form['email'],
                             request.form['password']):
            return 'success!'
        else:
            error = 'Invalid email/password'
    return render_template('login.html', error=error)


if __name__ == '__main__':
    app.run()
