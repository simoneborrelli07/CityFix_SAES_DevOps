import os
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from .Auth.routes import auth_bp
from .extensions import mongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configurazione da ENV o default locale
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/cityfix")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    
    mongo.init_app(app)
    
    # Passiamo l'istanza mongo al blueprint se necessario, o la importiamo globalmente
    # Qui usiamo il pattern di importare 'mongo' da questo file nelle routes
    
    app.register_blueprint(auth_bp)
    
    return app

# Questa variabile serve alle routes per importare 'mongo'
app_instance = create_app()

if __name__ == '__main__':
    app_instance.run(host='0.0.0.0', port=5001, debug=True)