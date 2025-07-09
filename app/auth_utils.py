from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password_hash, provided_password):
    return check_password_hash(stored_password_hash, provided_password)

def is_admin(user):
    return user.role == 'admin'

def is_leader(user):
    return user.role == 'leader'

def is_counselor(user):
    return user.role == 'counselor'

