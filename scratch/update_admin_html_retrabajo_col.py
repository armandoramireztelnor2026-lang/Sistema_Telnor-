# -*- coding: utf-8 -*-
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                                    <th class="th-amarillo col-amarillo">FECHA DE FINALIZACION/REINGRESO</th>
                                    <th class="th-negro col-negro">NUM. PEDIDO</th>"""

repl = """                                    <th class="th-amarillo col-amarillo">FECHA DE FINALIZACION/REINGRESO</th>
                                    <th class="th-amarillo col-amarillo">RETRABAJO FINALIZADO</th>
                                    <th class="th-negro col-negro">NUM. PEDIDO</th>"""

target_colspan = """                                    <td colspan="33" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando"""
repl_colspan = """                                    <td colspan="34" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando"""

is_crlf = '\r\n' in text
text_norm = text.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
repl_norm = repl.replace('\r\n', '\n')
target_cs_norm = target_colspan.replace('\r\n', '\n')
repl_cs_norm = repl_colspan.replace('\r\n', '\n')

if target_norm in text_norm:
    text_norm = text_norm.replace(target_norm, repl_norm, 1)
    if target_cs_norm in text_norm:
        text_norm = text_norm.replace(target_cs_norm, repl_cs_norm, 1)
    if is_crlf:
        final_text = text_norm.replace('\n', '\r\n')
    else:
        final_text = text_norm
    with open('templates/administracion.html', 'w', encoding='utf-8') as f:
        f.write(final_text)
    print('SUCCESS: administracion.html updated')
else:
    print('ERROR: target not found in administracion.html')

