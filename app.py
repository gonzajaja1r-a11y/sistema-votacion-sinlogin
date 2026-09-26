from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Administrador, Stand, Voto
from datetime import datetime
import hashlib
import random
import string
import os
import io
import json
import zipfile
import qrcode
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import openpyxl

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

def generar_hash_voto(ip, user_agent, codigo_stand):
    """Generar hash único con IP + User-Agent + código de stand.
    Esto permite votar una vez POR CADA stand (no una vez en toda la muestra)."""
    datos = f"{ip}|{user_agent}|{codigo_stand}"
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
                return ip
    return request.remote_addr

def generar_codigo_unico():
    """Genera un código alfanumérico único de 6 caracteres para el QR de un stand"""
    caracteres = string.ascii_uppercase + string.digits
    while True:
        codigo = ''.join(random.choices(caracteres, k=6))
        if not Stand.query.filter_by(codigo_qr=codigo).first():
            return codigo

def generar_imagen_qr(stand):
    """Genera la tarjeta QR (imagen PIL) de un stand: QR + nombre de proyecto
    destacado + profesor/curso, lista para mostrar o incluir en un PDF."""
    url_voto = url_for('votar_stand', codigo=stand.codigo_qr, _external=True)

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url_voto)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1a1a2e", back_color="white").convert('RGB')

    ancho = 640
    padding = 40
    qr_size = ancho - padding * 2
    qr_img = qr_img.resize((qr_size, qr_size))

    font_titulo = ImageFont.load_default(size=34)
    font_subtitulo = ImageFont.load_default(size=22)
    font_caption = ImageFont.load_default(size=16)

    def envolver_texto(draw, texto, font, max_width):
        palabras = texto.split()
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            prueba = (linea_actual + " " + palabra).strip()
            bbox = draw.textbbox((0, 0), prueba, font=font)
            if bbox[2] - bbox[0] <= max_width:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)
        return lineas[:2]

    dummy = Image.new('RGB', (10, 10))
    dummy_draw = ImageDraw.Draw(dummy)
    lineas_titulo = envolver_texto(dummy_draw, stand.nombre_proyecto, font_titulo, ancho - padding * 2)

    subtitulo = f"Prof. {stand.profesor_cargo} - {stand.curso}"

    alto_titulo = len(lineas_titulo) * 44
    alto_total = padding + 24 + qr_size + 20 + alto_titulo + 10 + 30 + padding

    canvas = Image.new('RGB', (ancho, alto_total), 'white')
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle([4, 4, ancho - 5, alto_total - 5], radius=24, outline=(102, 126, 234), width=4)

    y = padding
    caption = f"MUESTRA ANUAL ITEL {datetime.now().year}"
    bbox = draw.textbbox((0, 0), caption, font=font_caption)
    cw = bbox[2] - bbox[0]
    draw.text(((ancho - cw) / 2, y), caption, font=font_caption, fill=(102, 126, 234))
    y += 24

    x_qr = (ancho - qr_size) // 2
    canvas.paste(qr_img, (x_qr, y))
    y += qr_size + 20

    for linea in lineas_titulo:
        bbox = draw.textbbox((0, 0), linea, font=font_titulo)
        lw = bbox[2] - bbox[0]
        draw.text(((ancho - lw) / 2, y), linea, font=font_titulo, fill=(30, 30, 30))
        y += 44

    y += 10
    bbox = draw.textbbox((0, 0), subtitulo, font=font_subtitulo)
    sw = bbox[2] - bbox[0]
    draw.text(((ancho - sw) / 2, y), subtitulo, font=font_subtitulo, fill=(100, 100, 100))

    return canvas

def generar_pdf_bytes(stand):
    """Genera el PDF (bytes) con el QR del stand repetido 6 veces en grilla 2x3"""
    img = generar_imagen_qr(stand)
    img_buf = io.BytesIO()
    img.save(img_buf, format='PNG')

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    margen = 15
    gutter = 8
    cols, rows = 2, 3
    ancho_pagina = 210 - margen * 2
    alto_pagina = 297 - margen * 2
    cell_w = (ancho_pagina - gutter * (cols - 1)) / cols
    cell_h = (alto_pagina - gutter * (rows - 1)) / rows

    aspect = img.width / img.height
    if cell_w / cell_h > aspect:
        img_h = cell_h
        img_w = img_h * aspect
    else:
        img_w = cell_w
        img_h = img_w / aspect

    for r in range(rows):
        for c in range(cols):
            x = margen + c * (cell_w + gutter) + (cell_w - img_w) / 2
            y = margen + r * (cell_h + gutter) + (cell_h - img_h) / 2
            img_buf.seek(0)
            pdf.image(img_buf, x=x, y=y, w=img_w, h=img_h)

    return bytes(pdf.output())

# Columnas obligatorias que debe tener el Excel a importar
COLUMNAS_REQUERIDAS = ['nombre_proyecto', 'profesor', 'curso', 'materia', 'alumnos']

def leer_excel_stands(file_stream):
    """Lee un archivo .xlsx y devuelve (filas_validas, errores)"""
    wb = openpyxl.load_workbook(file_stream, read_only=True, data_only=True)
    ws = wb.active

    filas = list(ws.iter_rows(values_only=True))
    if not filas:
        return [], [{'fila': 0, 'motivo': 'El archivo está vacío'}]

    headers = [str(h).strip().lower() if h else '' for h in filas[0]]

    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in headers]
    if faltantes:
        return [], [{'fila': 1, 'motivo': f"Faltan columnas obligatorias: {', '.join(faltantes)}"}]

    idx = {c: headers.index(c) for c in COLUMNAS_REQUERIDAS}

    validas = []
    errores = []
    for i, fila in enumerate(filas[1:], start=2):
        if not fila or all(c is None or str(c).strip() == '' for c in fila):
            continue  # fila vacía, se ignora silenciosamente

        def obtener(campo):
            pos = idx[campo]
            val = fila[pos] if pos < len(fila) else None
            return str(val).strip() if val is not None else ''

        datos = {campo: obtener(campo) for campo in COLUMNAS_REQUERIDAS}

        faltan = [c for c in COLUMNAS_REQUERIDAS if not datos[c]]
        if faltan:
            errores.append({'fila': i, 'motivo': f"Faltan datos en: {', '.join(faltan)}"})
            continue

        validas.append(datos)

    return validas, errores

def clave_duplicado(nombre_proyecto, profesor, curso):
    """Clave normalizada para detectar si un stand ya existe (mismo proyecto+profe+curso)"""
    return (nombre_proyecto.strip().lower(), profesor.strip().lower(), curso.strip().lower())

def separar_nuevas_y_duplicadas(validas):
    """Compara las filas leídas del Excel contra los stands ya existentes en la BD.
    Devuelve (nuevas, duplicadas) para que las duplicadas se omitan automáticamente."""
    existentes = Stand.query.filter_by(activo=True).all()
    claves_existentes = {
        clave_duplicado(s.nombre_proyecto, s.profesor_cargo, s.curso) for s in existentes
    }

    nuevas = []
    duplicadas = []
    for fila in validas:
        clave = clave_duplicado(fila['nombre_proyecto'], fila['profesor'], fila['curso'])
        if clave in claves_existentes:
            duplicadas.append(fila)
        else:
            nuevas.append(fila)
            claves_existentes.add(clave)  # evita duplicados repetidos dentro del mismo excel

    return nuevas, duplicadas

# ================================
# RUTAS PÚBLICAS - VOTACIÓN POR QR
# ================================

@app.route('/votar/<codigo>')
def votar_stand(codigo):
    """Página pública a la que apunta el QR de un stand específico"""
    stand = Stand.query.filter_by(codigo_qr=codigo.upper(), activo=True).first()
    if not stand:
        return render_template('stand_no_encontrado.html'), 404
    return render_template('votar_stand.html', stand=stand)

@app.route('/api/verificar-voto-stand/<codigo>', methods=['POST'])
def verificar_voto_stand(codigo):
    """Verificar si ya se votó en ESTE stand en particular"""
    try:
        data = request.get_json()
        user_agent = data.get('user_agent')
        ip = obtener_ip_real(request)

        if not user_agent:
            return jsonify({'puede_votar': True})

        hash_voto = generar_hash_voto(ip, user_agent, codigo.upper())
        voto_existente = Voto.query.filter_by(hash_voto=hash_voto).first()

        return jsonify({'puede_votar': voto_existente is None})
    except Exception as e:
        print(f"❌ Error verificando voto: {e}")
        return jsonify({'puede_votar': True})

@app.route('/votar/<codigo>/confirmar', methods=['POST'])
def confirmar_voto_stand(codigo):
    """Registrar el voto para un stand específico"""
    try:
        stand = Stand.query.filter_by(codigo_qr=codigo.upper(), activo=True).first()
        if not stand:
            return jsonify({'success': False, 'mensaje': 'Stand no válido'}), 404

        data = request.get_json()
        user_agent = data.get('user_agent')
        ip = obtener_ip_real(request)

        if not user_agent:
            return jsonify({'success': False, 'mensaje': 'Datos incompletos'}), 400

        hash_voto = generar_hash_voto(ip, user_agent, codigo.upper())
        voto_existente = Voto.query.filter_by(hash_voto=hash_voto).first()

        if voto_existente:
            return jsonify({'success': False, 'mensaje': 'Ya has votado en este stand'}), 400

        nuevo_voto = Voto(
            stand_id=stand.id,
            ip_address=ip,
            user_agent=user_agent,
            hash_voto=hash_voto
        )
        db.session.add(nuevo_voto)
        db.session.commit()

        return jsonify({
            'success': True,
            'mensaje': '¡Voto registrado exitosamente!',
            'stand': {
                'nombre_proyecto': stand.nombre_proyecto,
                'profesor_cargo': stand.profesor_cargo,
                'materia': stand.materia,
                'curso': stand.curso
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al registrar voto: {e}")
        return jsonify({'success': False, 'mensaje': 'Error al registrar el voto'}), 500

@app.route('/')
def index():
    """Redirigir según corresponda"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('vista_proyector'))

@app.route('/vista-proyector')
def vista_proyector():
    """Vista en vivo para proyector - Acceso público"""
    return render_template('vista_proyector.html')

@app.route('/api/resultados-live')
def resultados_live():
    """API para obtener resultados en tiempo real"""
    try:
        total_stands = Stand.query.filter_by(activo=True).count()
        total_votos = Voto.query.count()

        stands_raw = db.session.query(
            Stand.id,
            Stand.nombre_proyecto,
            Stand.curso,
            Stand.materia,
            db.func.count(Voto.id).label('votos')
        ).outerjoin(Voto).group_by(Stand.id).filter(
            Stand.activo == True
        ).order_by(db.func.count(Voto.id).desc()).all()

        proyectos = []
        for p in stands_raw:
            proyectos.append({
                'id': p[0],
                'nombre_proyecto': p[1],
                'curso': p[2],
                'materia': p[3],
                'categoria': None,
                'votos': p[4]
            })

        return jsonify({
            'total_proyectos': total_stands,
            'total_votos': total_votos,
            'proyectos': proyectos
        })
    except Exception as e:
        print(f"❌ Error en resultados-live: {e}")
        return jsonify({'total_proyectos': 0, 'total_votos': 0, 'proyectos': []}), 500

# ================================
# RUTAS DE ADMINISTRADOR
# ================================
from flask import Blueprint
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

class AdminLoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class StandForm(FlaskForm):
    nombre_proyecto = StringField('Nombre del Proyecto', validators=[DataRequired()])
    profesor_cargo = StringField('Profesor a cargo', validators=[DataRequired()])
    materia = StringField('Materia', validators=[DataRequired()])
    curso = StringField('Curso', validators=[DataRequired()])
    alumnos = TextAreaField('Alumnos (separados por coma)', validators=[DataRequired()])

class ImportarExcelForm(FlaskForm):
    archivo = FileField('Archivo Excel (.xlsx)', validators=[
        FileRequired(message='Seleccioná un archivo'),
        FileAllowed(['xlsx'], 'Solo se permiten archivos .xlsx')
    ])

class ConfirmarImportForm(FlaskForm):
    pass  # solo se usa para validar el token CSRF

class EliminarTodoForm(FlaskForm):
    pass  # solo se usa para validar el token CSRF

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

    total_stands = Stand.query.filter_by(activo=True).count()
    total_votos = Voto.query.count()

    stands_raw = db.session.query(
        Stand.id,
        Stand.nombre_proyecto,
        Stand.curso,
        Stand.materia,
        db.func.count(Voto.id).label('votos')
    ).outerjoin(Voto).group_by(Stand.id).filter(Stand.activo == True).order_by(db.func.count(Voto.id).desc()).all()

    proyectos = []
    for p in stands_raw:
        proyectos.append({
            'id': p[0],
            'nombre_proyecto': p[1],
            'curso': p[2],
            'materia': p[3],
            'categoria': None,
            'votos': p[4]
        })

    return render_template('admin/dashboard.html',
                         total_proyectos=total_stands,
                         total_votos=total_votos,
                         proyectos=proyectos)

@admin_bp.route('/stands', methods=['GET', 'POST'])
@login_required
def proyectos():
    """Gestión manual de stands (carga de emergencia, 1 por 1)"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    form = StandForm()
    eliminar_form = EliminarTodoForm()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'agregar' and form.validate_on_submit():
            stand = Stand(
                codigo_qr=generar_codigo_unico(),
                nombre_proyecto=form.nombre_proyecto.data,
                profesor_cargo=form.profesor_cargo.data,
                materia=form.materia.data,
                curso=form.curso.data,
                alumnos=form.alumnos.data
            )
            try:
                db.session.add(stand)
                db.session.commit()
                flash(f'Stand agregado exitosamente. Código QR: {stand.codigo_qr}', 'success')
                return redirect(url_for('admin.proyectos'))
            except Exception as e:
                db.session.rollback()
                flash('Error al agregar el stand', 'error')

        elif action == 'eliminar':
            stand_id = request.form.get('proyecto_id')
            stand = Stand.query.get(stand_id)
            if stand:
                if stand.votos.count() > 0:
                    flash('No se puede eliminar un stand que ya tiene votos', 'error')
                else:
                    try:
                        db.session.delete(stand)
                        db.session.commit()
                        flash('Stand eliminado exitosamente.', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash('Error al eliminar el stand', 'error')

    stands_lista = db.session.query(
        Stand, db.func.count(Voto.id).label('total_votos')
    ).outerjoin(Voto).group_by(Stand.id).filter(Stand.activo == True).all()

    return render_template('admin/proyectos.html', form=form, eliminar_form=eliminar_form, proyectos=stands_lista)

@admin_bp.route('/stands/eliminar-todos', methods=['POST'])
@login_required
def eliminar_todos_stands():
    """Borra TODOS los stands y sus votos. Pensado para reiniciar el sistema
    entre una muestra anual y la siguiente."""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    form = EliminarTodoForm()
    if not form.validate_on_submit():
        flash('No se pudo procesar la solicitud, intentá de nuevo.', 'error')
        return redirect(url_for('admin.proyectos'))

    try:
        total_stands = Stand.query.count()
        total_votos = Voto.query.count()
        # Se borran los votos primero por la relación de clave foránea
        Voto.query.delete()
        Stand.query.delete()
        db.session.commit()
        flash(f'🗑️ Se eliminaron {total_stands} stands y {total_votos} votos. El sistema quedó en cero.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {e}', 'error')

    return redirect(url_for('admin.proyectos'))

@admin_bp.route('/stands/<int:stand_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_stand(stand_id):
    """Editar los datos de un stand existente (el código QR no cambia)"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    stand = Stand.query.get_or_404(stand_id)
    form = StandForm(obj=stand)

    if form.validate_on_submit():
        stand.nombre_proyecto = form.nombre_proyecto.data
        stand.profesor_cargo = form.profesor_cargo.data
        stand.materia = form.materia.data
        stand.curso = form.curso.data
        stand.alumnos = form.alumnos.data
        try:
            db.session.commit()
            flash(f'Stand "{stand.nombre_proyecto}" actualizado correctamente. El código QR ({stand.codigo_qr}) no cambió.', 'success')
            return redirect(url_for('admin.proyectos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el stand', 'error')

    return render_template('admin/editar_stand.html', form=form, stand=stand)

@admin_bp.route('/stands/<int:stand_id>/qr')
@login_required
def stand_qr(stand_id):
    """Devuelve la imagen PNG del QR (con texto) de un stand puntual"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    stand = Stand.query.get_or_404(stand_id)
    img = generar_imagen_qr(stand)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@admin_bp.route('/stands/<int:stand_id>/pdf')
@login_required
def stand_pdf(stand_id):
    """Descarga el PDF con el QR del stand repetido 6 veces (grilla 2x3)"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    stand = Stand.query.get_or_404(stand_id)
    pdf_bytes = generar_pdf_bytes(stand)
    pdf_buf = io.BytesIO(pdf_bytes)
    pdf_buf.seek(0)

    nombre_archivo = f"QR_{stand.codigo_qr}.pdf"
    return send_file(pdf_buf, mimetype='application/pdf', as_attachment=True, download_name=nombre_archivo)

@admin_bp.route('/stands/importar', methods=['GET', 'POST'])
@login_required
def importar_stands():
    """Paso 1: subir el Excel y ver la vista previa antes de confirmar"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    form = ImportarExcelForm()

    if form.validate_on_submit():
        archivo = form.archivo.data
        try:
            file_bytes = io.BytesIO(archivo.read())
            validas, errores = leer_excel_stands(file_bytes)
        except Exception as e:
            flash(f'No se pudo leer el archivo: {e}', 'error')
            return redirect(url_for('admin.importar_stands'))

        nuevas, duplicadas = separar_nuevas_y_duplicadas(validas)

        if not nuevas and not duplicadas:
            flash('No se encontró ninguna fila válida para importar.', 'error')
            return render_template('admin/importar_excel.html', form=form)

        confirm_form = ConfirmarImportForm()
        return render_template('admin/importar_preview.html',
                               nuevas=nuevas,
                               duplicadas=duplicadas,
                               errores=errores,
                               datos_json=json.dumps(nuevas),
                               confirm_form=confirm_form)

    return render_template('admin/importar_excel.html', form=form)

@admin_bp.route('/stands/importar/confirmar', methods=['POST'])
@login_required
def confirmar_importar_stands():
    """Paso 2: crea SOLO los stands nuevos (los duplicados ya vienen filtrados)"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    form = ConfirmarImportForm()
    if not form.validate_on_submit():
        flash('La sesión de importación expiró, subí el archivo de nuevo.', 'error')
        return redirect(url_for('admin.importar_stands'))

    try:
        filas = json.loads(request.form.get('datos_json', '[]'))
    except Exception:
        flash('Error al procesar los datos del archivo.', 'error')
        return redirect(url_for('admin.importar_stands'))

    if not filas:
        flash('No había stands nuevos para importar.', 'error')
        return redirect(url_for('admin.importar_stands'))

    stands_creados = []
    for fila in filas:
        stand = Stand(
            codigo_qr=generar_codigo_unico(),
            nombre_proyecto=fila['nombre_proyecto'],
            profesor_cargo=fila['profesor'],
            materia=fila['materia'],
            curso=fila['curso'],
            alumnos=fila['alumnos']
        )
        db.session.add(stand)
        stands_creados.append(stand)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar los stands en la base de datos: {e}', 'error')
        return redirect(url_for('admin.importar_stands'))

    flash(f'✅ Se importaron {len(stands_creados)} stands correctamente.', 'success')

    ids_str = ','.join(str(s.id) for s in stands_creados)
    return redirect(url_for('admin.importar_exito', ids=ids_str))

@admin_bp.route('/stands/importar/exito')
@login_required
def importar_exito():
    """Página de confirmación después de importar, con botón para descargar el ZIP"""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    ids_str = request.args.get('ids', '')
    ids = [int(i) for i in ids_str.split(',') if i.isdigit()]
    stands = Stand.query.filter(Stand.id.in_(ids)).all() if ids else []

    return render_template('admin/importar_exito.html', stands=stands, ids_str=ids_str)

@admin_bp.route('/stands/importar/zip')
@login_required
def importar_zip():
    """Genera (o regenera) el .zip con los PDF de los stands indicados.
    Se puede descargar las veces que haga falta sin duplicar nada, porque
    no crea registros nuevos: solo arma los PDF a partir de los que ya existen."""
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    ids_str = request.args.get('ids', '')
    ids = [int(i) for i in ids_str.split(',') if i.isdigit()]
    stands = Stand.query.filter(Stand.id.in_(ids)).all() if ids else []

    if not stands:
        flash('No se encontraron stands para descargar.', 'error')
        return redirect(url_for('admin.proyectos'))

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for stand in stands:
            pdf_bytes = generar_pdf_bytes(stand)
            nombre_pdf = f"QR_{stand.codigo_qr}_{stand.nombre_proyecto[:30]}.pdf"
            nombre_pdf = nombre_pdf.replace('/', '-').replace('\\', '-').replace(' ', '_')
            zf.writestr(nombre_pdf, pdf_bytes)
    zip_buf.seek(0)

    nombre_zip = f'QRs_ITEL_{datetime.now().strftime("%Y%m%d_%H%M")}.zip'
    return send_file(zip_buf, mimetype='application/zip', as_attachment=True, download_name=nombre_zip)

@admin_bp.route('/votos')
@login_required
def votos():
    if not is_admin():
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('admin.login'))

    votos_lista = db.session.query(
        Voto, Stand.nombre_proyecto, Stand.curso
    ).join(Stand).order_by(Voto.fecha_voto.desc()).all()

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)