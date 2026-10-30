# -*- coding: utf-8 -*-

with open("rutas_reportes.py", "r", encoding="utf-8") as f:
    content = f.read()

is_crlf = "\r\n" in content
norm = content.replace("\r\n", "\n")

# 1. Update imports
t_import = """from notificaciones import (
    enviar_correo_nueva_orden,
    enviar_correo_nuevo_ticket,
    enviar_correo_confirmacion_reporte,
    enviar_correo_ticket_rechazado,
    enviar_correo_retrabajo_taller,
    enviar_correo_cancelacion_retrabajo_chofer,
    enviar_correo_retrabajo_exitoso_supervisor,
)"""

r_import = """import random
from notificaciones import (
    enviar_correo_nueva_orden,
    enviar_correo_nuevo_ticket,
    enviar_correo_confirmacion_reporte,
    enviar_correo_ticket_rechazado,
    enviar_correo_retrabajo_taller,
    enviar_correo_cancelacion_retrabajo_chofer,
    enviar_correo_retrabajo_exitoso_supervisor,
    enviar_correo_retrabajo_listo_chofer,
    enviar_correo_retrabajo_listo_taller,
    enviar_correo_retrabajo_listo_supervisor_respaldo,
)"""

assert t_import in norm, "t_import not found"
norm = norm.replace(t_import, r_import, 1)
print("Imports updated successfully")

# 2. Update finalizar_retrabajo_taller
t_finalizar = """@reportes_bp.route("/api/garantia/taller/finalizar", methods=["POST"])
def finalizar_retrabajo_taller():
    if "usuario" not in session or session["usuario"].get("rol") != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

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

    dp = session["usuario"].get("datos_perfil", {})
    taller_nombre = dp.get("nombre_proveedor", "Taller")

    # Actualizar estado en retrabajos.json a 'Por Liberar' (para que pase al rol de Supervisor en Liberar/Retrabajo)
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
    })"""

r_finalizar = """@reportes_bp.route("/api/garantia/taller/finalizar", methods=["POST"])
def finalizar_retrabajo_taller():
    if "usuario" not in session or session["usuario"].get("rol") != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

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

    dp = session["usuario"].get("datos_perfil", {})
    taller_nombre = dp.get("nombre_proveedor", "Taller")

    # Generar códigos de validación de 6 dígitos: uno al chofer y otro al supervisor de respaldo
    codigo_chofer = f"{random.randint(100000, 999999)}"
    codigo_supervisor = f"{random.randint(100000, 999999)}"

    # Buscar datos del chofer (sección 1 o reportes.json)
    seccion_1 = encontrado.get("seccion_1") or {}
    nombre_chofer = seccion_1.get("empleado")
    correo_chofer = seccion_1.get("email")

    if not correo_chofer or not nombre_chofer:
        reportes_data = leer_json("reportes.json")
        for r in reportes_data.get("reportes", []):
            r_id = str(r.get("id", "")).strip().upper()
            if r_id == ticket or r_id == str(encontrado.get("ticket_original", "")).strip().upper():
                if not correo_chofer: correo_chofer = r.get("email") or r.get("correo")
                if not nombre_chofer: nombre_chofer = r.get("empleado")
                break

    if not correo_chofer:
        correo_chofer = "armandoramireztelnor2026@gmail.com"
    if not nombre_chofer:
        nombre_chofer = "Chofer"

    # Actualizar estado en retrabajos.json a 'Por Liberar' con sus códigos
    encontrado["estado"] = "Por Liberar"
    encontrado["fecha_finalizacion_taller"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encontrado["codigo_chofer"] = codigo_chofer
    encontrado["codigo_supervisor"] = codigo_supervisor
    encontrado["chofer"] = nombre_chofer
    encontrado["correo_chofer"] = correo_chofer
    encontrado["unidad_entregada"] = "No"
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar estado en facturas.json (mantiene f['estado'] en Retrabajo hasta que el supervisor lo valide)
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Por Liberar"
            f["fecha_finalizacion_retrabajo"] = encontrado["fecha_finalizacion_taller"]
            f["codigo_chofer_retrabajo"] = codigo_chofer
            f["codigo_supervisor_retrabajo"] = codigo_supervisor
            f["retrabajo_unidad_entregada"] = "No"
            break
    escribir_json("facturas.json", facturas_data)

    unidad_str = encontrado.get("unidad") or "N/A"
    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket

    # Enviar notificaciones por correo:
    # 1. Al Chofer con su código de validación
    try:
        enviar_correo_retrabajo_listo_chofer(
            correo_chofer=correo_chofer,
            nombre_chofer=nombre_chofer,
            ticket=ticket_display,
            unidad=unidad_str,
            nombre_taller=taller_nombre,
            codigo_chofer=codigo_chofer
        )
    except Exception as e:
        print(f"Error al enviar correo de retrabajo listo al chofer: {e}")

    # 2. Al Taller confirmando la conclusión
    correo_taller = dp.get("correo") or session["usuario"].get("correo")
    if not correo_taller:
        usuarios_data = leer_json("usuarios.json")
        for u in usuarios_data.get("usuarios", []):
            if u.get("usuario") == session["usuario"].get("usuario"):
                correo_taller = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                break
    if not correo_taller:
        correo_taller = "armandoramireztelnor2026@gmail.com"

    try:
        enviar_correo_retrabajo_listo_taller(
            correo_taller=correo_taller,
            nombre_taller=taller_nombre,
            ticket=ticket_display,
            unidad=unidad_str,
            nombre_chofer=nombre_chofer
        )
    except Exception as e:
        print(f"Error al enviar correo de confirmación de retrabajo listo al taller: {e}")

    # 3. Al Supervisor de respaldo con su código de respaldo
    correo_supervisor = encontrado.get("supervisor_correo")
    nombre_supervisor = encontrado.get("supervisor_asignado") or "Supervisor"
    if not correo_supervisor:
        usuarios_data = leer_json("usuarios.json")
        sup_target = encontrado.get("supervisor_usuario")
        for u in usuarios_data.get("usuarios", []):
            if (sup_target and u.get("usuario") == sup_target) or (u.get("rol") == "administracion" and u.get("datos_perfil", {}).get("subrol") == "Supervisor"):
                correo_supervisor = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                nombre_supervisor = f"{u.get('datos_perfil', {}).get('nombres', '')} {u.get('datos_perfil', {}).get('apellido_paterno', '')}".strip() or nombre_supervisor
                if correo_supervisor:
                    break
    if not correo_supervisor:
        correo_supervisor = "armandoramireztelnor2026@gmail.com"

    try:
        enviar_correo_retrabajo_listo_supervisor_respaldo(
            correo_supervisor=correo_supervisor,
            nombre_supervisor=nombre_supervisor,
            ticket=ticket_display,
            unidad=unidad_str,
            nombre_taller=taller_nombre,
            nombre_chofer=nombre_chofer,
            codigo_supervisor=codigo_supervisor
        )
    except Exception as e:
        print(f"Error al enviar correo de código de respaldo al supervisor: {e}")

    return jsonify({
        "status": "success",
        "message": f"Unidad marcada como LISTA. Se envió código de validación al chofer ({nombre_chofer}) y código de respaldo al supervisor ({nombre_supervisor}) para su liberación y entrega."
    })"""

assert t_finalizar in norm, "t_finalizar not found"
norm = norm.replace(t_finalizar, r_finalizar, 1)
print("finalizar_retrabajo_taller updated successfully")

# 3. Update liberar_retrabajo_supervisor
t_liberar = """@reportes_bp.route("/api/garantia/supervisor/liberar", methods=["POST"])
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

r_liberar = """@reportes_bp.route("/api/garantia/supervisor/liberar", methods=["POST"])
def liberar_retrabajo_supervisor():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    usuario_sesion = session["usuario"]
    dp = usuario_sesion.get("datos_perfil", {})
    sup_nombre = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip() or "Supervisor"

    data = request.get_json() or {}
    ticket = str(data.get("ticket", "")).strip().upper()
    codigo_ingresado = str(data.get("codigo", "")).strip()

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

    # Validar código (código del chofer o código de respaldo del supervisor)
    cod_chofer = str(encontrado.get("codigo_chofer", "")).strip()
    cod_super = str(encontrado.get("codigo_supervisor", "")).strip()

    es_valido = False
    tipo_codigo = ""

    if cod_chofer or cod_super:
        if not codigo_ingresado:
            return jsonify({
                "status": "error",
                "message": "Debes ingresar el código de validación (proporcionado por el chofer o el código de respaldo de supervisión)."
            }), 400

        if cod_chofer and codigo_ingresado.upper() == cod_chofer.upper():
            es_valido = True
            tipo_codigo = "Código de Chofer"
        elif cod_super and codigo_ingresado.upper() == cod_super.upper():
            es_valido = True
            tipo_codigo = "Código de Respaldo de Supervisión"

        if not es_valido:
            return jsonify({
                "status": "error",
                "message": "❌ Código de validación incorrecto. Ingresa el código recibido por el chofer o el código de respaldo del supervisor."
            }), 400
    else:
        # Compatibilidad con tickets previos sin código registrado
        es_valido = True
        tipo_codigo = "Autorización Directa"

    fecha_ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Actualizar estado en retrabajos.json a Finalizado y Entregado
    encontrado["estado"] = "Finalizado"
    encontrado["fecha_liberacion"] = fecha_ahora
    encontrado["supervisor_libero"] = sup_nombre
    encontrado["unidad_entregada"] = "Sí"
    encontrado["fecha_entrega"] = fecha_ahora
    encontrado["codigo_validado_por"] = sup_nombre
    encontrado["tipo_codigo_validado"] = tipo_codigo
    escribir_json("retrabajos.json", retrabajos_data)

    # 2. Actualizar estado en facturas.json y marcar entrega
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Finalizado"
            f["fecha_liberacion_retrabajo"] = fecha_ahora
            f["retrabajo_unidad_entregada"] = "Sí"
            f["fecha_entrega_retrabajo"] = fecha_ahora
            f["estado"] = f.get("estado_previo") or "Archivado"
            break
    escribir_json("facturas.json", facturas_data)

    # 3. Actualizar estado en reportes.json y marcar entrega
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            r["estado"] = r.get("estado_previo") or "Finalizado"
            r["entregado"] = "Sí"
            r["retrabajo_entregado"] = "Sí"
            r["fecha_entrega"] = fecha_ahora
            break
    escribir_json("reportes.json", reportes_data)

    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket
    return jsonify({
        "status": "success",
        "message": f"Código validado exitosamente ({tipo_codigo}). El retrabajo para el ticket {ticket_display} ha sido liberado por el supervisor {sup_nombre} y la unidad quedó marcada como ENTREGADA."
    })"""

assert t_liberar in norm, "t_liberar not found"
norm = norm.replace(t_liberar, r_liberar, 1)
print("liberar_retrabajo_supervisor updated successfully")

final = norm.replace("\n", "\r\n") if is_crlf else norm
with open("rutas_reportes.py", "w", encoding="utf-8") as f:
    f.write(final)

print("rutas_reportes.py updated.")

