import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-aqui'
    
    # Configuración para MySQL con XAMPP
    # Usuario: root (por defecto en XAMPP)
    # Contraseña: vacía (por defecto en XAMPP)
    # Host: localhost
    # Puerto: 3306 (por defecto)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/sistema_votacion'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)