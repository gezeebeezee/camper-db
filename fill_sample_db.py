import requests
import random
import secrets
import os
from flask import url_for
from PIL import Image, ImageDraw, ImageFont
import qrcode

from app import create_app, db
from app.models import Camper
from flask import current_app

app = create_app()
with app.app_context():
    if Camper.query.first() is None:
        pokemon_data = {}
        pokemon_diets = ['Berries', 'Pokeblock candy', 'Poffin', 'Aprijuice', 'Poke puffs', 'Poke beans', 'Curry', 'Sandwiches']
        pokemon_notes = [
            "Eats berries before breakfast every day.",
            "Gets along well with water-type campers.",
            "Still learning to control their thunder shock.",
            "Sleeps best when it's raining outside.",
            "Likes to battle, but hates to lose.",
            "Has an unusual fear of Poké Balls.",
            "Collects shiny rocks during free time.",
            "Always volunteers for group activities.",
            "Frequently seen training at sunrise.",
            "Sneezes cause minor flame bursts—be cautious.",
            "Very protective of their teammates.",
            "Prefers solitude but opens up with snacks.",
            "Has a strong bond with their trainer.",
            "Needs help remembering sunscreen before outdoor time.",
            "Fascinated by flying types—wants to learn to fly.",
            "Sometimes hides under the table during meals.",
            "Has mastered the art of stealth naps.",
            "Knows all the lyrics to the Pokérap.",
            "Likes to hum the Pokémon Center theme.",
            "Carries around a lucky Pokédoll everywhere.",
        ]

        request = requests.get("https://pokeapi.co/api/v2/pokemon?limit=50&offset=0").json()
        pokemon = request['results']

        for i in pokemon:
            pokemon_name = i['name'].capitalize()
            pokemon_url = i['url']
            pokemon_json = requests.get(f'{pokemon_url}').json()
            pokemon_type = pokemon_json['types'][0]['type']['name'].capitalize()

            pokemon_data[pokemon_name] = pokemon_type


        base_url = os.getenv("PUBLIC_BASE_URL") or os.getend("SAMPLE_DB_HOST")
        qr_folder = os.path.join(current_app.root_path, 'static', 'qrcodes')
        os.makedirs(qr_folder, exist_ok=True)

        count = 1
        for name in pokemon_data:
            qr_token = secrets.token_urlsafe(8)
            team_number = 12 if count % 12 == 0 else count % 12

            camper = Camper(
                name=name,
                team_number=team_number,
                disability=pokemon_data.get(name),
                medications="None",
                diet=random.choice(pokemon_diets),
                notes=random.choice(pokemon_notes),
                qr_token=qr_token
            )
            db.session.add(camper)
            db.session.flush()  # ensure camper.qr_token is set for url_for

            # Generate QR code URL
            qr_url = f"{base_url}/camper/{qr_token}"
            qr_img = qrcode.make(qr_url).convert("RGB")
            qr_width, qr_height = qr_img.size

            # Load font
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()

            # Measure text height/width
            dummy_img = Image.new("RGB", (qr_width, 1))
            draw_dummy = ImageDraw.Draw(dummy_img)
            bbox = draw_dummy.textbbox((0, 0), name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Final image size and composition
            text_padding = 12
            bottom_padding = 55
            total_height = qr_height + text_padding + text_height + bottom_padding
            final_img = Image.new("RGB", (qr_width, total_height), "white")
            draw = ImageDraw.Draw(final_img)
            final_img.paste(qr_img, (0, 0))
            draw.text(((qr_width - text_width) // 2, qr_height + text_padding), name, fill="black", font=font)

            # Save QR code
            qr_path = os.path.join(qr_folder, f"{qr_token}.png")
            final_img.save(qr_path)

            count += 1

        db.session.commit()
        print("Sample database filled with styled QR codes.")
        
    else:
        print("Database already filled.")
