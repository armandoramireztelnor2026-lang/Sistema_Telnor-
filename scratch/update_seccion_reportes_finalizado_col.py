# -*- coding: utf-8 -*-
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Colspan in cargarSeccionReportes
t_cs1 = 'tbody.innerHTML = `<tr><td colspan="33" style="text-align: center; color: #a3b1c6; padding: 20px;">No se encontraron resultados.</td></tr>`;'
r_cs1 = 'tbody.innerHTML = `<tr><td colspan="34" style="text-align: center; color: #a3b1c6; padding: 20px;">No se encontraron resultados.</td></tr>`;'

# 2. Variable declarations
t_vars = """        let valFechaRetrabajo = badgeNoAplicaRet;
        let valTiempoReingreso = badgeNoAplicaRet;
        let valFechaFinReingreso = badgeNoAplicaRet;"""

r_vars = """        let valFechaRetrabajo = badgeNoAplicaRet;
        let valTiempoReingreso = badgeNoAplicaRet;
        let valFechaFinReingreso = badgeNoAplicaRet;
        let valRetrabajoFinalizado = badgeNoAplicaRet;"""

# 3. Calculation inside if (tieneReingreso)
t_calc = """            // 3. Fecha de Finalizacion / Reingreso
            if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                valFechaFinReingreso = `<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">${fechaFinRetRaw}</span>`;
            } else {
                valFechaFinReingreso = `<span style="background:#eab308; color:#0b1c30; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;" title="La unidad se encuentra actualmente en proceso de retrabajo en el taller">En Proceso ⏱️</span>`;
            }
        }"""

r_calc = """            // 3. Fecha de Finalizacion / Reingreso
            if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                valFechaFinReingreso = `<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">${fechaFinRetRaw}</span>`;
            } else {
                valFechaFinReingreso = `<span style="background:#eab308; color:#0b1c30; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;" title="La unidad se encuentra actualmente en proceso de retrabajo en el taller">En Proceso ⏱️</span>`;
            }

            // 4. Retrabajo Finalizado (Sí con círculo verde, No con círculo rojo, No Aplica)
            let estaFinalizado = Boolean(fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado' || f.estado === 'Archivado' || f.estado === 'Finalizado / Histórico'));
            if (rawEstRet === 'finalizado') {
                estaFinalizado = true;
            }

            if (estaFinalizado) {
                valRetrabajoFinalizado = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-flex; align-items:center; gap:6px;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#4ade80; box-shadow:0 0 6px #4ade80;"></span> Sí</span>`;
            } else {
                valRetrabajoFinalizado = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-flex; align-items:center; gap:6px;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#f87171; box-shadow:0 0 6px #f87171;"></span> No</span>`;
            }
        }"""

# 4. Table cell in rowHtml
t_td = """                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaFinReingreso}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumPedido}</td>"""

r_td = """                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaFinReingreso}</td>
                <td class="td-amarillo col-amarillo" style="vertical-align:top; padding-top:15px; color:#ffffff;">${valRetrabajoFinalizado}</td>
                <td class="td-negro col-negro" style="vertical-align:top; padding-top:15px; color:#ffffff;">${htmlNumPedido}</td>"""

# 5. Colspan in no results row
t_cs2 = 'filaSinResultados.innerHTML = `<td colspan="30" style="text-align: center; color: #a3b1c6; padding: 25px; font-weight: bold; background: #0f172a;">🔍 No se encontraron tickets con los filtros seleccionados.</td>`;'
r_cs2 = 'filaSinResultados.innerHTML = `<td colspan="34" style="text-align: center; color: #a3b1c6; padding: 25px; font-weight: bold; background: #0f172a;">🔍 No se encontraron tickets con los filtros seleccionados.</td>`;'

is_crlf = '\r\n' in text
text_norm = text.replace('\r\n', '\n')

def replace_chunk(content, t, r, desc):
    t_n = t.replace('\r\n', '\n')
    r_n = r.replace('\r\n', '\n')
    if t_n in content:
        print(f"SUCCESS: {desc}")
        return content.replace(t_n, r_n, 1)
    else:
        print(f"FAILED: {desc}")
        return content

text_norm = replace_chunk(text_norm, t_cs1, r_cs1, "colspan 1")
text_norm = replace_chunk(text_norm, t_vars, r_vars, "variable declaration")
text_norm = replace_chunk(text_norm, t_calc, r_calc, "retrabajo finalizado calculation")
text_norm = replace_chunk(text_norm, t_td, r_td, "table td insertion")
text_norm = replace_chunk(text_norm, t_cs2, r_cs2, "colspan 2")

if is_crlf:
    final_text = text_norm.replace('\n', '\r\n')
else:
    final_text = text_norm

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(final_text)

print("seccion_reportes.js update complete.")

