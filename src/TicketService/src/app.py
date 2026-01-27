import os
import json
import datetime
from flask import Flask
from flask_cors import CORS
from bson import ObjectId
from .extensions import mongo
from .Tickets.routes import ticket_bp

# Helper per JSON
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId): return str(o)
        if isinstance(o, datetime.datetime): return o.isoformat() + 'Z'
        return json.JSONEncoder.default(self, o)

def create_app():
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    CORS(app)
    
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/cityfix")
    
    mongo.init_app(app)
    app.register_blueprint(ticket_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True)