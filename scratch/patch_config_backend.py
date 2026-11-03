import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('rutas_configuracion.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update calcular_metricas_presupuesto
old_calc = """def calcular_metricas_presupuesto(conf=None):
    if conf is None:
        conf = obtener_configuracion()
    presupuesto_total = float(conf.get("presupuesto_total", 500000.0) or 500000.0)

    facturas_data = leer_json(FACTURAS_FILE)
    facs = facturas_data.get("facturas", [])

    comprometido = 0.0
    confirmadas = []

    for fc in facs:
        # Excluir rechazadas o canceladas
        st = str(fc.get("estado", "")).strip().lower()
        if st in ["rechazada", "cancelada", "cancelado_cotizacion_cara"] or fc.get("cancelado"):
            continue

        es_confirmada = False
        if fc.get("aprobado_admin") is True or fc.get("aprobado_corp") is True:
            es_confirmada = True
        elif st in ["confirmada", "archivado", "revision_factura", "espera_aprobacion_pin", "retrabajo", "en asignacion/retrabajo"]:
            es_confirmada = True

        if es_confirmada:
            p = float(fc.get("precio", 0) or fc.get("precio_estimado", 0) or 0)
            comprometido += p
            confirmadas.append({
                "id": fc.get("id"),
                "id_reporte": fc.get("id_reporte") or fc.get("numero_reporte") or fc.get("id"),
                "unidad": fc.get("unidad") or "N/A",
                "proveedor": fc.get("proveedor") or fc.get("taller") or "N/A",
                "cope": fc.get("cope") or "N/A",
                "precio": p,
                "estado": fc.get("estado") or "Confirmada",
                "fecha": str(fc.get("timestamp_aprobacion") or fc.get("fecha_creacion") or fc.get("timestamp") or "").split("T")[0] or "--"
            })

    # Ordenar por fecha descendente
    confirmadas.sort(key=lambda x: str(x.get("id", "")), reverse=True)

    restante = max(0.0, presupuesto_total - comprometido)
    pct = round((comprometido / presupuesto_total) * 100, 2) if presupuesto_total > 0 else 0.0

    return {
        "presupuesto_total": presupuesto_total,
        "dinero_comprometido": comprometido,
        "presupuesto_restante": restante,
        "porcentaje_consumido": pct,
        "total_confirmadas": len(confirmadas),
        "cotizaciones_confirmadas": confirmadas
    }"""

new_calc = """def calcular_metricas_presupuesto(conf=None):
    if conf is None:
        conf = obtener_configuracion()
    presupuesto_total = float(conf.get("presupuesto_total", 500000.0) or 500000.0)
    ids_reseteados = set(str(i) for i in conf.get("ids_reseteados", []))
    fecha_reseteo = str(conf.get("fecha_reseteo_presupuesto", "")).strip()

    facturas_data = leer_json(FACTURAS_FILE)
    facs = facturas_data.get("facturas", [])

    comprometido = 0.0
    confirmadas = []

    for fc in facs:
        # Excluir rechazadas o canceladas
        st = str(fc.get("estado", "")).strip().lower()
        if st in ["rechazada", "cancelada", "cancelado_cotizacion_cara"] or fc.get("cancelado"):
            continue

        es_confirmada = False
        if fc.get("aprobado_admin") is True or fc.get("aprobado_corp") is True:
            es_confirmada = True
        elif st in ["confirmada", "archivado", "revision_factura", "espera_aprobacion_pin", "retrabajo", "en asignacion/retrabajo"]:
            es_confirmada = True

        if es_confirmada:
            fc_id = str(fc.get("id"))
            # Si el ticket ya formaba parte del ciclo reseteado por Jefatura, se excluye del consumo actual
            if fc_id in ids_reseteados:
                continue

            if fecha_reseteo:
                ts_factura = str(fc.get("timestamp_aprobacion") or fc.get("fecha") or fc.get("fecha_creacion") or "")
                if ts_factura and ts_factura < fecha_reseteo and not fc.get("nuevo_ciclo_presupuesto"):
                    continue

            p = float(fc.get("precio", 0) or fc.get("precio_estimado", 0) or 0)
            comprometido += p
            confirmadas.append({
                "id": fc.get("id"),
                "id_reporte": fc.get("id_reporte") or fc.get("numero_reporte") or fc.get("id"),
                "unidad": fc.get("unidad") or "N/A",
                "proveedor": fc.get("proveedor") or fc.get("taller") or "N/A",
                "cope": fc.get("cope") or "N/A",
                "precio": p,
                "estado": fc.get("estado") or "Confirmada",
                "fecha": str(fc.get("timestamp_aprobacion") or fc.get("fecha_creacion") or fc.get("timestamp") or "").split("T")[0] or "--"
            })

    # Ordenar por fecha descendente
    confirmadas.sort(key=lambda x: str(x.get("id", "")), reverse=True)

    restante = max(0.0, presupuesto_total - comprometido)
    pct = round((comprometido / presupuesto_total) * 100, 2) if presupuesto_total > 0 else 0.0

    return {
        "presupuesto_total": presupuesto_total,
        "dinero_comprometido": comprometido,
        "presupuesto_restante": restante,
        "porcentaje_consumido": pct,
        "total_confirmadas": len(confirmadas),
        "cotizaciones_confirmadas": confirmadas,
        "fecha_reseteo_presupuesto": conf.get("fecha_reseteo_presupuesto", "--"),
        "monto_reseteado_acumulado": float(conf.get("monto_reseteado_acumulado", 0.0) or 0.0)
    }"""

if old_calc in code:
    code = code.replace(old_calc, new_calc, 1)
    print("calcular_metricas_presupuesto actualizado con soporte de reseteo")
else:
    print("Aviso: No se encontró old_calc exacto")

# 2. Update GET /api/configuracion response to include envio_automatico_activo
old_get_config = """"cuentas_correo": conf.get("cuentas_correo", []),"""
new_get_config = """"cuentas_correo": conf.get("cuentas_correo", []),
            "envio_automatico_activo": conf.get("envio_automatico_activo", True),"""

if old_get_config in code:
    code = code.replace(old_get_config, new_get_config, 1)
    print("GET /api/configuracion actualizado con envio_automatico_activo")

# 3. Update activar_cuenta_correo to set envio_automatico_activo = True
old_activar_block = """    conf["correo_emisor"] = cuenta_seleccionada.get("correo")
    conf["codigo_emisor"] = cuenta_seleccionada.get("codigo")
    conf["servidor_smtp"] = cuenta_seleccionada.get("servidor_smtp", "smtp.gmail.com")
    conf["puerto_smtp"] = cuenta_seleccionada.get("puerto_smtp", 587)
    conf["nombre_remitente"] = cuenta_seleccionada.get("nombre", "Sistema Automotriz Telnor")
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {conf['correo_emisor']} activada como emisor principal del sistema.",
        "correo_activo": conf["correo_emisor"]
    })"""

new_activar_block = """    conf["correo_emisor"] = cuenta_seleccionada.get("correo")
    conf["codigo_emisor"] = cuenta_seleccionada.get("codigo")
    conf["servidor_smtp"] = cuenta_seleccionada.get("servidor_smtp", "smtp.gmail.com")
    conf["puerto_smtp"] = cuenta_seleccionada.get("puerto_smtp", 587)
    conf["nombre_remitente"] = cuenta_seleccionada.get("nombre", "Sistema Automotriz Telnor")
    conf["envio_automatico_activo"] = True
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {conf['correo_emisor']} activada para el envío de correos automáticos.",
        "correo_activo": conf["correo_emisor"],
        "envio_automatico_activo": True
    })


@configuracion_bp.route("/api/configuracion/correo/desactivar", methods=["POST"])
def desactivar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    cuenta_id = str(datos.get("id", "")).strip()
    correo = str(datos.get("correo", "")).strip().lower()

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])
    cuenta_desactivada = None

    for c in cuentas:
        if (cuenta_id and str(c.get("id")) == cuenta_id) or (correo and c.get("correo", "").lower() == correo):
            c["activa"] = False
            cuenta_desactivada = c

    if not cuenta_desactivada:
        return jsonify({"status": "error", "message": "Cuenta de correo no encontrada."}), 404

    # Pausar el emisor automático
    conf["envio_automatico_activo"] = False
    conf["correo_emisor_anterior"] = conf.get("correo_emisor")
    conf["correo_emisor"] = ""
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {cuenta_desactivada.get('correo')} desactivada. Los correos automáticos han sido pausados hasta activar una cuenta.",
        "correo_activo": "",
        "envio_automatico_activo": False
    })


@configuracion_bp.route("/api/configuracion/correo/eliminar", methods=["POST"])
def eliminar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    cuenta_id = str(datos.get("id", "")).strip()
    correo = str(datos.get("correo", "")).strip().lower()

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])
    if len(cuentas) <= 1:
        return jsonify({"status": "error", "message": "No se puede eliminar la única cuenta registrada."}), 400

    nuevas_cuentas = []
    eliminada = None
    for c in cuentas:
        if (cuenta_id and str(c.get("id")) == cuenta_id) or (correo and c.get("correo", "").lower() == correo):
            eliminada = c
        else:
            nuevas_cuentas.append(c)

    if not eliminada:
        return jsonify({"status": "error", "message": "Cuenta no encontrada."}), 404

    if eliminada.get("activa") or (conf.get("correo_emisor", "").lower() == eliminada.get("correo", "").lower()):
        nuevas_cuentas[0]["activa"] = True
        conf["correo_emisor"] = nuevas_cuentas[0]["correo"]
        conf["codigo_emisor"] = nuevas_cuentas[0]["codigo"]
        conf["servidor_smtp"] = nuevas_cuentas[0].get("servidor_smtp", "smtp.gmail.com")
        conf["puerto_smtp"] = nuevas_cuentas[0].get("puerto_smtp", 587)
        conf["envio_automatico_activo"] = True

    conf["cuentas_correo"] = nuevas_cuentas
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {eliminada.get('correo')} eliminada exitosamente.",
        "cuentas": nuevas_cuentas,
        "correo_activo": conf.get("correo_emisor", "")
    })"""

if old_activar_block in code:
    code = code.replace(old_activar_block, new_activar_block, 1)
    print("activar, desactivar y eliminar cuentas de correo integradas")

# 4. Add resetear_presupuesto endpoint
presupuesto_reset_endpoint = """
@configuracion_bp.route("/api/configuracion/presupuesto/resetear", methods=["POST"])
def resetear_presupuesto():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    conf = obtener_configuracion()
    metricas = calcular_metricas_presupuesto(conf)
    monto_utilizado_previo = float(metricas.get("dinero_comprometido", 0.0))

    facturas_data = leer_json(FACTURAS_FILE)
    facs = facturas_data.get("facturas", [])

    ids_confirmadas = []
    for fc in facs:
        st = str(fc.get("estado", "")).strip().lower()
        if st in ["rechazada", "cancelada", "cancelado_cotizacion_cara"] or fc.get("cancelado"):
            continue
        es_confirmada = False
        if fc.get("aprobado_admin") is True or fc.get("aprobado_corp") is True:
            es_confirmada = True
        elif st in ["confirmada", "archivado", "revision_factura", "espera_aprobacion_pin", "retrabajo", "en asignacion/retrabajo"]:
            es_confirmada = True
        if es_confirmada:
            ids_confirmadas.append(str(fc.get("id")))

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    usuario_nom = session["usuario"].get("usuario", "Jefatura")

    conf["fecha_reseteo_presupuesto"] = now_str
    conf["ids_reseteados"] = ids_confirmadas
    conf["monto_reseteado_acumulado"] = monto_utilizado_previo
    conf["reseteado_por"] = f"{subrol}: {usuario_nom}"
    conf["fecha_actualizacion"] = now_str
    conf["actualizado_por"] = f"{subrol}: {usuario_nom}"

    escribir_json(CONFIG_FILE, conf)

    metricas_nuevas = calcular_metricas_presupuesto(conf)

    return jsonify({
        "status": "success",
        "message": f"Presupuesto utilizado reseteado correctamente. Se eliminaron ${monto_utilizado_previo:,.2f} MXN del cálculo acumulado. Saldo disponible restablecido a ${metricas_nuevas['presupuesto_restante']:,.2f} MXN.",
        "presupuesto": metricas_nuevas
    })
"""

if 'def resetear_presupuesto():' not in code:
    pos_pres_save = code.find('def guardar_presupuesto():')
    pos_end_save = code.find('\n@configuracion_bp.route("/api/configuracion/limite_caras/guardar"', pos_pres_save)
    code = code[:pos_end_save] + presupuesto_reset_endpoint + '\n' + code[pos_end_save:]
    print("Endpoint /api/configuracion/presupuesto/resetear agregado")

with open('rutas_configuracion.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_configuracion.py actualizado con éxito!")

