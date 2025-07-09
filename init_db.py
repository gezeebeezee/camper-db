from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)
    
    # Check if the 'user' table already exists
    if not inspector.has_table('user'):
        db.create_all()
        print("✅ Database initialized.")
    else:
        print("ℹ️ Database already exists. Skipping initialization.")
