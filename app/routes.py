
from flask import Blueprint, render_template, redirect, url_for, request, send_from_directory, current_app
from flask_login import login_required, current_user, login_user, logout_user
from .models import Camper, User
import os, secrets, qrcode
from PIL import Image, ImageDraw, ImageFont
from . import db

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
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
    if current_user.team_number:
        campers = Camper.query.filter_by(team_number=current_user.team_number).all()
    else:
        campers = Camper.query.all()  # Admins or unassigned users
    return render_template('index.html', campers=campers)

@main.route('/camper/<string:token>')
@login_required
def camper_detail(token):
    camper = Camper.query.filter_by(qr_token=token).first_or_404()

    if current_user.team_number is not None and camper.team_number != current_user.team_number:
        return "Unauthorized access", 403

    return render_template('camper_detail.html', camper=camper)

@main.route('/add_camper', methods=['GET', 'POST'])
@login_required
def add_camper():
    if request.method == 'GET':
        return render_template('add_camper.html')

    name = request.form['name']
    disability = request.form['disability']
    medications = request.form['medications']
    diet = request.form['diet']
    notes = request.form['notes']
    qr_token = secrets.token_urlsafe(8)

    camper = Camper(name=name, disability=disability, medications=medications, diet=diet, notes=notes, qr_token=qr_token)
    db.session.add(camper)
    db.session.commit()

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

@main.route('/edit_camper/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_camper(id):
    camper = Camper.query.get_or_404(id)
    if request.method == 'POST':
        camper.name = request.form['name']
        camper.disability = request.form['disability']
        camper.medications = request.form['medications']
        camper.diet = request.form['diet']
        camper.notes = request.form['notes']
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

    # Remove associated QR code image
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

