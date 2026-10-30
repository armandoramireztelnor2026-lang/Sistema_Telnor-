with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('style.css?v=1000034', 'style.css?v=1000035')
content = content.replace('seccion_reportes.js?v=1000019', 'seccion_reportes.js?v=1000020')

old_th = '<th class="th-verde col-verde">RETRO (PROBLEMA)</th>'
new_th = '<th class="th-verde col-verde col-retro-problema">RETRO (PROBLEMA)</th>'

if old_th in content:
    content = content.replace(old_th, new_th)
    print("Replaced retro th in administracion.html")
else:
    print("Warning: old_th not found!")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html successfully")

