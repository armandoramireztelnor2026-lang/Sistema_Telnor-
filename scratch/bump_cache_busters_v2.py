def bump(path, mapping):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in mapping.items():
        content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

bump('templates/administracion.html', {
    'facturas_principal.js?v=65': 'facturas_principal.js?v=70',
    'cotizaciones_10k.js?v=26': 'cotizaciones_10k.js?v=28',
    'script.js?v=1000045': 'script.js?v=1000050'
})

bump('templates/proveedores.html', {
    'facturas_principal.js?v=65': 'facturas_principal.js?v=70',
    'script.js?v=1000045': 'script.js?v=1000050'
})

print("Cache busters bumped successfully to v70 / v28 / v1000050")

