import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx_c = html.find('id="seccion-cfg-correo"')
idx_p = html.find('id="seccion-cfg-presupuesto"')
idx_l = html.find('id="seccion-cfg-limite"')
idx_m = html.find('id="modal-agregar-cuenta-correo"')

print('Seccion Correo tag:', html[idx_c-30:idx_c+60])
print('Seccion Presupuesto tag:', html[idx_p-30:idx_p+60])
print('Seccion Limite tag:', html[idx_l-30:idx_l+60])
print('Nav 1 check in html:', 'Paso 1 de 3' in html)
print('Nav 2 check in html:', 'Paso 2 de 3' in html)
print('Nav 3 check in html:', 'Paso 3 de 3' in html)
print('Script tag v=2 check:', 'configuraciones_jefatura.js?v=2' in html)

