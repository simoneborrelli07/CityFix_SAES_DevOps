from flask import Blueprint, request, jsonify

notif_bp = Blueprint('notifications', __name__)

@notif_bp.route('/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    recipient = data.get('recipient') # ID Utente o Email
    message = data.get('message')
    
    # Qui ci andrebbe la logica SMTP (es. Flask-Mail)
    print(f"[EMAIL MOCK] To: {recipient} | Body: {message}")
    
    return jsonify({"status": "sent"}), 200