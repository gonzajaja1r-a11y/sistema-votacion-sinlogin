"""
Script para inicializar la base de datos en Supabase (PostgreSQL)
Ejecutar UNA SOLA VEZ para crear las tablas y los administradores.

Requiere que exista un archivo .env en la raíz del proyecto con:
DATABASE_URL=postgresql://...
SECRET_KEY=...
"""

from app import app, db
from models import Administrador, Stand, Voto

def init_supabase_db():
    """Inicializar base de datos en Supabase"""
    with app.app_context():
        print("=" * 70)
        print("🔧 INICIALIZANDO BASE DE DATOS - SISTEMA DE VOTACIÓN ITEL")
        print("=" * 70)
        
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Ocultar la password al imprimir
        safe_uri = db_uri.split('@')[-1] if '@' in db_uri else db_uri
        print(f"\n📍 Conectando a: ...@{safe_uri}")

        try:
            print("\n📦 Creando estructura de tablas...")
            db.create_all()
            print("✅ Tablas creadas correctamente:")
            print("   ✓ administradores")
            print("   ✓ stands")
            print("   ✓ votos")

            # ============================================
            # CREAR ADMINISTRADORES
            # ⚠️ CAMBIAR ESTOS DATOS ANTES DE EJECUTAR
            # ============================================
            admins_config = [
                {
                    'usuario': 'admin1',
                    'nombre': 'Administrador Principal',
                    'password': 'CAMBIAR-ESTA-CONTRASEÑA-1'
                },
                {
                    'usuario': 'admin2',
                    'nombre': 'Administrador Secundario',
                    'password': 'CAMBIAR-ESTA-CONTRASEÑA-2'
                }
            ]

            print("\n👤 Creando administradores...")
            admins_existentes = Administrador.query.count()

            if admins_existentes == 0:
                for admin_data in admins_config:
                    admin = Administrador(
                        usuario=admin_data['usuario'],
                        nombre=admin_data['nombre']
                    )
                    admin.set_password(admin_data['password'])
                    db.session.add(admin)
                    print(f"   ✅ Creado: {admin_data['usuario']} ({admin_data['nombre']})")

                db.session.commit()
                print(f"\n✅ {len(admins_config)} administradores creados exitosamente")
                print("\n🔐 CREDENCIALES DE ACCESO:")
                for admin_data in admins_config:
                    print(f"   • Usuario: {admin_data['usuario']}")
                    print(f"     Contraseña: {admin_data['password']}")
            else:
                print(f"⚠️  Ya existen {admins_existentes} administrador(es), no se crean nuevos.")
                print("   Si querés reiniciar admins, borralos manualmente desde Supabase")
                print("   (Table Editor → administradores → borrar filas) y volvé a correr este script.")

            # Estadísticas
            total_proyectos = Stand.query.count()
            total_votos = Voto.query.count()
            total_admins = Administrador.query.count()

            print("\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:")
            print(f"   Stands: {total_proyectos}")
            print(f"   Votos: {total_votos}")
            print(f"   Administradores: {total_admins}")

            print("\n" + "=" * 70)
            print("🎉 ¡BASE DE DATOS LISTA EN SUPABASE!")
            print("=" * 70)
            print("\n💡 Podés verificar las tablas en:")
            print("   Supabase Dashboard → Table Editor")

        except Exception as e:
            print("\n" + "=" * 70)
            print("❌ ERROR AL INICIALIZAR LA BASE DE DATOS")
            print("=" * 70)
            print(f"\n{str(e)}\n")

            import traceback
            traceback.print_exc()

            print("\n💡 POSIBLES SOLUCIONES:")
            print("   1. Verifica que el archivo .env existe y tiene DATABASE_URL correcta")
            print("   2. Verifica que copiaste bien la password (sin espacios de más)")
            print("   3. Verifica que instalaste las dependencias nuevas:")
            print("      pip install -r requirements.txt")

if __name__ == '__main__':
    init_supabase_db()