from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .models import User, USER_DATA

app = Flask(__name__)

app.config.from_object('config.Config')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # uses the static method in your User class

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USER_DATA.get(username)
        if user and user['password'] == password:
            login_user(User(username))
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



from app import routes, models

