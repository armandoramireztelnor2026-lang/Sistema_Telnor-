with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bump versions
content = content.replace('style.css?v=1000032', 'style.css?v=1000033')
content = content.replace('seccion_reportes.js?v=1000018', 'seccion_reportes.js?v=1000019')

# 2. Update the 6 green headers
old_verde_block = """                                    <th>RETRO (PROBLEMA)</th>
                                    <th>COSTO (TOTAL)</th>
                                    <th>PROVEEDOR/TALLER</th>
                                    <th>FECHA DE ENTRADA</th>
                                    <th>TIEMPO EN TALLER</th>
                                    <th>FECHA DE SALIDA</th>"""

new_verde_block = """                                    <th class="th-verde col-verde">RETRO (PROBLEMA)</th>
                                    <th class="th-verde col-verde">COSTO (TOTAL)</th>
                                    <th class="th-verde col-verde">PROVEEDOR/TALLER</th>
                                    <th class="th-verde col-verde">FECHA DE ENTRADA</th>
                                    <th class="th-verde col-verde">TIEMPO EN TALLER</th>
                                    <th class="th-verde col-verde">FECHA DE SALIDA</th>"""

if old_verde_block in content:
    content = content.replace(old_verde_block, new_verde_block)
    print("Replaced LF block for verde th")
else:
    old_verde_block_crlf = old_verde_block.replace("\n", "\r\n")
    new_verde_block_crlf = new_verde_block.replace("\n", "\r\n")
    if old_verde_block_crlf in content:
        content = content.replace(old_verde_block_crlf, new_verde_block_crlf)
        print("Replaced CRLF block for verde th")
    else:
        print("Warning: could not find exact verde th block!")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html with verde headers successfully")

