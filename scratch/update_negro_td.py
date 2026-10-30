with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update checkbox cell to azul marino
old_chk_td = '<td style="vertical-align:top; padding-top:15px;"><input type="checkbox" class="chk-reporte" value="${ticket}"></td>'
new_chk_td = '<td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px;"><input type="checkbox" class="chk-reporte" value="${ticket}"></td>'

if old_chk_td in content:
    content = content.replace(old_chk_td, new_chk_td)
    print("Replaced checkbox td")
else:
    print("Warning: old_chk_td not found!")

# 2. Update the 9 black columns td
old_negro_block = """                <td style="vertical-align:top; padding-top:15px;">${htmlNumPedido}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumOrden}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlBtnPdfFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreAdmin}</td>
                <td style="vertical-align:top; padding-top:15px;">${statusDocContable}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumContable}</td>
                <td style="vertical-align:top; padding-top:15px;">${btnComentarios}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreJefatura}</td>"""

new_negro_block = """                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumPedido}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumOrden}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumFactura}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlBtnPdfFactura}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${nombreAdmin}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${statusDocContable}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumContable}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${btnComentarios}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${nombreJefatura}</td>"""

if old_negro_block in content:
    content = content.replace(old_negro_block, new_negro_block)
    print("Replaced LF block for negro columns")
else:
    old_negro_block_crlf = old_negro_block.replace("\n", "\r\n")
    new_negro_block_crlf = new_negro_block.replace("\n", "\r\n")
    if old_negro_block_crlf in content:
        content = content.replace(old_negro_block_crlf, new_negro_block_crlf)
        print("Replaced CRLF block for negro columns")
    else:
        print("Warning: could not find exact negro td block in seccion_reportes.js!")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/seccion_reportes.js successfully")

