# ================================
# models.py - Modelos de Base de Datos
# ================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Administrador(UserMixin, db.Model):
    __tablename__ = 'administradores'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.usuario}>'

class Stand(db.Model):
    __tablename__ = 'stands'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_qr = db.Column(db.String(10), unique=True, nullable=False, index=True)  # ej: A7K9X2
    nombre_proyecto = db.Column(db.String(200), nullable=False)
    profesor_cargo = db.Column(db.String(150), nullable=False)
    materia = db.Column(db.String(150), nullable=False)
    curso = db.Column(db.String(20), nullable=False)  # "1°A", "5°U"
    alumnos = db.Column(db.Text, nullable=False)  # Lista de nombres separados por coma
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con votos
    votos = db.relationship('Voto', backref='stand', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_votos(self):
        return self.votos.count()
    
    def __repr__(self):
        return f'<Stand {self.nombre_proyecto} ({self.codigo_qr})>'

class Voto(db.Model):
    __tablename__ = 'votos'
    
    id = db.Column(db.Integer, primary_key=True)
    stand_id = db.Column(db.Integer, db.ForeignKey('stands.id'), nullable=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=False)
    hash_voto = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Voto {self.id} -> Stand {self.stand_id}>'

class Configuracion(db.Model):
    """Tabla de una sola fila para guardar ajustes globales del sistema,
    como si la votación está abierta o cerrada."""
    __tablename__ = 'configuracion'

    id = db.Column(db.Integer, primary_key=True)
    votacion_abierta = db.Column(db.Boolean, default=True, nullable=False)

    @staticmethod
    def obtener():
        """Devuelve la fila de configuración (id=1), creándola si no existe"""
        config = Configuracion.query.get(1)
        if not config:
            config = Configuracion(id=1, votacion_abierta=True)
            db.session.add(config)
            db.session.commit()
        return config