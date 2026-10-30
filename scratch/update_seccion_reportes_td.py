with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix colspan from 24 to 33
content = content.replace('colspan="24"', 'colspan="33"')

old_td_block = """                <td style="vertical-align:top; padding-top:15px;"><span style="color:#0ea5e9; font-weight:bold;">${ticket}</span>${badgeCaras}</td>
                <td style="vertical-align:top; padding-top:15px;">${numEco}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaTicket}</td>
                <td style="vertical-align:top; padding-top:15px;">${tiempoTicket}</td>
                <td style="vertical-align:top; padding-top:15px;">${f.fecha_cierre || pendienteHTML}</td>
                <td style="vertical-align:top; padding-top:15px;"><span style="background:${badgeColorEstado}; color:${textColorEstado}; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">${estado}</span></td>
                <td style="vertical-align:top; padding-top:15px;">${statusUnidad}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreSup}</td>
                <td style="vertical-align:top; padding-top:15px;">${compania}</td>
                <td style="vertical-align:top; padding-top:15px;">${departamento}</td>
                <td style="vertical-align:top; padding-top:15px;">${cope}</td>
                <td style="vertical-align:top; padding-top:15px;">${ciudad}</td>"""

new_td_block = """                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px;"><span style="color:#0ea5e9; font-weight:bold;">${ticket}</span>${badgeCaras}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${numEco}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${fechaTicket}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${tiempoTicket}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${f.fecha_cierre || pendienteHTML}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px;"><span style="background:${badgeColorEstado}; color:${textColorEstado}; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">${estado}</span></td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${statusUnidad}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${nombreSup}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${compania}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${departamento}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${cope}</td>
                <td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px; color:#ffffff;">${ciudad}</td>"""

if old_td_block in content:
    content = content.replace(old_td_block, new_td_block)
    print("Found and replaced LF block in seccion_reportes.js")
else:
    old_td_block_crlf = old_td_block.replace("\n", "\r\n")
    new_td_block_crlf = new_td_block.replace("\n", "\r\n")
    if old_td_block_crlf in content:
        content = content.replace(old_td_block_crlf, new_td_block_crlf)
        print("Found and replaced CRLF block in seccion_reportes.js")
    else:
        print("Warning: could not find exact td block in seccion_reportes.js!")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/seccion_reportes.js successfully")

