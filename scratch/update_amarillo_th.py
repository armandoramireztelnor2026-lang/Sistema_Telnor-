with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bump style.css version
content = content.replace('style.css?v=1000030', 'style.css?v=1000031')

# 2. Bump seccion_reportes.js version
content = content.replace('seccion_reportes.js?v=1000016', 'seccion_reportes.js?v=1000017')

# 3. Target the 5 th headers
old_th_block = """                                    <th>RETRABAJO</th>
                                    <th>NUM/RETRABAJO</th>
                                    <th>FECHA/RETRABAJO</th>
                                    <th>TIEMPO EN TALLER/REINGRESO</th>
                                    <th>FECHA DE FINALIZACION/REINGRESO</th>"""

new_th_block = """                                    <th class="th-amarillo col-amarillo">RETRABAJO</th>
                                    <th class="th-amarillo col-amarillo">NUM/RETRABAJO</th>
                                    <th class="th-amarillo col-amarillo">FECHA/RETRABAJO</th>
                                    <th class="th-amarillo col-amarillo">TIEMPO EN TALLER/REINGRESO</th>
                                    <th class="th-amarillo col-amarillo">FECHA DE FINALIZACION/REINGRESO</th>"""

if old_th_block in content:
    content = content.replace(old_th_block, new_th_block)
    print("Found and replaced LF th block")
else:
    old_th_block_crlf = old_th_block.replace("\n", "\r\n")
    new_th_block_crlf = new_th_block.replace("\n", "\r\n")
    if old_th_block_crlf in content:
        content = content.replace(old_th_block_crlf, new_th_block_crlf)
        print("Found and replaced CRLF th block")
    else:
        print("Warning: could not find exact th block!")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html with yellow headers successfully")

