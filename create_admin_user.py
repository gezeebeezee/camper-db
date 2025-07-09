from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if admin user already exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            team_number=None,  # Admins don't need a team
            role='admin'
        )
        admin_user.password = 'trickypassword'  # This sets the hashed password
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
