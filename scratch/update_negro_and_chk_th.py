with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bump style.css and seccion_reportes.js
content = content.replace('style.css?v=1000031', 'style.css?v=1000032')
content = content.replace('seccion_reportes.js?v=1000017', 'seccion_reportes.js?v=1000018')

# 2. Update checkbox header to azul marino
old_chk = '<th><input type="checkbox" id="chk-all-reportes" onclick="toggleAllReportes(this)">'
new_chk = '<th class="th-azul-marino col-azul-marino"><input type="checkbox" id="chk-all-reportes" onclick="toggleAllReportes(this)">'

if old_chk in content:
    content = content.replace(old_chk, new_chk)
    print("Replaced checkbox th")
else:
    print("Warning: old_chk not found!")

# 3. Update the 9 black column headers
old_th_block = """                                    <th>NUM. PEDIDO</th>
                                    <th>NUM. DE ORDEN</th>
                                    <th>NUM. FACTURA</th>
                                    <th>PDF FACTURA</th>
                                    <th>ADMINISTRADOR</th>
                                    <th>STATUS DOC. CONTABLE</th>
                                    <th>NUM DOC. CONTABLE</th>
                                    <th>COMENTARIOS</th>
                                    <th>JEFATURA</th>"""

new_th_block = """                                    <th class="th-negro col-negro">NUM. PEDIDO</th>
                                    <th class="th-negro col-negro">NUM. DE ORDEN</th>
                                    <th class="th-negro col-negro">NUM. FACTURA</th>
                                    <th class="th-negro col-negro">PDF FACTURA</th>
                                    <th class="th-negro col-negro">ADMINISTRADOR</th>
                                    <th class="th-negro col-negro">STATUS DOC. CONTABLE</th>
                                    <th class="th-negro col-negro">NUM DOC. CONTABLE</th>
                                    <th class="th-negro col-negro">COMENTARIOS</th>
                                    <th class="th-negro col-negro">JEFATURA</th>"""

if old_th_block in content:
    content = content.replace(old_th_block, new_th_block)
    print("Replaced LF th block for black columns")
else:
    old_th_block_crlf = old_th_block.replace("\n", "\r\n")
    new_th_block_crlf = new_th_block.replace("\n", "\r\n")
    if old_th_block_crlf in content:
        content = content.replace(old_th_block_crlf, new_th_block_crlf)
        print("Replaced CRLF th block for black columns")
    else:
        print("Warning: could not find exact black th block!")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html successfully")

