from app import db
import uuid
from flask_login import UserMixin

# Simple user store
USER_DATA = {
    "admin": {
        "password": "trickypassword"  # In production, use hashed passwords
    }
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        if user_id in USER_DATA:
            return User(user_id)
        return None


class Camper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    disability = db.Column(db.Text)
    medications = db.Column(db.Text)
    diet = db.Column(db.Text)
    notes = db.Column(db.Text, nullable=True)
    qr_token = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4()))
