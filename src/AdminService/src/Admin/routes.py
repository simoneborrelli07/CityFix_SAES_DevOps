from flask import Blueprint, jsonify
from ..db_config import mongo

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats/global', methods=['GET'])
def global_stats():
    # Aggregation Pipeline
    pipeline = [
        {"$group": {"_id": "$tenant_id", "count": {"$sum": 1}}}
    ]
    results = list(mongo.db.tickets.aggregate(pipeline))
    return jsonify(results), 200

@admin_bp.route('/municipalities', methods=['POST'])
def add_municipality():
    # Logica per aggiungere un nuovo comune (GeoJSON)
    pass