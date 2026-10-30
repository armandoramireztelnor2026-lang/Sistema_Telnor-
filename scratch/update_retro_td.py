with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_td = '<td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;"><div style="max-width:250px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${htmlRetro}</div></td>'
new_td = '<td class="td-verde col-verde col-retro-problema" style="vertical-align:top; padding-top:15px; color:#ffffff;"><div class="retro-contenido">${htmlRetro}</div></td>'

if old_td in content:
    content = content.replace(old_td, new_td)
    print("Replaced retro td in seccion_reportes.js")
else:
    print("Warning: old_td not found in seccion_reportes.js!")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated seccion_reportes.js successfully")

