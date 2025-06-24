from app import db
import uuid

class Camper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    disability = db.Column(db.Text)
    medications = db.Column(db.Text)
    diet = db.Column(db.Text)
    notes = db.Column(db.Text, nullable=True)
    qr_token = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4()))
