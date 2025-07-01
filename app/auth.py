from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .models import User
from . import db
from .decorators import admin_required


auth = Blueprint('auth', __name__)

@auth.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@auth.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.team_number is not None:
        return redirect(url_for('main.index'))  # Not admin

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form['username'].strip()
        team_number = request.form.get('team_number')
        password = request.form.get('password')

        if not username:
            return render_template('edit_user.html', user=user, error="Username is required.")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            return render_template('edit_user.html', user=user, error="Username already taken.")

        user.username = username
        user.team_number = int(team_number) if team_number else None

        if password:
            user.password = password  # uses the password setter

        db.session.commit()
        return redirect(url_for('auth.manage_users'))

    return render_template('edit_user.html', user=user)

@auth.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for('auth.manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('auth.manage_users'))


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
        return "Access denied", 403  # Or redirect with flash("Access denied")

    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm']

        # Validate required fields
        if not username or not password or not request.form.get('team_number'):
            return render_template('register.html', error="All fields are required.")

        # Validate password confirmation
        if password != confirm:
            return render_template('register.html', error="Passwords do not match.")

        # Check for duplicate username
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists.")

        # Validate team number
        try:
            team_number = int(request.form['team_number'])
            if team_number < 1:
                raise ValueError
        except (ValueError, TypeError):
            return render_template('register.html', error="Team Number must be a positive integer.")

        # Create user
        new_user = User(username=username, team_number=team_number)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('register.html')
