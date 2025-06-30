from app import create_app, db
from app.models import User
from app.auth_utils import hash_password

app = create_app()
with app.app_context():
    db.create_all()

    # Create a user
    new_user = User(username="kle", password_hash=hash_password("trickypassword"))
    db.session.add(new_user)
    db.session.commit()

    print("User created successfully.")
