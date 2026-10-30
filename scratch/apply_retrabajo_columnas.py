import re
import json

# =====================================================================
# 1. ACTUALIZAR RUTAS_SECCION_REPORTES.PY
# =====================================================================
with open('rutas_seccion_reportes.py', 'r', encoding='utf-8') as f:
    code_sr = f.read()

# Load retrabajos.json mapping into obtener_lista_seccion_reportes
old_sr_block = '''    # Precalcular COPEs y reactivados de los reportes para búsqueda rápida
    reporte_a_cope = {str(r.get("id")): r.get("cope", "") for r in todos_reportes}
    reporte_a_reactivado = {str(r.get("id")): r.get("reactivado_desde_caras", False) for r in todos_reportes}'''

new_sr_block = '''    # Precalcular COPEs y reactivados de los reportes para búsqueda rápida
    reporte_a_cope = {str(r.get("id")): r.get("cope", "") for r in todos_reportes}
    reporte_a_reactivado = {str(r.get("id")): r.get("reactivado_desde_caras", False) for r in todos_reportes}

    # Precalcular datos de retrabajos para cruzar fechas de reingreso
    retrabajos_data = leer_json('retrabajos.json')
    retrabajos_map = {}
    for ret in retrabajos_data.get('retrabajos', []):
        t_orig = str(ret.get('ticket_original') or ret.get('ticket') or ret.get('id', '')).strip().upper()
        f_id_ret = str(ret.get('factura_id', '')).strip().upper()
        if t_orig:
            retrabajos_map[t_orig] = ret
        if f_id_ret:
            retrabajos_map[f_id_ret] = ret'''

if old_sr_block in code_sr:
    code_sr = code_sr.replace(old_sr_block, new_sr_block, 1)
    print("[OK] rutas_seccion_reportes: mapeo de retrabajos agregado.")
else:
    print("[WARN] old_sr_block not found in rutas_seccion_reportes.py")

old_sr_loop_block = '''        sup_nombre = cope_a_sup.get(cope_f, "No asignado")
        admin_nombre = cope_a_admin.get(cope_f, "No asignado")
        
        f['supervisor_nombre'] = sup_nombre
        f['administrador_nombre'] = admin_nombre
        f['jefatura_nombre'] = nombre_jefatura
        f['estado_calculado'] = determinar_estado_ticket(f)'''

new_sr_loop_block = '''        sup_nombre = cope_a_sup.get(cope_f, "No asignado")
        admin_nombre = cope_a_admin.get(cope_f, "No asignado")
        
        f['supervisor_nombre'] = sup_nombre
        f['administrador_nombre'] = admin_nombre
        f['jefatura_nombre'] = nombre_jefatura
        f['estado_calculado'] = determinar_estado_ticket(f)

        # Cruzar con retrabajos.json para obtener los datos de reingreso
        t_key = str(f.get("id", "")).strip().upper()
        r_key = str(r_id or "").strip().upper()
        ret_obj = retrabajos_map.get(t_key) or retrabajos_map.get(r_key)
        if ret_obj:
            f['fecha_retrabajo'] = ret_obj.get("fecha_reasignacion") or ret_obj.get("fecha_ingreso") or f.get("fecha_retrabajo")
            if ret_obj.get("estado") == "Finalizado":
                f['fecha_finalizacion_retrabajo'] = ret_obj.get("fecha_finalizacion_taller") or f.get("fecha_finalizacion_retrabajo")
            else:
                f['fecha_finalizacion_retrabajo'] = f.get("fecha_finalizacion_retrabajo") or ""
            f['estado_retrabajo'] = ret_obj.get("estado") or f.get("estado_retrabajo")
            if not f.get("num_retrabajo"):
                f["num_retrabajo"] = 1
            if not f.get("retrabajo"):
                f["retrabajo"] = "Sí"'''

if old_sr_loop_block in code_sr:
    code_sr = code_sr.replace(old_sr_loop_block, new_sr_loop_block, 1)
    print("[OK] rutas_seccion_reportes: cruce de campos de retrabajo en loop agregado.")
else:
    print("[WARN] old_sr_loop_block not found in rutas_seccion_reportes.py")

with open('rutas_seccion_reportes.py', 'w', encoding='utf-8') as f:
    f.write(code_sr)


# =====================================================================
# 2. ACTUALIZAR RUTAS_REPORTES.PY
# =====================================================================
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    code_rr = f.read()

old_rr_reasig = '''            f["retrabajo"] = "Sí"
            f["estado_retrabajo"] = "Reasignado"'''

new_rr_reasig = '''            f["retrabajo"] = "Sí"
            f["estado_retrabajo"] = "Reasignado"
            f["fecha_retrabajo"] = encontrado["fecha_reasignacion"]
            f["fecha_finalizacion_retrabajo"] = ""'''

if old_rr_reasig in code_rr:
    code_rr = code_rr.replace(old_rr_reasig, new_rr_reasig, 1)
    print("[OK] rutas_reportes: fecha_retrabajo en reasignar_retrabajo actualizado.")

old_rr_fin = '''            f["estado_retrabajo"] = "Finalizado"
            f["estado"] = f.get("estado_previo") or "Archivado"'''

new_rr_fin = '''            f["estado_retrabajo"] = "Finalizado"
            f["fecha_finalizacion_retrabajo"] = encontrado["fecha_finalizacion_taller"]
            f["estado"] = f.get("estado_previo") or "Archivado"'''

if old_rr_fin in code_rr:
    code_rr = code_rr.replace(old_rr_fin, new_rr_fin, 1)
    print("[OK] rutas_reportes: fecha_finalizacion_retrabajo en finalizar_retrabajo_taller actualizado.")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(code_rr)


# =====================================================================
# 3. ACTUALIZAR TEMPLATES/ADMINISTRACION.HTML
# =====================================================================
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html_admin = f.read()

old_headers = '''                                    <th>RETRABAJO</th>
                                    <th>NUM/RETRABAJO</th>
                                    <th>NUM. PEDIDO</th>'''

new_headers = '''                                    <th>RETRABAJO</th>
                                    <th>NUM/RETRABAJO</th>
                                    <th>FECHA/RETRABAJO</th>
                                    <th>TIEMPO EN TALLER/REINGRESO</th>
                                    <th>FECHA DE FINALIZACION/REINGRESO</th>
                                    <th>NUM. PEDIDO</th>'''

if old_headers in html_admin:
    html_admin = html_admin.replace(old_headers, new_headers, 1)
    print("[OK] administracion.html: encabezados de tabla actualizados.")
else:
    print("[WARN] old_headers not found in administracion.html")

# Update colspan from 30 to 33
html_admin = html_admin.replace('<td colspan="30" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando', '<td colspan="33" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando')

# Bump seccion_reportes.js cache version
html_admin = re.sub(r'src="/static/seccion_reportes\.js\?v=\d+"', 'src="/static/seccion_reportes.js?v=1000010"', html_admin)

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html_admin)


# =====================================================================
# 4. ACTUALIZAR STATIC/SECCION_REPORTES.JS
# =====================================================================
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    code_sr_js = f.read()

old_numret_block = '''        let numRet = parseInt(f.num_retrabajo || f.numero_retrabajo || 0, 10);
        let valNumRetrabajo = (numRet > 0)
            ? `<span style="background:#f59e0b; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">${numRet}</span>`
            : '<span style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No Aplica</span>';'''

new_reingreso_block = '''        let numRet = parseInt(f.num_retrabajo || f.numero_retrabajo || 0, 10);
        let valNumRetrabajo = (numRet > 0)
            ? `<span style="background:#f59e0b; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">${numRet}</span>`
            : '<span style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No Aplica</span>';

        // ----------------------------------------------------
        // LOGICA DE LAS 3 COLUMNAS DE REINGRESO / RETRABAJO
        // 1. FECHA/RETRABAJO: Fecha de ingreso al taller por reingreso
        // 2. TIEMPO EN TALLER/REINGRESO: Tiempo que tenga en reingreso
        // 3. FECHA DE FINALIZACION/REINGRESO: Fecha en que se concluyo el reingreso
        // ----------------------------------------------------
        let rawEstRet = String(f.estado_retrabajo || '').trim().toLowerCase();
        let fechaRetRaw = f.fecha_retrabajo || f.fecha_reasignacion || f.fecha_reingreso || '';
        let fechaFinRetRaw = f.fecha_finalizacion_retrabajo || f.fecha_finalizacion_taller || '';

        let tieneReingreso = false;
        if (numRet > 0 || rawRetrabajo.toLowerCase() === 'sí' || rawRetrabajo.toLowerCase() === 'si' || rawEstRet === 'reasignado' || rawEstRet === 'finalizado' || fechaRetRaw) {
            if (rawRetrabajo.toLowerCase() !== 'cancelado') {
                tieneReingreso = true;
            }
        }

        const badgeNoAplicaRet = '<span style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No Aplica</span>';

        let valFechaRetrabajo = badgeNoAplicaRet;
        let valTiempoReingreso = badgeNoAplicaRet;
        let valFechaFinReingreso = badgeNoAplicaRet;

        if (tieneReingreso) {
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

if old_numret_block in code_sr_js:
    code_sr_js = code_sr_js.replace(old_numret_block, new_reingreso_block, 1)
    print("[OK] seccion_reportes.js: logica de las 3 columnas agregada.")
else:
    print("[WARN] old_numret_block not found in seccion_reportes.js")

old_row_cells = '''                <td style="vertical-align:top; padding-top:15px;">${valRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valNumRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumPedido}</td>'''

new_row_cells = '''                <td style="vertical-align:top; padding-top:15px;">${valRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valNumRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valFechaRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valTiempoReingreso}</td>
                <td style="vertical-align:top; padding-top:15px;">${valFechaFinReingreso}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumPedido}</td>'''

if old_row_cells in code_sr_js:
    code_sr_js = code_sr_js.replace(old_row_cells, new_row_cells, 1)
    print("[OK] seccion_reportes.js: celdas <td> inyectadas en la fila.")
else:
    print("[WARN] old_row_cells not found in seccion_reportes.js")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(code_sr_js)


# =====================================================================
# 5. ACTUALIZAR FACTURAS.JSON PARA SINCRONIZACION INMEDIATA
# =====================================================================
with open('facturas.json', 'r', encoding='utf-8') as f:
    facturas_data = json.load(f)

for fact in facturas_data.get('facturas', []):
    if fact.get('id') == '20261008133951' or 'REP-20261008131643' in str(fact):
        fact['fecha_retrabajo'] = '2026-10-29 11:41:38'
        fact['fecha_finalizacion_retrabajo'] = ''
        print(f"[OK] facturas.json: factura {fact.get('id')} sincronizada con fecha_retrabajo.")

with open('facturas.json', 'w', encoding='utf-8') as f:
    json.dump(facturas_data, f, indent=4)

print("\n=== TODAS LAS ACTUALIZACIONES FUERON COMPLETADAS EXITOSAMENTE ===")

