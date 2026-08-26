import os

files_to_fix = [
    'static/facturas_principal.js',
    'static/facturas_pdf.js',
    'static/script.js',
    'app.py',
    'rutas_facturas.py',
    'rutas_reportes.py',
    'templates/administracion.html'
]

replacements = {
    'cdigo': 'código',
    'reparacin': 'reparación',
    'termin': 'terminó',
    'enviar': 'enviará',
    'automtico': 'automático',
    'Confirmas': '¿Confirmas',
    'Aprobar': '¿Aprobar',
    'Administracin': 'Administración',
    'actualizacin': 'actualización',
    'Aceptar': '¿Aceptar',
    'Ests': '¿Estás',
    'Eliminar': '¿Eliminar',
    ' PROPSITO': ' PROPÓSITO',
    'Mdulos': 'Módulos',
    'FIRMA': '✍ FIRMA' # Fix firma icon as well
}

for file_path in files_to_fix:
    if not os.path.exists(file_path): continue
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for bad, good in replacements.items():
            content = content.replace(bad, good)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print("Encoding fixes applied.")
