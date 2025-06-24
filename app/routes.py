from flask import render_template, redirect, url_for, request, send_from_directory, current_app
from app import app, db
from app.models import Camper
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import secrets


@app.route('/')
def index():
    campers = Camper.query.all()
    return render_template('index.html', campers=campers)

@app.route('/camper/<string:token>')
def camper_detail(token):
    camper = Camper.query.filter_by(qr_token=token).first_or_404()
    return render_template('camper_detail.html', camper=camper)


@app.route('/add_camper', methods=['GET', 'POST'])
def add_camper():
    if request.method == 'GET':
        return render_template('add_camper.html')

    # POST method: get form data
    name = request.form['name']
    disability = request.form['disability']
    medications = request.form['medications']
    diet = request.form['diet']
    notes = request.form['notes']

    # Generate unique QR token
    qr_token = secrets.token_urlsafe(8)

    # Create camper with QR token
    camper = Camper(name=name, disability=disability, medications=medications, diet=diet, notes=notes, qr_token=qr_token)
    db.session.add(camper)
    db.session.commit()

    # Generate QR code URL for camper details
    # qr_url = request.url_root.rstrip('/') + url_for('camper_detail', token=qr_token)

    base_url = os.getenv("PUBLIC_BASE_URL")

    if not base_url:
        # Fallback to request.url_root (automatically includes http:// or https://)
        base_url = request.url_root.rstrip('/')

    qr_url = f"{base_url}{url_for('camper_detail', token=camper.qr_token)}"


    # Save QR code image to static/qrcodes folder
    path = os.path.join(current_app.root_path, 'static', 'qrcodes', f'{qr_token}.png')
    qr_img = qrcode.make(qr_url)
    # img.save(path)

    # Convert to RGB to allow pasting camper name
    qr_img = qr_img.convert("RGB")

    # Dimensions
    qr_width, qr_height = qr_img.size
    text = camper.name

    # Load a nicer font for camper name or fall back to default font
    try:
        font = ImageFont.truetype("arial.ttf", 20)

    except:
        font = ImageFont.load_default()

    # Get text size using textbox
    dummy_img = Image.new("RGB", (qr_width, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    bbox = draw_dummy.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Set spacing/padding
    top_padding = 0
    text_padding = 12
    bottom_padding = 55

    # Final image height
    total_height = qr_height + text_padding + text_height + bottom_padding

    # Create new blank image
    final_img = Image.new("RGB", (qr_width, total_height), "white")
    draw = ImageDraw.Draw(final_img)

    # Paste QR code
    final_img.paste(qr_img, (0, 0))

    # Draw text centered below QR
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + text_padding
    draw.text((text_x, text_y), text, fill="black", font=font)

    # Save final image
    final_img.save(path)


    return redirect(url_for('index'))


@app.route('/qrcode/<string:token>')
def qrcode_image(token):
    return send_from_directory('static/qrcodes', f'{token}.png')

@app.route('/edit_camper/<int:id>', methods=['GET', 'POST'])
def edit_camper(id):
    camper = Camper.query.get_or_404(id)
    if request.method == 'POST':
        camper.name = request.form['name']
        camper.disability = request.form['disability']
        camper.medications = request.form['medications']
        camper.diet = request.form['diet']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_camper.html', camper=camper)

@app.route('/delete_camper/<int:id>', methods=['POST'])
def delete_camper(id):
    camper = Camper.query.get_or_404(id)

    # Also remove QR code file
    qr_path = f'app/static/qrcodes/{camper.qr_token}.png'
    try:
        os.remove(qr_path)
    except FileNotFoundError:
        pass

    db.session.delete(camper)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/nametag/<token>')
def camper_nametag(token):
    camper = Camper.query.filter_by(qr_token=token).first_or_404()
    return render_template('nametag.html', camper=camper)
