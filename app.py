from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Administrador, Proyecto, Voto  # ← CAMBIO AQUÍ
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
    ip_headers = [
        'X-Real-IP',
        'X-Forwarded-For',
        'CF-Connecting-IP',
        'True-Client-IP',
        'X-Client-IP'
    ]
    
    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            ip = ip.split(',')[0].strip()
            if not ip.startswith(('10.', '172.16.', '192.168.', '127.')):
                print(f"🌐 IP detectada desde {header}: {ip}")
                return ip
    
    ip = request.remote_addr
    print(f"⚠️ IP desde remote_addr: {ip}")
    return ip

# ================================
# RUTAS PRINCIPALES - VOTACIÓN PÚBLICA
# ================================
@app.route('/verificar-voto', methods=['POST'])
def verificar_voto():
    """Verificar si el usuario ya votó antes de mostrar proyectos"""
    try:
        data = request.get_json()
        user_agent = data.get('user_agent')
        device_id = data.get('device_id', '')
        ip = obtener_ip_real(request)
        
        print(f"\n🔍 DEBUG VERIFICAR VOTO:")
        print(f"   IP Real: {ip}")
        print(f"   User-Agent: {user_agent[:50] if user_agent else 'N/A'}...")
        print(f"   Device ID: {device_id}")
        
        if not user_agent:
            return jsonify({'puede_votar': True})
        
        hash_voto = generar_hash_voto(ip, user_agent, device_id)
        print(f"   Hash generado: {hash_voto[:16]}...")
        
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
    # Obtener filtros
    categoria_filtro = request.args.get('categoria', 'todas')
    curso_filtro = request.args.get('curso', 'todos')
    
    # Query base
    query = Proyecto.query.filter_by(activo=True)
    
    # Aplicar filtros
    if categoria_filtro != 'todas':
        query = query.filter_by(categoria=categoria_filtro)
    if curso_filtro != 'todos':
        query = query.filter_by(curso=curso_filtro)
    
    proyectos = query.all()
    
    # Obtener listas para filtros
    categorias = db.session.query(Proyecto.categoria).filter_by(activo=True).distinct().all()
    categorias = [c[0] for c in categorias if c[0]]
    
    cursos = db.session.query(Proyecto.curso).filter_by(activo=True).distinct().all()
    cursos = sorted([c[0] for c in cursos if c[0]])
    
    return render_template('votacion_publica.html', 
                         proyectos=proyectos,
                         categorias=categorias,
                         cursos=cursos,
                         categoria_filtro=categoria_filtro,
                         curso_filtro=curso_filtro)

@app.route('/votar-publico', methods=['POST'])
def votar_publico():
    """Registrar voto público sin autenticación"""
    try:
        data = request.get_json()
        
        proyecto_id = data.get('proyecto_id')  # ← CAMBIO AQUÍ
        user_agent = data.get('user_agent')
        device_id = data.get('device_id', '')
        ip = obtener_ip_real(request)
        
        print(f"\n🗳️ DEBUG VOTAR:")
        print(f"   IP Real: {ip}")
        print(f"   User-Agent: {user_agent[:50] if user_agent else 'N/A'}...")
        print(f"   Device ID: {device_id}")
        print(f"   Proyecto: {proyecto_id}")
        
        if not proyecto_id or not user_agent:
            return jsonify({
                'success': False,
                'mensaje': 'Datos incompletos'
            }), 400
        
        # Verificar que el proyecto existe
        proyecto = Proyecto.query.get(proyecto_id)  # ← CAMBIO AQUÍ
        if not proyecto or not proyecto.activo:
            return jsonify({
                'success': False,
                'mensaje': 'Proyecto no válido'
            }), 400
        
        hash_voto = generar_hash_voto(ip, user_agent, device_id)
        print(f"   Hash generado: {hash_voto[:16]}...")
        
        voto_existente = Voto.query.filter_by(hash_voto=hash_voto).first()
        
        if voto_existente:
            print(f"   ⚠️ Voto duplicado detectado!")
            return jsonify({
                'success': False,
                'mensaje': 'Ya has votado en esta elección'
            }), 400
        
        nuevo_voto = Voto(
            proyecto_id=int(proyecto_id),  # ← CAMBIO AQUÍ
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
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class AdminLoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class ProyectoForm(FlaskForm):
    nombre_proyecto = StringField('Nombre del Proyecto', validators=[DataRequired()])
    curso = StringField('Curso', validators=[DataRequired()])
    ciclo = SelectField('Ciclo', choices=[
        ('', 'Seleccionar...'),
        ('Ciclo Básico', 'Ciclo Básico'),
        ('Ciclo Superior', 'Ciclo Superior')
    ])
    materia = StringField('Materia', validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('', 'Seleccionar...'),
        ('Robótica', '🤖 Robótica'),
        ('Programación', '💻 Programación'),
        ('Hardware', '🔧 Hardware'),
        ('Procedimientos Técnicos', '🪵 Procedimientos Técnicos'),
        ('Arte', '🎨 Arte'),
        ('Literatura', '📚 Literatura'),
        ('Ciencias Sociales', '🌍 Ciencias Sociales'),
        ('Matemática', '🧮 Matemática'),
        ('Catequesis', '✝️ Catequesis'),
        ('Otros', '📌 Otros')
    ])
    integrantes = TextAreaField('Integrantes (separados por coma)', validators=[DataRequired()])
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
    
    total_proyectos = Proyecto.query.filter_by(activo=True).count()
    total_votos = Voto.query.count()
    
    proyectos_raw = db.session.query(
        Proyecto.id, 
        Proyecto.nombre_proyecto, 
        Proyecto.curso,
        Proyecto.materia,
        Proyecto.categoria,
        db.func.count(Voto.id).label('votos')
    ).outerjoin(Voto).group_by(Proyecto.id).filter(Proyecto.activo==True).order_by(db.func.count(Voto.id).desc()).all()
    
    proyectos = []
    for p in proyectos_raw:
        proyectos.append({
            'id': p[0],
            'nombre_proyecto': p[1],
            'curso': p[2],
            'materia': p[3],
            'categoria': p[4],
            'votos': p[5]
        })
    
    return render_template('admin/dashboard.html', 
                         total_proyectos=total_proyectos,
                         total_votos=total_votos,
                         proyectos=proyectos)

@admin_bp.route('/proyectos', methods=['GET', 'POST'])
@login_required
def proyectos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))
    
    form = ProyectoForm()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'agregar' and form.validate_on_submit():
            proyecto = Proyecto(
                nombre_proyecto=form.nombre_proyecto.data,
                curso=form.curso.data,
                ciclo=form.ciclo.data,
                materia=form.materia.data,
                categoria=form.categoria.data,
                integrantes=form.integrantes.data,
                descripcion=form.descripcion.data
            )
            
            try:
                db.session.add(proyecto)
                db.session.commit()
                flash('Proyecto agregado exitosamente.', 'success')
                return redirect(url_for('admin.proyectos'))
            except Exception as e:
                db.session.rollback()
                flash('Error al agregar proyecto', 'error')
        
        elif action == 'eliminar':
            proyecto_id = request.form.get('proyecto_id')
            proyecto = Proyecto.query.get(proyecto_id)
            
            if proyecto:
                if proyecto.votos.count() > 0:
                    flash('No se puede eliminar un proyecto que ya tiene votos', 'error')
                else:
                    try:
                        db.session.delete(proyecto)
                        db.session.commit()
                        flash('Proyecto eliminado exitosamente.', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash('Error al eliminar proyecto', 'error')
    
    proyectos_lista = db.session.query(
        Proyecto, db.func.count(Voto.id).label('total_votos')
    ).outerjoin(Voto).group_by(Proyecto.id).filter(Proyecto.activo==True).all()
    
    return render_template('admin/proyectos.html', form=form, proyectos=proyectos_lista)

@admin_bp.route('/votos')
@login_required
def votos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))
    
    votos_lista = db.session.query(
        Voto, Proyecto.nombre_proyecto, Proyecto.curso
    ).join(Proyecto).order_by(Voto.fecha_voto.desc()).all()
    
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
    # Comentar esto en producción
    #init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)