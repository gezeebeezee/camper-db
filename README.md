# CAMPER DATABASE

Project designed for camp to catalog campers into a database with name, disability, medications, special diets, and notes. A unique QR code is generated for each camper added, which will allow users to scan the QR code and view campers' profiles. The project currently uses SQLite, but will likely be migrated to mySQL or PostgreSQL for deployment.

**TO USE**
- (Optional) Create a virtual environment
    - python -m venv venv
    - venv/Scripts/activate
- Install required packages
    - pip install -r requirements.txt
- Run init_db.py to create 'camp.db'
    - This will create a folder called 'instance' with 'camp.db' inside.
- Run app.py
- Access the database at http://127.0.0.1:5000


**TO DO**
- Add CSRF protection to delete form
- Add authentication to allow select staff members to create/delete camper profiles
    - Added login, but currently utilizes hardcoded credentials

