
from . import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class Camper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    team_number = db.Column(db.Integer, nullable=True)
    disability = db.Column(db.String(150))
    medications = db.Column(db.String(250))
    diet = db.Column(db.String(150))
    notes = db.Column(db.Text)
    qr_token = db.Column(db.String(100), unique=True, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)

# USER_DATA = {
#     "admin": {"password": "adminpass"}
# }
