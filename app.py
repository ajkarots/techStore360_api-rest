"""TechStore 360 - API REST (se despliega 2 veces: Render 1 y Render 2)."""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from auth import init_firebase
from routes.usuarios import usuarios_bp
from routes.productos import productos_bp
from routes.compras import compras_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # permite consumo desde React, Flutter web y portales
    db.init_app(app)
    init_firebase()

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(compras_bp)

    @app.get("/health")
    def health():
        """Usado por NGINX para detección de fallos (failover)."""
        return jsonify({"status": "ok", "instancia": app.config["INSTANCE_NAME"]})

    @app.get("/")
    def root():
        return jsonify({
            "servicio": "TechStore 360 API REST",
            "instancia": app.config["INSTANCE_NAME"],
            "endpoints": ["/api/usuarios", "/api/productos", "/api/compras", "/health"],
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
