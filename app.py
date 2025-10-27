from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Administrador, Candidato, Voto
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

@login_manager.user_loader
def load_user(user_id):
    """Cargar administrador"""
    return Administrador.query.get(int(user_id))

def is_admin():
    """Helper para verificar si el usuario actual es admin"""
    return current_user.is_authenticated and isinstance(current_user, Administrador)

# ================================
# FUNCIONES AUXILIARES
# ================================

def generar_hash_voto(ip, user_agent, device_id=''):
    """Generar hash único con IP + User-Agent + Device ID"""
    datos = f"{ip}|{user_agent}|{device_id}"
    hash_obj = hashlib.sha256(datos.encode('utf-8'))
    return hash_obj.hexdigest()

def obtener_ip_real(request):
    """Obtener la IP real del cliente considerando proxies"""
    # Lista de headers donde puede estar la IP real
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',
        'X-Client-IP'
    ]
    
    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For puede tener múltiples IPs separadas por coma
            # La primera es la del cliente original
            return ip.split(',')[0].strip()
    
    # Si no hay headers, usar remote_addr
    return request.remote_addr
# ================================
# RUTAS PRINCIPALES - VOTACIÓN PÚBLICA
# ================================
@app.route('/verificar-voto', methods=['POST'])
def verificar_voto():
    """Verificar si el usuario ya votó antes de mostrar candidatos"""
    try:
        data = request.get_json()
        user_agent = data.get('user_agent')
        device_id = data.get('device_id', '')
        ip = obtener_ip_real(request)  # ← CAMBIO AQUÍ
        
        print(f"\n🔍 DEBUG VERIFICAR VOTO:")
        print(f"   IP Real: {ip}")
        print(f"   User-Agent: {user_agent[:50] if user_agent else 'N/A'}...")
        print(f"   Device ID: {device_id}")
        
        if not user_agent:
            return jsonify({'puede_votar': True})
        
        # Generar hash
        hash_voto = generar_hash_voto(ip, user_agent, device_id)
        print(f"   Hash generado: {hash_voto[:16]}...")
        
        # Verificar si existe
        voto_existente = Voto.query.filter_by(hash_voto=hash_voto).first()
        print(f"   ¿Existe en BD? {voto_existente is not None}")
        
        return jsonify({
            'puede_votar': voto_existente is None
        })
        
    except Exception as e:
        print(f"❌ Error verificando voto: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'puede_votar': True})

@app.route('/')
def index():
    """Redirigir a votación pública"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('votacion_publica'))

@app.route('/votacion-publica')
def votacion_publica():
    """Página de votación pública sin login"""
    candidatos = Candidato.query.filter_by(activo=True).all()
    return render_template('votacion_publica.html', candidatos=candidatos)

@app.route('/votar-publico', methods=['POST'])
def votar_publico():
    """Registrar voto público sin autenticación"""
    try:
        data = request.get_json()
        
        candidato_id = data.get('candidato_id')
        user_agent = data.get('user_agent')
        device_id = data.get('device_id', '')
        ip = obtener_ip_real(request)  # ← CAMBIO AQUÍ
        
        print(f"\n🗳️ DEBUG VOTAR:")
        print(f"   IP Real: {ip}")
        print(f"   User-Agent: {user_agent[:50] if user_agent else 'N/A'}...")
        print(f"   Device ID: {device_id}")
        print(f"   Candidato: {candidato_id}")
        
        # Validar datos
        if not candidato_id or not user_agent:
            return jsonify({
                'success': False,
                'mensaje': 'Datos incompletos'
            }), 400
        
        # Verificar que el candidato existe
        candidato = Candidato.query.get(candidato_id)
        if not candidato or not candidato.activo:
            return jsonify({
                'success': False,
                'mensaje': 'Candidato no válido'
            }), 400
        
        # Generar hash único
        hash_voto = generar_hash_voto(ip, user_agent, device_id)
        print(f"   Hash generado: {hash_voto[:16]}...")
        
        # Verificar si ya existe
        voto_existente = Voto.query.filter_by(hash_voto=hash_voto).first()
        
        if voto_existente:
            print(f"   ⚠️ Voto duplicado detectado!")
            return jsonify({
                'success': False,
                'mensaje': 'Ya has votado en esta elección'
            }), 400
        
        # Crear y guardar voto
        nuevo_voto = Voto(
            candidato_id=int(candidato_id),
            ip_address=ip,
            user_agent=user_agent,
            hash_voto=hash_voto
        )
        
        db.session.add(nuevo_voto)
        db.session.commit()
        
        print(f"   ✅ Voto registrado exitosamente! ID={nuevo_voto.id}")
        
        return jsonify({
            'success': True,
            'mensaje': '¡Voto registrado exitosamente!'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al registrar voto: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'mensaje': 'Error al registrar el voto'
        }), 500

@app.route('/gracias')
def gracias():
    """Página de agradecimiento después de votar"""
    return render_template('gracias.html')

# ================================
# RUTAS DE ADMINISTRADOR
# ================================
from flask import Blueprint
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

# Formularios simples inline (ya no usamos forms.py)
class AdminLoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class CandidatoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    partido = StringField('Partido Político', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and is_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Administrador.query.filter_by(usuario=form.usuario.data).first()
        if admin and admin.check_password(form.password.data):
            session.clear()
            login_user(admin, remember=True)
            session.permanent = True
            return redirect(url_for('admin.dashboard'))
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))
    
    # Estadísticas
    total_candidatos = Candidato.query.filter_by(activo=True).count()
    total_votos = Voto.query.count()
    
    # Resultados por candidato - CAMBIA ESTA PARTE
    candidatos_raw = db.session.query(
        Candidato.id, 
        Candidato.nombre, 
        Candidato.apellido, 
        Candidato.partido, 
        db.func.count(Voto.id).label('votos')
    ).outerjoin(Voto).group_by(Candidato.id).filter(Candidato.activo==True).all()
    
    # Convertir a lista de diccionarios para facilitar acceso en template
    candidatos = []
    for c in candidatos_raw:
        candidatos.append({
            'id': c[0],
            'nombre': c[1],
            'apellido': c[2],
            'partido': c[3],
            'votos': c[4]
        })
    
    return render_template('admin/dashboard.html', 
                         total_candidatos=total_candidatos,
                         total_votos=total_votos,
                         candidatos=candidatos)

@admin_bp.route('/candidatos', methods=['GET', 'POST'])
@login_required
def candidatos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))
    
    form = CandidatoForm()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'agregar' and form.validate_on_submit():
            candidato = Candidato(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                partido=form.partido.data,
                descripcion=form.descripcion.data
            )
            
            try:
                db.session.add(candidato)
                db.session.commit()
                flash('Candidato agregado exitosamente.', 'success')
                return redirect(url_for('admin.candidatos'))
            except Exception as e:
                db.session.rollback()
                flash('Error al agregar candidato', 'error')
        
        elif action == 'eliminar':
            candidato_id = request.form.get('candidato_id')
            candidato = Candidato.query.get(candidato_id)
            
            if candidato:
                if candidato.votos.count() > 0:
                    flash('No se puede eliminar un candidato que ya tiene votos', 'error')
                else:
                    try:
                        db.session.delete(candidato)
                        db.session.commit()
                        flash('Candidato eliminado exitosamente.', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash('Error al eliminar candidato', 'error')
    
    # Obtener todos los candidatos con conteo de votos
    candidatos = db.session.query(
        Candidato, db.func.count(Voto.id).label('total_votos')
    ).outerjoin(Voto).group_by(Candidato.id).filter(Candidato.activo==True).all()
    
    return render_template('admin/candidatos.html', form=form, candidatos=candidatos)

@admin_bp.route('/votos')
@login_required
def votos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))
    
    # Obtener todos los votos con información del candidato
    votos_lista = db.session.query(
        Voto, Candidato.nombre, Candidato.apellido
    ).join(Candidato).order_by(Voto.fecha_voto.desc()).all()
    
    total_votos = Voto.query.count()
    
    return render_template('admin/votos.html', 
                         votos=votos_lista,
                         total_votos=total_votos)

@admin_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('admin.login'))

# Registrar blueprint
app.register_blueprint(admin_bp)

# ================================
# FUNCIONES DE INICIALIZACIÓN
# ================================

def create_admin():
    """Crear administrador por defecto"""
    if not Administrador.query.first():
        admin = Administrador(
            usuario='admin',
            nombre='Administrador'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Administrador creado - Usuario: admin, Contraseña: admin123")

def create_database():
    """Crear la base de datos si no existe"""
    import pymysql
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_votacion")
        print("✓ Base de datos 'sistema_votacion' verificada/creada")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

def init_db():
    """Inicializar la base de datos"""
    create_database()
    with app.app_context():
        print("Creando tablas en MySQL...")
        db.create_all()
        print("✓ Tablas creadas correctamente")
        create_admin()
        print("✓ Base de datos inicializada")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)