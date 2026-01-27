import os
from flask import Blueprint, request, jsonify, send_from_directory

media_bp = Blueprint('media', __name__)
UPLOAD_FOLDER = '/app/uploads' # Percorso nel container

@media_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename # In prod: usa secure_filename e UUID
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    return jsonify({
        'url': f'/api/media/files/{filename}',
        'filename': filename
    }), 201

@media_bp.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)