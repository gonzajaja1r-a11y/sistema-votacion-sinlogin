from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Usuario, Administrador, Candidato, Voto
from forms import LoginForm, AdminLoginForm, CandidatoForm
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario basado en el tipo almacenado en sesión"""
    try:
        user_id = int(user_id)
        # Verificar si es admin basado en la sesión
        if session.get('user_type') == 'admin':
            admin = Administrador.query.get(user_id)
            if admin:
                return admin
        
        # Si no es admin, cargar como usuario normal
        user = Usuario.query.get(user_id)
        if user:
            return user
            
    except (ValueError, TypeError):
        pass
    return None

def is_admin():
    """Helper para verificar si el usuario actual es admin"""
    return current_user.is_authenticated and isinstance(current_user, Administrador)

# ================================
# RUTAS PRINCIPALES
# ================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('vote'))
    
    form = LoginForm()
    return render_template('index.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('vote'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        
        # Buscar usuario por email
        user = Usuario.query.filter_by(email=email).first()
        
        # Si no existe, crear nuevo usuario automáticamente
        if not user:
            user = Usuario(email=email)
            try:
                db.session.add(user)
                db.session.commit()
                flash('¡Bienvenido! Tu cuenta ha sido creada.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error al crear la cuenta. Intenta nuevamente.', 'error')
                return redirect(url_for('index'))
        
        # Limpiar cualquier sesión de admin previa
        session.pop('user_type', None)
        login_user(user, remember=True)
        session['user_type'] = 'usuario'
        return redirect(url_for('vote'))
    
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    # Verificar que no sea admin
    if is_admin():
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST' and not current_user.ha_votado:
        candidato_id = request.form.get('candidato_id')
        if candidato_id:
            try:
                # Crear voto
                voto = Voto(
                    usuario_id=current_user.id,
                    candidato_id=int(candidato_id),
                    ip_address=request.remote_addr
                )
                
                # Marcar usuario como votado
                current_user.ha_votado = True
                
                db.session.add(voto)
                db.session.commit()
                
                flash('¡Su voto ha sido registrado exitosamente!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error al registrar el voto.', 'error')
    
    candidatos = Candidato.query.filter_by(activo=True).all()
    return render_template('vote.html', candidatos=candidatos)

@app.route('/logout')
@login_required
def logout():
    # Limpiar completamente la sesión
    session.clear()
    logout_user()
    return redirect(url_for('index'))

# ================================
# RUTAS DE ADMINISTRADOR
# ================================
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Si hay un usuario común logueado, hacer logout primero
    if current_user.is_authenticated:
        logout_user()
        session.clear()
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Administrador.query.filter_by(usuario=form.usuario.data).first()
        if admin and admin.check_password(form.password.data):
            # Limpiar sesión y establecer tipo admin
            session.clear()
            login_user(admin, remember=True)
            session['user_type'] = 'admin'
            session.permanent = True
            return redirect(url_for('admin.dashboard'))
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    # Estadísticas
    total_usuarios = Usuario.query.count()
    total_candidatos = Candidato.query.filter_by(activo=True).count()
    total_votos = Voto.query.count()
    
    # Resultados por candidato
    candidatos = db.session.query(
        Candidato.id, Candidato.nombre, Candidato.apellido, 
        Candidato.partido, db.func.count(Voto.id).label('votos')
    ).outerjoin(Voto).group_by(Candidato.id).filter(Candidato.activo==True).all()
    
    participacion = round((total_votos / total_usuarios * 100), 1) if total_usuarios > 0 else 0
    
    return render_template('admin/dashboard.html', 
                         total_usuarios=total_usuarios,
                         total_candidatos=total_candidatos,
                         total_votos=total_votos,
                         participacion=participacion,
                         candidatos=candidatos)

@admin_bp.route('/candidatos', methods=['GET', 'POST'])
@login_required
def candidatos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
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

@admin_bp.route('/usuarios')
@login_required
def usuarios():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    # Filtros
    filtro_voto = request.args.get('voto', 'todos')
    busqueda = request.args.get('buscar', '')
    
    query = Usuario.query
    
    if filtro_voto == 'votaron':
        query = query.filter(Usuario.ha_votado == True)
    elif filtro_voto == 'no_votaron':
        query = query.filter(Usuario.ha_votado == False)
    
    if busqueda:
        query = query.filter(Usuario.email.contains(busqueda))
    
    usuarios = query.order_by(Usuario.fecha_registro.desc()).all()
    
    # Estadísticas
    total_usuarios = Usuario.query.count()
    usuarios_votaron = Usuario.query.filter_by(ha_votado=True).count()
    usuarios_no_votaron = total_usuarios - usuarios_votaron
    
    return render_template('admin/usuarios.html', 
                         usuarios=usuarios,
                         total_usuarios=total_usuarios,
                         usuarios_votaron=usuarios_votaron,
                         usuarios_no_votaron=usuarios_no_votaron,
                         filtro_voto=filtro_voto,
                         busqueda=busqueda)

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
    # Crear tablas e inicializar la BD
    init_db()
    app.run(debug=True)