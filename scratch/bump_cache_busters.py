import re

def bump(path, mapping):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in mapping.items():
        content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

bump('templates/administracion.html', {
    'script.js?v=1000040': 'script.js?v=1000045',
    'facturas_principal.js?v=61': 'facturas_principal.js?v=65',
    'seccion_reportes.js?v=1000020': 'seccion_reportes.js?v=1000025'
})

bump('templates/proveedores.html', {
    'script.js?v=1000038': 'script.js?v=1000045',
    'facturas_principal.js?v=61': 'facturas_principal.js?v=65'
})

print("Cache busters bumped successfully")

