from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from rembg import remove, new_session
session = new_session("u2netp")
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# ---- Database Setup ----
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'change-this-secret-key-later'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ---- User Table (Database Model) ----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# ---- Test Route ----
@app.route('/')
def home():
    return "Backend chal raha hai!"

# ---- Background Remove Route (purana wala, waise hi hai) ----
@app.route('/remove-bg', methods=['POST'])
def remove_background():
    file = request.files['image']
    input_image = Image.open(file.stream)
    output_image = remove(input_image)

    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

# ---- Signup Route ----
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Ye email already registered hai"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful!"}), 201

# ---- Login Route ----
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Email ya password galat hai"}), 401

    access_token = create_access_token(identity=email)
    return jsonify({"message": "Login successful!", "token": access_token}), 200

if __name__ == '__main__':
import os
port = int(os.environ.get("PORT", 5000))
app.run(debug=True, host="0.0.0.0", port=port, threaded=True)