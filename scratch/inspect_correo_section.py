import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx_c = html.find('id="seccion-cfg-correo"')
idx_p = html.find('id="seccion-cfg-presupuesto"')

print("Correo section HTML (first 1000 chars):")
print(html[idx_c:idx_c+1000])

