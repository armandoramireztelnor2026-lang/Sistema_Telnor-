# -*- coding: utf-8 -*-

def patch_administracion():
    with open("templates/administracion.html", "r", encoding="utf-8") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    norm = content.replace("\r\n", "\n")

    t_header = '<th class="th-amarillo col-amarillo">RETRABAJO FINALIZADO</th>'
    r_header = '<th class="th-amarillo col-amarillo">RETRABAJO FINALIZADO</th>\n                                    <th class="th-amarillo col-amarillo">RETRABAJO/UNIDAD ENTREGADA</th>'

    assert t_header in norm, "t_header not found in administracion.html"
    norm = norm.replace(t_header, r_header, 1)

    t_colspan = '<td colspan="34" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando'
    r_colspan = '<td colspan="35" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando'

    assert t_colspan in norm, "t_colspan not found in administracion.html"
    norm = norm.replace(t_colspan, r_colspan, 1)

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open("templates/administracion.html", "w", encoding="utf-8") as f:
        f.write(final)

    print("templates/administracion.html updated successfully.")


def patch_seccion_reportes():
    with open("static/seccion_reportes.js", "r", encoding="utf-8") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    norm = content.replace("\r\n", "\n")

    # 1. Variable initialization
    t_init = "let valRetrabajoFinalizado = badgeNoAplicaRet;"
    r_init = "let valRetrabajoFinalizado = badgeNoAplicaRet;\n        let valRetrabajoUnidadEntregada = badgeNoAplicaRet;"
    assert t_init in norm, "t_init not found in seccion_reportes.js"
    norm = norm.replace(t_init, r_init, 1)

    # 2. Logic inside tieneReingreso
    t_logic = """            if (estaFinalizado) {
                valRetrabajoFinalizado = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">Sí</span>`;
            } else {
                valRetrabajoFinalizado = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No</span>`;
            }"""

    r_logic = """            if (estaFinalizado) {
                valRetrabajoFinalizado = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">Sí</span>`;
            } else {
                valRetrabajoFinalizado = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No</span>`;
            }

            // 5. Retrabajo / Unidad Entregada
            let entRaw = String(f.retrabajo_unidad_entregada || f.unidad_entregada_retrabajo || '').trim().toLowerCase();
            if (entRaw === 'sí' || entRaw === 'si') {
                valRetrabajoUnidadEntregada = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">Sí</span>`;
            } else if (entRaw === 'no') {
                valRetrabajoUnidadEntregada = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No</span>`;
            } else if (f.fecha_liberacion_retrabajo || rawEstRet === 'finalizado') {
                valRetrabajoUnidadEntregada = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">Sí</span>`;
            } else {
                valRetrabajoUnidadEntregada = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No</span>`;
            }"""

    assert t_logic in norm, "t_logic not found in seccion_reportes.js"
    norm = norm.replace(t_logic, r_logic, 1)

    # 3. Table cell inclusion
    t_td = '<td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valRetrabajoFinalizado}</td>'
    r_td = '<td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valRetrabajoFinalizado}</td>\n                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valRetrabajoUnidadEntregada}</td>'

    assert t_td in norm, "t_td not found in seccion_reportes.js"
    norm = norm.replace(t_td, r_td, 1)

    # 4. colspans in seccion_reportes.js
    norm = norm.replace('<td colspan="34"', '<td colspan="35"')

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open("static/seccion_reportes.js", "w", encoding="utf-8") as f:
        f.write(final)

    print("static/seccion_reportes.js updated successfully.")


if __name__ == "__main__":
    patch_administracion()
    patch_seccion_reportes()

