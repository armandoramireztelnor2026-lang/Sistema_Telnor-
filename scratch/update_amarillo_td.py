with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_td_block = """                <td style="vertical-align:top; padding-top:15px;">${valRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valNumRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valTiempoReingreso}</td>
                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaFinReingreso}</td>"""

new_td_block = """                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px;">${valRetrabajo}</td>
                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px;">${valNumRetrabajo}</td>
                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaRetrabajo}</td>
                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valTiempoReingreso}</td>
                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaFinReingreso}</td>"""

if old_td_block in content:
    content = content.replace(old_td_block, new_td_block)
    print("Found and replaced LF td block in seccion_reportes.js")
else:
    old_td_block_crlf = old_td_block.replace("\n", "\r\n")
    new_td_block_crlf = new_td_block.replace("\n", "\r\n")
    if old_td_block_crlf in content:
        content = content.replace(old_td_block_crlf, new_td_block_crlf)
        print("Found and replaced CRLF td block in seccion_reportes.js")
    else:
        print("Warning: could not find exact td block in seccion_reportes.js!")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/seccion_reportes.js with yellow columns successfully")

