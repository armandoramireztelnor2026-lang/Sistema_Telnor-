import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx_c = html.find('id="seccion-cfg-correo"')
idx_p = html.find('id="seccion-cfg-presupuesto"')

print(html[idx_c:idx_p])

