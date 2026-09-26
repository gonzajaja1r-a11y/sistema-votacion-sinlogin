"""
Genera un Excel de prueba (test_stands.xlsx) con 5 stands de ejemplo,
para probar la importación masiva.
Uso: python generar_excel_prueba.py
"""

import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Stands"

# Encabezados (deben coincidir exactamente con lo que espera el sistema)
headers = ["nombre_proyecto", "profesor", "curso", "materia", "alumnos"]
ws.append(headers)

# Filas de ejemplo
datos = [
    ["Robot Seguidor de Línea", "Prof. Gómez", "3°A", "Robótica", "Juan Pérez, Ana López"],
    ["App de Recetas", "Prof. Rolón", "5°U", "Programación", "María Fernández"],
    ["Huerta Automatizada", "Prof. Torres", "4°B", "Hardware", "Carlos Ruiz, Sofía Díaz, Martín Gómez"],
    ["Juegos de Historia Argentina", "Prof. Benítez", "2°A", "Ciencias Sociales", "Lucía Martínez"],
    ["", "Prof. Falla", "1°A", "Prueba", "Sin nombre de proyecto"],  # fila con error a propósito
]

for fila in datos:
    ws.append(fila)

wb.save("test_stands.xlsx")
print("✅ Archivo 'test_stands.xlsx' creado en la carpeta actual")
print("   Contiene 4 filas válidas + 1 fila con error a propósito (sin nombre_proyecto)")
print("   Así podés probar también que el sistema detecte y muestre los errores.")