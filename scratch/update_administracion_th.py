with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bump style.css version
content = content.replace('style.css?v=1000029', 'style.css?v=1000030')

# 2. Bump seccion_reportes.js version
content = content.replace('seccion_reportes.js?v=1000015', 'seccion_reportes.js?v=1000016')

# 3. Target the 12 th headers
old_th_block = """                                    <th>TICKET</th>
                                    <th>NUM. ECO</th>
                                    <th>FECHA TICKET</th>
                                    <th>TIEMPO DEL TICKET</th>
                                    <th>FECHA TICKET FINALIZADO</th>
                                    <th>ESTADO</th>
                                    <th>STATUS UNIDAD</th>
                                    <th>SUPERVISOR</th>
                                    <th>COMPAÑIA</th>
                                    <th>DEPARTAMENTO</th>
                                    <th>COPE/EDIFICIO</th>
                                    <th>CIUDAD/MUNICIPIO BASE</th>"""

new_th_block = """                                    <th class="th-azul-marino col-azul-marino">TICKET</th>
                                    <th class="th-azul-marino col-azul-marino">NUM. ECO</th>
                                    <th class="th-azul-marino col-azul-marino">FECHA TICKET</th>
                                    <th class="th-azul-marino col-azul-marino">TIEMPO DEL TICKET</th>
                                    <th class="th-azul-marino col-azul-marino">FECHA TICKET FINALIZADO</th>
                                    <th class="th-azul-marino col-azul-marino">ESTADO</th>
                                    <th class="th-azul-marino col-azul-marino">STATUS UNIDAD</th>
                                    <th class="th-azul-marino col-azul-marino">SUPERVISOR</th>
                                    <th class="th-azul-marino col-azul-marino">COMPAÑIA</th>
                                    <th class="th-azul-marino col-azul-marino">DEPARTAMENTO</th>
                                    <th class="th-azul-marino col-azul-marino">COPE/EDIFICIO</th>
                                    <th class="th-azul-marino col-azul-marino">CIUDAD/MUNICIPIO BASE</th>"""

if old_th_block in content:
    content = content.replace(old_th_block, new_th_block)
    print("Found and replaced LF block")
else:
    old_th_block_crlf = old_th_block.replace("\n", "\r\n")
    new_th_block_crlf = new_th_block.replace("\n", "\r\n")
    if old_th_block_crlf in content:
        content = content.replace(old_th_block_crlf, new_th_block_crlf)
        print("Found and replaced CRLF block")
    else:
        print("Warning: could not find exact th block!")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html successfully")

