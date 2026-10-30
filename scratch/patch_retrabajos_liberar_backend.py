# -*- coding: utf-8 -*-

# Update rutas_reportes.py
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update line 61 check
target_chk1 = """            if st_ret in ["pendiente", "reasignado"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_finalizacion_taller")):"""
repl_chk1 = """            if st_ret in ["pendiente", "reasignado", "por liberar", "por_liberar", "pendiente liberacion"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_liberacion")):"""

# 2. Update line 363 check
target_chk2 = """            if st_ret in ["pendiente", "reasignado"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_finalizacion_taller")):
                return True"""
repl_chk2 = """            if st_ret in ["pendiente", "reasignado", "por liberar", "por_liberar", "pendiente liberacion"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_liberacion")):
                return True"""

# 3. Update finalizar_retrabajo_taller and add por_liberar and liberar endpoints
target_finalizar = """    # Actualizar estado en retrabajos.json
    encontrado["estado"] = "Finalizado"
    encontrado["fecha_finalizacion_taller"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar estado en facturas.json y restaurar estado previo
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Finalizado"
            f["fecha_finalizacion_retrabajo"] = encontrado["fecha_finalizacion_taller"]
            f["estado"] = f.get("estado_previo") or "Archivado"
            break
    escribir_json("facturas.json", facturas_data)

    # Actualizar estado en reportes.json
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            r["estado"] = r.get("estado_previo") or "Finalizado"
            break
    escribir_json("reportes.json", reportes_data)

    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket
    return jsonify({
        "status": "success",
        "message": f"El retrabajo para el ticket {ticket_display} ha sido marcado como FINALIZADO exitosamente por el taller {taller_nombre}."
    })"""

repl_finalizar = """    # Actualizar estado en retrabajos.json a 'Por Liberar' (para que pase al rol de Supervisor en Liberar/Retrabajo)
    encontrado["estado"] = "Por Liberar"
    encontrado["fecha_finalizacion_taller"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar estado en facturas.json (mantiene f['estado'] en Retrabajo hasta que el supervisor lo libere)
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Por Liberar"
            f["fecha_finalizacion_retrabajo"] = encontrado["fecha_finalizacion_taller"]
            break
    escribir_json("facturas.json", facturas_data)

    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket
    return jsonify({
        "status": "success",
        "message": f"El retrabajo para el ticket {ticket_display} ha sido marcado como LISTO por el taller {taller_nombre} y enviado a Supervisión (Liberar/Retrabajo)."
    })


@reportes_bp.route("/api/garantia/supervisor/por_liberar", methods=["GET"])
def obtener_retrabajos_por_liberar():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    usuario_sesion = session["usuario"]
    dp = usuario_sesion.get("datos_perfil", {})
    subrol = dp.get("subrol", "")
    mi_cope = str(dp.get("cope", "")).strip().upper()
    copes_extra = [str(c).strip().upper() for c in dp.get("copes_asignados", [])]
    copes_permitidos = set([mi_cope] + copes_extra)

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    filtrados = []
    for ret in todos:
        st = str(ret.get("estado", "")).strip().lower()
        if st in ["por liberar", "por_liberar", "pendiente liberacion", "listo_taller"]:
            ret_cope = str(ret.get("cope", "")).strip().upper()
            if subrol in ["Jefatura", "Administrador"]:
                filtrados.append(ret)
            elif ret_cope in copes_permitidos or not ret_cope:
                filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })


@reportes_bp.route("/api/garantia/supervisor/liberar", methods=["POST"])
def liberar_retrabajo_supervisor():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    usuario_sesion = session["usuario"]
    dp = usuario_sesion.get("datos_perfil", {})
    sup_nombre = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip() or "Supervisor"

    data = request.get_json() or {}
    ticket = str(data.get("ticket", "")).strip().upper()
    if not ticket:
        return jsonify({"status": "error", "message": "Ticket no especificado"}), 400

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    encontrado = None
    for ret in todos:
        r_id = str(ret.get("id", "")).strip().upper()
        r_orig = str(ret.get("ticket_original", "")).strip().upper()
        r_tick = str(ret.get("ticket", "")).strip().upper()
        if ticket in [r_id, r_orig, r_tick] or (ticket.replace("REP-", "") in [r_id.replace("REP-", ""), r_orig.replace("REP-", "")]):
            encontrado = ret
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Reporte de retrabajo no encontrado"}), 404

    # 1. Actualizar estado en retrabajos.json a Finalizado
    encontrado["estado"] = "Finalizado"
    encontrado["fecha_liberacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encontrado["supervisor_libero"] = sup_nombre
    escribir_json("retrabajos.json", retrabajos_data)

    # 2. Actualizar estado en facturas.json y restaurar estado previo
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Finalizado"
            f["fecha_liberacion_retrabajo"] = encontrado["fecha_liberacion"]
            f["estado"] = f.get("estado_previo") or "Archivado"
            break
    escribir_json("facturas.json", facturas_data)

    # 3. Actualizar estado en reportes.json
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            r["estado"] = r.get("estado_previo") or "Finalizado"
            break
    escribir_json("reportes.json", reportes_data)

    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket
    return jsonify({
        "status": "success",
        "message": f"El retrabajo para el ticket {ticket_display} ha sido liberado exitosamente por el supervisor {sup_nombre}. La unidad concluye formalmente su garantía."
    })"""

is_crlf = '\r\n' in code
code_norm = code.replace('\r\n', '\n')

def replace_piece(src, t, r, name):
    t_n = t.replace('\r\n', '\n')
    r_n = r.replace('\r\n', '\n')
    if t_n in src:
        print(f"SUCCESS: {name}")
        return src.replace(t_n, r_n, 1)
    else:
        print(f"FAILED: {name}")
        return src

code_norm = replace_piece(code_norm, target_chk1, repl_chk1, "check 1")
code_norm = replace_piece(code_norm, target_chk2, repl_chk2, "check 2")
code_norm = replace_piece(code_norm, target_finalizar, repl_finalizar, "finalizar and liberar endpoints")

if is_crlf:
    final_code = code_norm.replace('\n', '\r\n')
else:
    final_code = code_norm

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(final_code)

print("rutas_reportes.py updated.")

# Update rutas_unidades_metricas.py
with open('rutas_unidades_metricas.py', 'r', encoding='utf-8') as f:
    um_code = f.read()

target_um = """        if st_ret in ["pendiente", "reasignado"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_finalizacion_taller")):"""
repl_um = """        if st_ret in ["pendiente", "reasignado", "por liberar", "por_liberar", "pendiente liberacion"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_liberacion")):"""

is_crlf_um = '\r\n' in um_code
um_norm = um_code.replace('\r\n', '\n')
um_norm = replace_piece(um_norm, target_um, repl_um, "rutas_unidades_metricas check")

if is_crlf_um:
    final_um = um_norm.replace('\n', '\r\n')
else:
    final_um = um_norm

with open('rutas_unidades_metricas.py', 'w', encoding='utf-8') as f:
    f.write(final_um)

print("rutas_unidades_metricas.py updated.")

