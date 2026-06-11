import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    INSTANCE_NAME = os.getenv("INSTANCE_NAME", "RENDER-LOCAL")
    SOAP_URL = os.getenv("SOAP_URL", "http://localhost:8000/soap")
