
from flask import Blueprint, render_template, redirect, url_for, request, send_from_directory, current_app, abort
from flask_login import login_required, current_user, login_user, logout_user
from .models import Camper, User
import os, secrets, qrcode
from PIL import Image, ImageDraw, ImageFont
from . import db

def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

def is_team_leader():
    return current_user.is_authenticated and current_user.role == 'team_leader'

def is_team_counselor():
    return current_user.is_authenticated and current_user.role == 'team_counselor'

def user_has_access_to_camper(camper):
    if is_admin():
        return True
    if current_user.team_number == camper.team_number:
        return True
    return False

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))

        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    team_filter = request.args.get('team_filter', '').strip()

    campers_query = Camper.query

    # Regular users only see their team
    if current_user.team_number is not None:
        campers_query = campers_query.filter_by(team_number=current_user.team_number)
    # Admin users can optionally filter by team
    elif team_filter.isdigit():
        campers_query = campers_query.filter_by(team_number=int(team_filter))

    # Apply name search (for both admin and regular users)
    if search_query:
        campers_query = campers_query.filter(Camper.name.ilike(f"%{search_query}%"))

    campers = campers_query.all()

    # Admin: provide all team numbers for dropdown
    team_numbers = []
    if current_user.team_number is None:
        team_numbers = sorted({c.team_number for c in Camper.query.filter(Camper.team_number != None).all()})

    return render_template('index.html', campers=campers, team_numbers=team_numbers)


@main.route('/camper/<string:token>')
@login_required
def camper_detail(token):
    camper = Camper.query.filter_by(qr_token=token).first_or_404()
    if current_user.role != 'admin' and camper.team_number != current_user.team_number:
        abort(403)
    return render_template('camper_detail.html', camper=camper)


@main.route('/add_camper', methods=['GET', 'POST'])
@login_required
def add_camper():
    if request.method == 'POST':
        name = request.form['name']
        disability = request.form['disability']
        medications = request.form['medications']
        diet = request.form['diet']
        notes = request.form['notes']

        # Determine team_number based on user role
        if current_user.role == 'admin':
            team_number = int(request.form['team_number'])
        else:
            team_number = current_user.team_number  # Force leader/counselor to use their own team

        qr_token = secrets.token_urlsafe(8)
        camper = Camper(
            name=name,
            team_number=team_number,
            disability=disability,
            medications=medications,
            diet=diet,
            notes=notes,
            qr_token=qr_token
        )

        db.session.add(camper)
        db.session.commit()

        # QR code generation logic (unchanged)
        base_url = os.getenv("PUBLIC_BASE_URL") or request.url_root.rstrip('/')
        qr_url = f"{base_url}{url_for('main.camper_detail', token=camper.qr_token)}"

        path = os.path.join(current_app.root_path, 'static', 'qrcodes', f'{qr_token}.png')
        qr_img = qrcode.make(qr_url).convert("RGB")
        qr_width, qr_height = qr_img.size

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        dummy_img = Image.new("RGB", (qr_width, 1))
        draw_dummy = ImageDraw.Draw(dummy_img)
        bbox = draw_dummy.textbbox((0, 0), camper.name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_padding = 12
        bottom_padding = 55
        total_height = qr_height + text_padding + text_height + bottom_padding
        final_img = Image.new("RGB", (qr_width, total_height), "white")
        draw = ImageDraw.Draw(final_img)
        final_img.paste(qr_img, (0, 0))
        draw.text(((qr_width - text_width) // 2, qr_height + text_padding), camper.name, fill="black", font=font)
        final_img.save(path)

        return redirect(url_for('main.index'))

    return render_template('add_camper.html')


@main.route('/edit_camper/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_camper(id):
    camper = Camper.query.get_or_404(id)

    # Allow if admin or if user's team matches
    if current_user.role != 'admin' and camper.team_number != current_user.team_number:
        abort(403)

    if request.method == 'POST':
        if current_user.role == 'counselor':
            # Counselors can only update diet and notes
            camper.diet = request.form['diet']
            camper.notes = request.form['notes']
        else:
            # Admins and team_leaders can update all fields
            camper.name = request.form['name']
            camper.disability = request.form['disability']
            camper.medications = request.form['medications']
            camper.diet = request.form['diet']
            camper.notes = request.form['notes']
            camper.team_number = request.form.get('team_number', camper.team_number)

        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_camper.html', camper=camper)


@main.route('/qrcode/<string:token>')
def qrcode_image(token):
    return send_from_directory('static/qrcodes', f'{token}.png')


@main.route('/delete_camper/<int:id>', methods=['POST'])
@login_required
def delete_camper(id):
    camper = Camper.query.get_or_404(id)

    if current_user.role not in ['admin', 'team_leader'] or camper.team_number != current_user.team_number:
        abort(403)

    # Delete QR code if exists
    qr_path = os.path.join(current_app.root_path, 'static', 'qrcodes', f'{camper.qr_token}.png')
    try:
        os.remove(qr_path)
    except FileNotFoundError:
        pass

    db.session.delete(camper)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/nametag/<token>')
def camper_nametag(token):
    camper = Camper.query.filter_by(qr_token=token).first_or_404()
    return render_template('nametag.html', camper=camper)

