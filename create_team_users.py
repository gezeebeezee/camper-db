from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    for team in range(1, 13):  # Example: Teams 1 through 12
        username = f"team{team}"
        if not User.query.filter_by(username=username).first():
            user = User(username=username, team_number=team)
            user.password = f"team{team}"  # Uses the password setter
            db.session.add(user)
    db.session.commit()
    print("Team users created.")
