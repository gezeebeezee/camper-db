# from app import create_app, db
# from app.models import User
# from app.auth_utils import hash_password

# app = create_app()
# with app.app_context():
#     db.create_all()

#     # Create a user
#     new_user = User(username="kle", password_hash="trickypassword", team_number=None)
#     db.session.add(new_user)
#     db.session.commit()

#     print("User created successfully.")

from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin_user = User(username='admin')
    admin_user.password = 'trickypassword'
    admin_user.team_number = None  # Gives access to all teams
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created.")
