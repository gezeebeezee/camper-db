
from . import db
from flask_login import UserMixin

class Camper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    disability = db.Column(db.String(150))
    medications = db.Column(db.String(250))
    diet = db.Column(db.String(150))
    notes = db.Column(db.Text)
    qr_token = db.Column(db.String(100), unique=True, nullable=False)

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @staticmethod
    def get(username):
        if username in USER_DATA:
            return User(username)
        return None

USER_DATA = {
    "admin": {"password": "adminpass"}
}
