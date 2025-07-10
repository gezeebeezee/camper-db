import os
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)

    # Step 1: Initialize DB if tables do not exist
    if not inspector.has_table('user'):
        db.create_all()
        print("✅ Database initialized.")
    else:
        print("ℹ️ Database already exists. Skipping initialization.")

    # Step 2: Create admin user if not found
    admin_username = 'admin'
    admin_exists = User.query.filter_by(username=admin_username).first()

    if not admin_exists:
        admin_password = os.getenv('ADMIN_PASSWORD', 'trickypassword')
        admin = User(username=admin_username, role='admin')
        admin.password = admin_password
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin user already exists.")
