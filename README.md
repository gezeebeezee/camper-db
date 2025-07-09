# CAMPER DATABASE

Project designed for camp to catalog campers into a database with name, disability, medications, special diets, and notes. A unique QR code is generated for each camper added, which will allow users to scan the QR code and view campers' profiles. The project currently uses SQLite, but will likely be migrated to mySQL or PostgreSQL for deployment.

**TO USE**
- (Optional) Create a virtual environment
    - python -m venv venv
    - venv/Scripts/activate
- Install required packages
    - pip install -r requirements.txt
- Initialize the database
    - Run init_db.py to create 'camp.db'
    - This will create a folder called 'instance' with 'camp.db' inside.
    - Run create_user.py to create the admin user
    - Other python scripts are included to create team users with counselor role (create_team_users.py)
- Run app.py
- Access the database at http://127.0.0.1:5000


**TO DO**
- Add dark mode toggle

