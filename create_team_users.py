from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    for team in range(1, 7):  # Example: Teams 1 through 6
        username = f"Team{team}"
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                password_hash=generate_password_hash("team123"),
                team_number=team
            )
            db.session.add(user)
    db.session.commit()
    print("Team users created.")
