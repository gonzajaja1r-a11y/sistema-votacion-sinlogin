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

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_proyecto = db.Column(db.String(200), nullable=False)
    curso = db.Column(db.String(20), nullable=False)  # "1°A", "5°U"
    ciclo = db.Column(db.String(30))  # "Ciclo Básico" o "Ciclo Superior"
    materia = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))  # "Robótica", "Programación", etc.
    integrantes = db.Column(db.Text, nullable=False)  # Lista de nombres separados por coma
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con votos
    votos = db.relationship('Voto', backref='proyecto', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_votos(self):
        return self.votos.count()
    
    def __repr__(self):
        return f'<Proyecto {self.nombre_proyecto}>'

class Voto(db.Model):
    __tablename__ = 'votos'
    
    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=False)
    hash_voto = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Voto {self.id} -> Proyecto {self.proyecto_id}>'