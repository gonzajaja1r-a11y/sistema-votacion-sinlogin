"""
Script rápido para cambiar la contraseña de un administrador existente.
Uso: python cambiar_password_admin.py
"""

from app import app, db
from models import Administrador

# ============================================
# EDITÁ ESTOS 2 DATOS ANTES DE CORRER
# ============================================
USUARIO = 'admin2'
NUEVA_PASSWORD = 'Segovia123454!'

with app.app_context():
    admin = Administrador.query.filter_by(usuario=USUARIO).first()
    
    if not admin:
        print(f"❌ No se encontró el usuario '{USUARIO}'")
    else:
        admin.set_password(NUEVA_PASSWORD)
        db.session.commit()
        print(f"✅ Contraseña actualizada para el usuario '{USUARIO}'")
        print(f"   Nueva contraseña: {NUEVA_PASSWORD}")