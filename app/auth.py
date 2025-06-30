from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only allow admin (team_number is None)
    if current_user.team_number is not None:
        return "Access denied", 403  # or redirect with a flash message

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm']
        team_number = request.form.get('team_number', type=int)

        if not username or not password:
            return render_template('register.html', error="All fields are required.")
        if password != confirm:
            return render_template('register.html', error="Passwords do not match.")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists.")
        if team_number is not None and not isinstance(team_number, int):
            return render_template('register.html', error="Team number must be an integer.")

        new_user = User(username=username, team_number=team_number)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('register.html')
