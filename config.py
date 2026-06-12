import os
from dotenv import load_dotenv

load_dotenv()

def _elegir_db() -> tuple[str, str]:
    """Devuelve (url, nombre). Intenta Supabase; cae a Aiven si no responde."""
    primary = os.getenv("DATABASE_URL", "")
    replica = os.getenv("DATABASE_URL_REPLICA", "")

    if not replica:
        print("[DB] DATABASE_URL_REPLICA no configurada — usando primaria")
        return primary, "SUPABASE"

    try:
        import psycopg2
        conn = psycopg2.connect(primary, connect_timeout=5)
        conn.close()
        print("[DB] Supabase activa — usando base principal")
        return primary, "SUPABASE"
    except Exception as ex:
        print(f"[DB] Supabase no disponible ({ex}) — usando réplica Aiven")
        return replica, "AIVEN"

_DB_URL, _DB_NOMBRE = _elegir_db()

class Config:
    SQLALCHEMY_DATABASE_URI = _DB_URL
    DB_ACTIVA = _DB_NOMBRE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    INSTANCE_NAME = os.getenv("INSTANCE_NAME", "RENDER-LOCAL")
    SOAP_URL = os.getenv("SOAP_URL", "http://localhost:8000/soap")
