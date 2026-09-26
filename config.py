import os
from datetime import timedelta
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Carga las variables del archivo .env (solo tiene efecto en desarrollo local;
# en Vercel las variables se configuran desde el dashboard y esto no molesta)
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CAMBIA-ESTO-POR-UNA-CLAVE-SUPER-SEGURA-123456'
    
    # Base de datos - Supabase (PostgreSQL)
    # La URL completa se configura como variable de entorno DATABASE_URL.
    # Formato esperado (Transaction Pooler, puerto 6543):
    # postgresql+psycopg2://postgres.xxxxx:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql+psycopg2://postgres:password@localhost:5432/sistema_votacion'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Importante para serverless (Vercel): usamos NullPool porque Supabase
    # (Transaction Pooler) ya se encarga del pooling de conexiones. Si Flask
    # además mantiene su propio pool, se generan conexiones "zombies" y
    # errores intermitentes en funciones serverless de corta duración.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool,
        'pool_pre_ping': True,
    }
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)