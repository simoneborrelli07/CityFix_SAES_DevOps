from flask import Blueprint, request, jsonify
from ..db_config import mongo

geo_bp = Blueprint('geo', __name__)

@geo_bp.route('/validate', methods=['POST'])
def validate_location():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')

    point = { "type": "Point", "coordinates": [lng, lat] }

    # Query spaziale: Trova il comune che contiene il punto
    municipality = mongo.db.municipalities.find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    if municipality:
        return jsonify({
            "valid": True, 
            "tenant_id": str(municipality['_id']),
            "name": municipality['name']
        }), 200
    
    return jsonify({"valid": False, "message": "Zona non coperta"}), 404