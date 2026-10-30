import re

# 1. Update static/seccion_reportes.js
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_block = '''        if (tieneReingreso) {
            // 1. Fecha / Retrabajo
            if (fechaRetRaw) {
                valFechaRetrabajo = `<strong style="color:#38bdf8; font-size:0.88em; white-space:nowrap;">${fechaRetRaw}</strong>`;
            } else {
                valFechaRetrabajo = `<span style="color:#f59e0b; font-size:0.85em; font-weight:bold;">En Asignación</span>`;
            }

            // 2. Tiempo en Taller / Reingreso
            if (fechaRetRaw) {
                let dInicio = new Date(fechaRetRaw);
                if (isNaN(dInicio)) dInicio = new Date(fechaRetRaw.replace(' ', 'T'));
                if (isNaN(dInicio)) dInicio = new Date(fechaRetRaw.replace(/-/g, '/'));

                let dFin = null;
                if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                    dFin = new Date(fechaFinRetRaw);
                    if (isNaN(dFin)) dFin = new Date(fechaFinRetRaw.replace(' ', 'T'));
                    if (isNaN(dFin)) dFin = new Date(fechaFinRetRaw.replace(/-/g, '/'));
                }

                let dComparar = dFin || new Date();
                if (!isNaN(dInicio) && !isNaN(dComparar) && dComparar >= dInicio) {
                    let diffMs = dComparar - dInicio;
                    let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    let diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    let sufijo = dFin ? '' : ' ⏱️';
                    let colorTxt = dFin ? '#4ade80' : '#eab308';
                    valTiempoReingreso = `<strong style="color:${colorTxt}; font-size:0.88em; white-space:nowrap;">${diffDays}d ${diffHours}h ${diffMinutes}m${sufijo}</strong>`;
                } else {
                    valTiempoReingreso = '<strong style="color:#eab308; font-size:0.88em; white-space:nowrap;">0d 0h 0m ⏱️</strong>';
                }
            } else {
                valTiempoReingreso = `<span style="color:#f59e0b; font-size:0.85em;">Esperando Ingreso</span>`;
            }

            // 3. Fecha de Finalizacion / Reingreso
            if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                valFechaFinReingreso = `<strong style="color:#4ade80; font-size:0.88em; white-space:nowrap;">${fechaFinRetRaw}</strong>`;
            } else {
                valFechaFinReingreso = `<span style="background:#eab308; color:#0b1c30; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;" title="La unidad se encuentra actualmente en proceso de retrabajo en el taller">En Proceso ⏱️</span>`;
            }
        }'''

new_block = '''        if (tieneReingreso) {
            // 1. Fecha / Retrabajo
            if (fechaRetRaw) {
                valFechaRetrabajo = `<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">${fechaRetRaw}</span>`;
            } else {
                valFechaRetrabajo = `<span style="color:#ffffff; font-size:0.9em;">En Asignación</span>`;
            }

            // 2. Tiempo en Taller / Reingreso
            if (fechaRetRaw) {
                let dInicio = new Date(fechaRetRaw);
                if (isNaN(dInicio)) dInicio = new Date(fechaRetRaw.replace(' ', 'T'));
                if (isNaN(dInicio)) dInicio = new Date(fechaRetRaw.replace(/-/g, '/'));

                let dFin = null;
                if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                    dFin = new Date(fechaFinRetRaw);
                    if (isNaN(dFin)) dFin = new Date(fechaFinRetRaw.replace(' ', 'T'));
                    if (isNaN(dFin)) dFin = new Date(fechaFinRetRaw.replace(/-/g, '/'));
                }

                let dComparar = dFin || new Date();
                if (!isNaN(dInicio) && !isNaN(dComparar) && dComparar >= dInicio) {
                    let diffMs = dComparar - dInicio;
                    let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    let diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    let sufijo = dFin ? '' : ' ⏱️';
                    valTiempoReingreso = `<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">${diffDays}d ${diffHours}h ${diffMinutes}m${sufijo}</span>`;
                } else {
                    valTiempoReingreso = '<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">0d 0h 0m ⏱️</span>';
                }
            } else {
                valTiempoReingreso = `<span style="color:#ffffff; font-size:0.9em;">Esperando Ingreso</span>`;
            }

            // 3. Fecha de Finalizacion / Reingreso
            if (fechaFinRetRaw && (rawEstRet === 'finalizado' || f.estado === 'Finalizado')) {
                valFechaFinReingreso = `<span style="color:#ffffff; font-size:0.9em; white-space:nowrap;">${fechaFinRetRaw}</span>`;
            } else {
                valFechaFinReingreso = `<span style="background:#eab308; color:#0b1c30; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;" title="La unidad se encuentra actualmente en proceso de retrabajo en el taller">En Proceso ⏱️</span>`;
            }
        }'''

# Replace in js
js_norm = js.replace('\r\n', '\n')
old_block_norm = old_block.replace('\r\n', '\n')
new_block_norm = new_block.replace('\r\n', '\n')

if old_block_norm in js_norm:
    js_norm = js_norm.replace(old_block_norm, new_block_norm, 1)
    print("Updated values to color: #ffffff in seccion_reportes.js")
else:
    print("WARNING: old_block_norm not found!")

old_tds = '''                <td style="vertical-align:top; padding-top:15px;">${valFechaRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valTiempoReingreso}</td>
                <td style="vertical-align:top; padding-top:15px;">${valFechaFinReingreso}</td>'''

new_tds = '''                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valTiempoReingreso}</td>
                <td style="vertical-align:top; padding-top:15px; color:#ffffff;">${valFechaFinReingreso}</td>'''

old_tds_norm = old_tds.replace('\r\n', '\n')
new_tds_norm = new_tds.replace('\r\n', '\n')

if old_tds_norm in js_norm:
    js_norm = js_norm.replace(old_tds_norm, new_tds_norm, 1)
    print("Updated <td> cells to color: #ffffff in seccion_reportes.js")
else:
    print("WARNING: old_tds_norm not found!")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(js_norm)

# 2. Bump version in templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'src="/static/seccion_reportes\.js\?v=\d+"', 'src="/static/seccion_reportes.js?v=1000015"', html)

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped seccion_reportes.js cache version in administracion.html to 1000015")

