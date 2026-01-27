from flask import Blueprint, request, jsonify
from ..extensions import mongo
from bson.objectid import ObjectId
import datetime
import requests # Per chiamare NotificationService

ticket_bp = Blueprint('tickets', __name__)

@ticket_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "TicketService running"}), 200

@ticket_bp.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'message': 'Dati invalidi'}), 400
    
    ticket_doc = {
        'title': data.get('title'),
        'description': data.get('description'),
        'category': data.get('category'),
        'status': 'received',
        'location': data.get('location'), # {type: Point, coordinates: [lng, lat]}
        'author_id': data.get('userId'),
        'tenant_id': data.get('municipalityId'),
        'photos': [],
        'comments': [],
        'created_at': datetime.datetime.utcnow(),
        'updated_at': datetime.datetime.utcnow()
    }
    
    res = mongo.db.tickets.insert_one(ticket_doc)
    return jsonify({'message': 'Ticket creato', 'id': str(res.inserted_id)}), 201

@ticket_bp.route('/tickets', methods=['GET'])
def get_tickets():
    query = {}
    if request.args.get('status'): query['status'] = request.args.get('status')
    if request.args.get('municipalityId'): query['tenant_id'] = request.args.get('municipalityId')
    if request.args.get('assignedOperatorId'): query['operator_id'] = request.args.get('assignedOperatorId')

    tickets = []
    for doc in mongo.db.tickets.find(query).sort('created_at', -1):
        doc['id'] = str(doc['_id'])
        del doc['_id']
        # La conversione date è gestita dall'Encoder in app.py o qui manualmente
        if doc.get('created_at'): doc['created_at'] = doc['created_at'].isoformat() + 'Z'
        tickets.append(doc)
        
    return jsonify(tickets), 200

@ticket_bp.route('/tickets/<ticket_id>/assign', methods=['POST'])
def assign_ticket(ticket_id):
    data = request.get_json()
    operator_id = data.get('operatorId')
    
    result = mongo.db.tickets.update_one(
        {'_id': ObjectId(ticket_id)},
        {'$set': {
            'status': 'in_progress', 
            'operator_id': operator_id, 
            'updated_at': datetime.datetime.utcnow()
        }}
    )
    
    if result.modified_count > 0:
        # Esempio chiamata inter-service (opzionale)
        # requests.post('http://notification-service:5005/send', json={...})
        return jsonify({'message': 'Ticket assegnato'}), 200
    
    return jsonify({'message': 'Ticket non trovato'}), 404