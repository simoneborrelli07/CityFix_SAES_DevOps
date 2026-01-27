from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson.objectid import ObjectId
from ..extensions import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "AuthService running"}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Dati mancanti'}), 400

    user = mongo.db.users.find_one({'email': data.get('email')})

    if user and check_password_hash(user['password_hash'], data.get('password')):
        token = jwt.encode({
            'user_id': str(user['_id']),
            'role': user.get('role', 'citizen'),
            'tenant_id': user.get('tenant_id'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            'token': token, 
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'role': user.get('role', 'citizen'),
                'municipalityId': user.get('tenant_id')
            }
        })
    
    return jsonify({'message': 'Credenziali non valide'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'Email già in uso'}), 400
        
    hashed_pw = generate_password_hash(data['password'])
    
    user_id = mongo.db.users.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password_hash': hashed_pw,
        'role': 'citizen', 
        'tenant_id': data.get('municipalityId', '1'),
        'created_at': datetime.datetime.utcnow()
    }).inserted_id
    
    return jsonify({'message': 'Utente creato', 'id': str(user_id)}), 201