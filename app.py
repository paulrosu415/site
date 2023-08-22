from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os

from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get_users', methods=['GET'])
def get_users():
    users = mongo.db.users.find({}, {'username': 1})
    user_list = [user['username'] for user in users]
    return jsonify(user_list)

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user1 = request.args.get('user1')
    user2 = request.args.get('user2')
    messages = mongo.db.messages.find({
        '$or': [
            {'from_user': user1, 'to_user': user2},
            {'from_user': user2, 'to_user': user1}
        ]
    })
    message_list = [{'from_user': msg['from_user'], 'text': msg['text']} for msg in messages]
    return jsonify(message_list)

@app.route('/send_message', methods=['POST'])
def send_message():
    from_user = request.json.get('from_user')
    to_user = request.json.get('to_user')
    text = request.json.get('text')

    message = {
        'from_user': from_user,
        'to_user': to_user,
        'text': text
    }

    mongo.db.messages.insert_one(message)
    return jsonify({'message': 'Message sent successfully'})

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Funcția logica pentru achiziționarea abonamentelor
def buy_membership(user_id, membership_type):
    membership_prices = {
        'basic': 9.99,
        'premium': 19.99,
        'vip': 29.99
    }
    
    users_collection = mongo.db.users
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    
    if user:
        required_diamonds = membership_prices.get(membership_type, 0)
        if user['available_diamonds'] >= required_diamonds:
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$inc': {'available_diamonds': -required_diamonds}}
            )
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'membership': membership_type}}
            )
            return True
    return False

@app.route('/complete_profile')
@jwt_required()
def complete_profile():
    return render_template('profile.html', user=get_jwt_identity())

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    users_collection = mongo.db.users
    existing_user = users_collection.find_one({'email': data['email']})

    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'age': data['age'],
        'eye_color': data['eye_color'],
        'height': data['height'],
        'weight': data['weight'],
        'photo_url': data['photo_url'],
        'vices': data['vices'],
        'hobbies': data['hobbies']
    }

    users_collection.insert_one(new_user)
    return jsonify({'message': 'User registered successfully!'})

@app.route('/save_profile', methods=['POST'])
@jwt_required()
def save_profile():
    data = request.form
    user_id = data['user_id']
    users_collection = mongo.db.users

    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'age': data['age'],
                        'eye_color': data['eye_color'],
                        'height': data['height'],
                        'weight': data['weight'],
                        'photo_url': photo_path,
                        'vices': data['vices'],
                        'hobbies': data['hobbies']
                    }
                }
            )
    return "Profilul a fost salvat cu succes!"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    users_collection = mongo.db.users
    user = users_collection.find_one({'email': data['email']})

    if user and bcrypt.check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({'access_token': access_token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    users_collection = mongo.db.users
    user = users_collection.find_one({'_id': ObjectId(current_user)})
    return jsonify({'message': f'Hello, user {user["username"]}'})

if __name__ == '__main__':
    app.run(debug=True)
