with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_verde_block = """                <td style="vertical-align:top; padding-top:15px;"><div style="max-width:250px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${htmlRetro}</div></td>
                <td style="vertical-align:top; padding-top:15px;" data-costo="${ticketGasto}"><strong>${htmlCosto}</strong></td>
                <td style="vertical-align:top; padding-top:15px;">${proveedor}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaEntrada}</td>
                <td style="vertical-align:top; padding-top:15px;">${tiempoTaller}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaSalida}</td>"""

new_verde_block = """                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;"><div style="max-width:250px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${htmlRetro}</div></td>
                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;" data-costo="${ticketGasto}"><strong>${htmlCosto}</strong></td>
                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;">${proveedor}</td>
                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;">${fechaEntrada}</td>
                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;">${tiempoTaller}</td>
                <td class="td-verde col-verde" style="vertical-align:top; padding-top:15px; color:#ffffff;">${fechaSalida}</td>"""

if old_verde_block in content:
    content = content.replace(old_verde_block, new_verde_block)
    print("Replaced LF block for verde td")
else:
    old_verde_block_crlf = old_verde_block.replace("\n", "\r\n")
    new_verde_block_crlf = new_verde_block.replace("\n", "\r\n")
    if old_verde_block_crlf in content:
        content = content.replace(old_verde_block_crlf, new_verde_block_crlf)
        print("Replaced CRLF block for verde td")
    else:
        print("Warning: could not find exact verde td block!")

# Ensure click listener for row selection exists
click_handler = """
// --- MARCADOR DE LINEA COMPLETA AL HACER CLICK EN CUALQUIER CELDA O CUADRO ---
document.addEventListener('click', function (e) {
    let tr = e.target.closest('#tabla-exportable-reportes tbody tr');
    if (!tr) return;
    let tbody = tr.parentElement;
    if (!tbody) return;
    let rows = tbody.querySelectorAll('tr');
    rows.forEach(r => {
        r.classList.remove('selected-row');
        r.classList.remove('fila-marcada');
    });
    tr.classList.add('selected-row');
    tr.classList.add('fila-marcada');
});
"""

if 'fila-marcada' not in content:
    content += click_handler
    print("Added click listener for fila-marcada")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/seccion_reportes.js successfully")

