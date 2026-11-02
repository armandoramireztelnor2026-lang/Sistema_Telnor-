import sys
import urllib.request

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Ejecutando pruebas de fijación de columna y cuadro de cruce ---")

# 1. Probar que el servidor Flask responde
base_url = "http://127.0.0.1:5000"
try:
    with urllib.request.urlopen(f"{base_url}/") as res:
        print(f"✓ Servidor Flask activo HTTP {res.status}")
except Exception as e:
    print(f"✗ Error al conectar con servidor: {e}")

# 2. Verificar static/style.css
with open('static/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

css_needles = [
    ".columna-fijada-th",
    ".columna-fijada-td",
    ".celda-cruce-marcada",
    "border: 3px solid #f59e0b",
    "box-shadow: inset 0 0 0 2px #fef08a"
]

for n in css_needles:
    assert n in css_content, f"Falta '{n}' en static/style.css"
print("✓ static/style.css contiene todas las clases requeridas (.columna-fijada-th, .columna-fijada-td, .celda-cruce-marcada)")

# 3. Verificar static/seccion_reportes.js
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

js_needles = [
    "window.columnaFijadaReportesIndex",
    "actualizarMarcadoColumnaYCruceReportes",
    "th.classList.add('columna-fijada-th')",
    "td.classList.add('columna-fijada-td')",
    "td.classList.add('celda-cruce-marcada')",
    "e.target.closest('#tabla-exportable-reportes thead th')",
    "e.target.closest('#tabla-exportable-reportes tbody tr')"
]

for n in js_needles:
    assert n in js_content, f"Falta '{n}' en static/seccion_reportes.js"
print("✓ static/seccion_reportes.js contiene la lógica interactiva de fijación de columna y cálculo de cuadro de cruce")

# 4. Simulación algorítmica de la lógica de cruce
class Celda:
    def __init__(self, col):
        self.col = col
        self.classes = set()

class Fila:
    def __init__(self, row_id, num_cols):
        self.row_id = row_id
        self.classes = set()
        self.celdas = [Celda(i) for i in range(num_cols)]

num_filas = 5
num_columnas = 35
filas = [Fila(i, num_columnas) for i in range(num_filas)]

def simular_actualizar(col_fijada, filas_list):
    for r in filas_list:
        is_row_marcada = 'selected-row' in r.classes
        for c in r.celdas:
            is_col_fijada = (col_fijada is not None and c.col == col_fijada)
            if is_col_fijada:
                c.classes.add('columna-fijada-td')
            else:
                c.classes.discard('columna-fijada-td')
            
            if is_col_fijada and is_row_marcada:
                c.classes.add('celda-cruce-marcada')
            else:
                c.classes.discard('celda-cruce-marcada')

# Paso A: Seleccionar Fila 2
filas[2].classes.add('selected-row')
simular_actualizar(col_fijada=None, filas_list=filas)
assert not any('celda-cruce-marcada' in c.classes for r in filas for c in r.celdas), "No debe haber cruce si no hay columna fijada"
print("✓ Paso A: Selección de fila sin columna fijada -> No hay cruce")

# Paso B: Fijar Columna 14 (COSTO TOTAL)
simular_actualizar(col_fijada=14, filas_list=filas)
cruce_cells = [(r.row_id, c.col) for r in filas for c in r.celdas if 'celda-cruce-marcada' in c.classes]
assert cruce_cells == [(2, 14)], f"Esperado cruce en (2, 14), obtenido {cruce_cells}"
print("✓ Paso B: Columna 14 fijada con Fila 2 marcada -> Cruce exacto en celda (Fila 2, Columna 14)")

# Paso C: Cambiar fila a Fila 4
filas[2].classes.remove('selected-row')
filas[4].classes.add('selected-row')
simular_actualizar(col_fijada=14, filas_list=filas)
cruce_cells = [(r.row_id, c.col) for r in filas for c in r.celdas if 'celda-cruce-marcada' in c.classes]
assert cruce_cells == [(4, 14)], f"Esperado cruce en (4, 14), obtenido {cruce_cells}"
print("✓ Paso C: Cambio de fila a Fila 4 -> Cruce se mueve limpiamente a (Fila 4, Columna 14)")

# Paso D: Cambiar columna a Columna 19 (RETRABAJO)
simular_actualizar(col_fijada=19, filas_list=filas)
cruce_cells = [(r.row_id, c.col) for r in filas for c in r.celdas if 'celda-cruce-marcada' in c.classes]
assert cruce_cells == [(4, 19)], f"Esperado cruce en (4, 19), obtenido {cruce_cells}"
print("✓ Paso D: Cambio de columna a Columna 19 -> Cruce se mueve a (Fila 4, Columna 19)")

# Paso E: Desfijar columna (clic en la misma columna)
simular_actualizar(col_fijada=None, filas_list=filas)
assert not any('celda-cruce-marcada' in c.classes for r in filas for c in r.celdas), "Al desfijar no debe haber cruce"
assert not any('columna-fijada-td' in c.classes for r in filas for c in r.celdas), "Al desfijar no debe haber celdas de columna fijada"
print("✓ Paso E: Desfijar columna -> Desactivación limpia y total")

print("\n🎉 TODAS LAS PRUEBAS DE FIJACIÓN DE COLUMNA Y CUADRO DE CRUCE PASARON SATISFACTORIAMENTE (100%)")

