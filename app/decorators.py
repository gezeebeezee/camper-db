from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.team_number is not None:
            flash("Admin access only.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
