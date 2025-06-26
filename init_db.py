from app import create_app, db

# Create the app instance
app = create_app()

# Run in the application context
with app.app_context():
    db.create_all()
    print("✅ Database initialized.")
