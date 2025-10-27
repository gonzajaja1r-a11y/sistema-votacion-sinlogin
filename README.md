# 🎓 Sistema de Votación - Muestra Anual ITEL 2025

Sistema de votación web para la Muestra Anual de Proyectos del ITEL.

**Desarrollado por:** Cristian Gonzalo Segovia - 5°U

---

## 📋 Requisitos del Servidor

- Python 3.8 o superior
- MySQL/MariaDB
- Acceso SSH al servidor

---

## 🚀 Instalación

### 1. Subir archivos al servidor
```bash
scp -r sistema-votacion/ usuario@servidor:/ruta/destino/
```

### 2. Conectarse por SSH
```bash
ssh usuario@servidor
cd /ruta/destino/sistema-votacion
```

### 3. Instalar dependencias
```bash
pip3 install -r requirements.txt
```

### 4. Configurar Base de Datos

**Crear la base de datos en MySQL:**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE sistema_votacion CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'votacion_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURA';
GRANT ALL PRIVILEGES ON sistema_votacion.* TO 'votacion_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Importar estructura:**
```bash
mysql -u votacion_user -p sistema_votacion < BASE\ DE\ DATOS/sistema_votacion.sql
```

### 5. Configurar credenciales

**Editar `config.py`:**
```python
SECRET_KEY = 'CAMBIAR-POR-CLAVE-SUPER-SEGURA-RANDOM-123456'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://votacion_user:TU_PASSWORD_SEGURA@localhost:3306/sistema_votacion'
```

> ⚠️ **IMPORTANTE:** Cambiar `TU_PASSWORD_SEGURA` por la contraseña real del usuario MySQL.

### 6. Inicializar aplicación

```bash
python3 app.py
```

Si es la primera vez, descomentar en `app.py` la línea:
```python
# init_db()  # ← Descomentar solo la primera vez
```

Luego ejecutar y volver a comentar.

---

## 🔐 Credenciales Admin por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> ⚠️ **CAMBIAR** inmediatamente después del primer acceso.

---

## 🌐 Acceso a la Aplicación

Una vez corriendo:

- **Votación Pública:** `http://servidor:5000/votacion-publica`
- **Panel Admin:** `http://servidor:5000/admin/login`
- **Vista Proyector:** `http://servidor:5000/vista-proyector`

---

## 🔧 Configuración Producción

### Opción 1: Gunicorn (Recomendado)

```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Opción 2: Con systemd

Crear `/etc/systemd/system/votacion.service`:

```ini
[Unit]
Description=Sistema Votacion ITEL
After=network.target

[Service]
User=www-data
WorkingDirectory=/ruta/destino/sistema-votacion
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable votacion
sudo systemctl start votacion
```

---

## 📁 Estructura de Archivos

```
sistema-votacion/
├── app.py                  # Aplicación principal
├── config.py              # Configuración (EDITAR AQUÍ)
├── models.py              # Modelos de BD
├── requirements.txt       # Dependencias
├── static/
│   └── img/
│       └── logo-itel.png  # Logo del colegio
└── templates/
    ├── votacion_publica.html
    ├── vista_proyector.html
    ├── gracias.html
    ├── base.html
    └── admin/
        ├── login.html
        ├── dashboard.html
        ├── proyectos.html
        └── votos.html
```

---

## 🐛 Solución de Problemas

### Error: "Could not build url"
Verificar que todas las rutas en `app.py` estén definidas.

### Error: "Unknown column 'candidato_id'"
Ejecutar en MySQL:
```sql
ALTER TABLE votos DROP FOREIGN KEY votos_ibfk_1;
ALTER TABLE votos CHANGE COLUMN candidato_id proyecto_id INT(11) NOT NULL;
ALTER TABLE votos ADD CONSTRAINT votos_ibfk_1 FOREIGN KEY (proyecto_id) REFERENCES proyectos (id);
```

### Puerto 5000 ocupado
Cambiar puerto en `app.py` última línea:
```python
app.run(host='0.0.0.0', port=8000, debug=False)
```


## 📝 Notas Importantes

- ✅ El sistema detecta votos duplicados por IP + User-Agent
- ✅ Los votos son anónimos, no se registran datos personales
- ✅ La vista en vivo se actualiza automáticamente cada 5 segundos
- ✅ No se pueden eliminar proyectos que ya tienen votos
- ⚠️ Hacer backup de la BD antes de la muestra: `mysqldump -u root -p sistema_votacion > backup.sql`

---

## ⚡ CHECKLIST RÁPIDO (Lo que SÍ o SÍ hay que hacer)

### 🔴 OBLIGATORIO - Antes de iniciar:

1. **Editar `config.py`:**
   ```python
   # Línea 4: Cambiar esta clave por algo aleatorio y seguro
   SECRET_KEY = 'CAMBIAR-ESTO-POR-ALGO-RANDOM-Y-LARGO-12345XYZ'
   
   # Línea 7: Poner credenciales reales de MySQL
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://votacion_user:TU_PASSWORD_REAL@localhost:3306/sistema_votacion'
   ```

2. **Primera ejecución - Descomentar en `app.py` (línea ~427):**
   ```python
   if __name__ == '__main__':
       init_db()  # ← Descomentar esta línea SOLO la primera vez
       app.run(...)
   ```
   
   Ejecutar: `python3 app.py`
   
   Luego **VOLVER A COMENTAR** esa línea:
   ```python
   # init_db()  # ← Volver a comentar después de la primera ejecución
   ```

3. **Cambiar contraseña admin:**
   - Acceder a `http://servidor:5000/admin/login`
   - Usuario: `admin` / Contraseña: `admin123`
   - ⚠️ Cambiar inmediatamente estas credenciales

### ✅ Verificación Final

Probar estos 3 accesos:
- [ ] **Votación Pública:** `http://servidor:5000/votacion-publica` (funciona sin login)
- [ ] **Panel Admin:** `http://servidor:5000/admin/login` (pide usuario/contraseña)
- [ ] **Vista Proyector:** `http://servidor:5000/vista-proyector` (muestra ranking en vivo)
