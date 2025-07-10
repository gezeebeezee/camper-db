from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
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
    return render_template('manage_users.html', users=users)

@auth.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.team_number is None:
        abort(403)  # Only admins (team_number = None) can edit users

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form['username'].strip()
        team_number = request.form['team_number'].strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate team_number
        user.team_number = int(team_number) if team_number else None
        user.username = username

        # If password fields are filled out, update the password
        if password:
            if password != confirm_password:
                return render_template('edit_user.html', user=user, error="Passwords do not match.")
            user.password = password  # uses the @password.setter in User model

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
        username = request.form['username'].strip().lower()
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
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm']
        role = request.form.get('role')
        team_number = request.form.get('team_number')
        next_url = request.args.get('next') or url_for('main.index')

        # Basic validation
        if not username or not password or not confirm or not role:
            return render_template('register.html', error="All fields are required.", next=next_url)
        if password != confirm:
            return render_template('register.html', error="Passwords do not match.", next=next_url)
        if User.query.filter_by(username=username.lower()).first():
            return render_template('register.html', error="Username already exists.", next=next_url)

        # Admin-only restriction
        if role == 'admin' and current_user.role != 'admin':
            return render_template('register.html', error="Only admins can create admin users.", next=next_url)

        # Team number validation
        if role == 'admin':
            team_number = None
        else:
            try:
                team_number = int(team_number)
                if team_number < 1:
                    raise ValueError
            except (ValueError, TypeError):
                return render_template('register.html', error="Team number must be a positive integer.", next=next_url)

        # Create user
        new_user = User(username=username.lower(), role=role, team_number=team_number)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()

        return redirect(next_url)

    next_url = request.args.get('next') or url_for('main.index')
    return render_template('register.html', next=next_url)

