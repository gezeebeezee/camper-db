
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
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        if user_id in USER_DATA:
            return User(user_id)
        return None

USER_DATA = {
    "admin": {"password": "trickypassword"}
}
