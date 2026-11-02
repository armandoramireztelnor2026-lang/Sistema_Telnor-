import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Aplicando regla: Ocultar tickets en retrabajo activo de Archivo General y Archivo Histórico ---")

# 1. static/facturas_principal.js
with open('static/facturas_principal.js', 'r', encoding='utf-8') as f:
    fp_code = f.read()

target_fp = """                    return; // skip active trays
                }

                if (f.estado === 'Archivado' || (rolUsuario === 'proveedores' && f.validacion_fiscal === 'Aprobada') || (rolUsuario === 'corporativos' && confirmadaTotal)) {"""

repl_fp = """                    return; // skip active trays
                }

                // ==========================================
                // REGLA: TICKET EN RETRABAJO ACTIVO
                // Si el ticket está en proceso de garantía / retrabajo activo,
                // se retira de Archivo General (Administración), de Archivo Histórico (Taller)
                // y de cualquier bandeja operativa normal (cotizaciones, facturas, doc contables).
                // Permanecerá exclusivamente en los botones de garantía (Retrabajo / Liberar Retrabajo)
                // hasta que el retrabajo sea finalizado mediante validación del código por el supervisor.
                // Una vez validado y finalizado el retrabajo, regresará al Archivo General y Archivo Histórico.
                // ==========================================
                let enRetrabajoActivo = Boolean(
                    f.en_retrabajo_activo ||
                    f.estado === 'Retrabajo' ||
                    f.estado === 'En Asignacion/Retrabajo' ||
                    f.estado_retrabajo === 'Pendiente' ||
                    f.estado_retrabajo === 'Reasignado' ||
                    f.estado_retrabajo === 'Por Liberar' ||
                    (f.retrabajo === 'Sí' && f.estado_retrabajo !== 'Finalizado' && f.estado_retrabajo !== 'Cancelado' && f.retrabajo_unidad_entregada !== 'Sí')
                );

                if (enRetrabajoActivo) {
                    return; // Vive exclusivamente en las bandejas/botones de Garantía mientras esté en proceso
                }

                if (f.estado === 'Archivado' || (rolUsuario === 'proveedores' && f.validacion_fiscal === 'Aprobada') || (rolUsuario === 'corporativos' && confirmadaTotal)) {"""

if target_fp in fp_code:
    fp_code = fp_code.replace(target_fp, repl_fp, 1)
    print("✓ static/facturas_principal.js: enRetrabajoActivo configurado para retirar de Archivo y bandejas normales")
else:
    print("! AVISO: target_fp no encontrado en static/facturas_principal.js")

# Asegurar que al regresar a archivo muestre badge de retrabajo (Finalizado)
fp_code = fp_code.replace(
    "let badgeRetrabajoArch = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí')",
    "let badgeRetrabajoArch = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí' || f.estado_retrabajo === 'Finalizado' || (f.num_retrabajo && Number(f.num_retrabajo) > 0))"
)
fp_code = fp_code.replace(
    "let badgeRetrabajoArchProv = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí')",
    "let badgeRetrabajoArchProv = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí' || f.estado_retrabajo === 'Finalizado' || (f.num_retrabajo && Number(f.num_retrabajo) > 0))"
)
fp_code = fp_code.replace(
    "let badgeRetrabajoArchCorp = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí')",
    "let badgeRetrabajoArchCorp = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí' || f.estado_retrabajo === 'Finalizado' || (f.num_retrabajo && Number(f.num_retrabajo) > 0))"
)

with open('static/facturas_principal.js', 'w', encoding='utf-8') as f:
    f.write(fp_code)

# 2. static/cotizaciones_10k.js
with open('static/cotizaciones_10k.js', 'r', encoding='utf-8') as f:
    c10_code = f.read()

target_c10 = """                let cancelado = f.estado === 'Cancelado_Cotizacion_Cara' || f.estado === 'Archivado' || f.estado === 'Rechazado_Con_Recomendaciones';
                return p >= 10001 && ap10k === false && supAsignado && !cancelado;"""

repl_c10 = """                let cancelado = f.estado === 'Cancelado_Cotizacion_Cara' || f.estado === 'Archivado' || f.estado === 'Rechazado_Con_Recomendaciones';
                let enRetrabajoActivo = Boolean(f.en_retrabajo_activo || f.estado === 'Retrabajo' || f.estado === 'En Asignacion/Retrabajo' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Por Liberar');
                return p >= 10001 && ap10k === false && supAsignado && !cancelado && !enRetrabajoActivo;"""

if target_c10 in c10_code:
    c10_code = c10_code.replace(target_c10, repl_c10, 1)
    with open('static/cotizaciones_10k.js', 'w', encoding='utf-8') as f:
        f.write(c10_code)
    print("✓ static/cotizaciones_10k.js: tickets en retrabajo excluidos de cotizaciones +10k")
else:
    print("! AVISO: target_c10 no encontrado en static/cotizaciones_10k.js")

# 3. rutas_reportes.py (garantizar estado 'Archivado' y en_retrabajo_activo False al liberar)
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    rr_code = f.read()

target_rr_lib = """            f["estado_retrabajo"] = "Finalizado"
            f["fecha_liberacion_retrabajo"] = fecha_ahora
            f["retrabajo_unidad_entregada"] = "Sí"
            f["fecha_entrega_retrabajo"] = fecha_ahora
            f["estado"] = f.get("estado_previo") or "Archivado"
            break"""

repl_rr_lib = """            f["estado_retrabajo"] = "Finalizado"
            f["fecha_liberacion_retrabajo"] = fecha_ahora
            f["retrabajo_unidad_entregada"] = "Sí"
            f["fecha_entrega_retrabajo"] = fecha_ahora
            f["estado"] = "Archivado"
            f["en_retrabajo_activo"] = False
            break"""

if target_rr_lib in rr_code:
    rr_code = rr_code.replace(target_rr_lib, repl_rr_lib, 1)
    with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
        f.write(rr_code)
    print("✓ rutas_reportes.py: al liberar se garantiza estado 'Archivado' para retorno a Archivo General")
else:
    print("! AVISO: target_rr_lib no encontrado en rutas_reportes.py")

# 4. rutas_facturas.py (enriquecer facturas con en_retrabajo_activo y filtrar de lista_archivados)
with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
    rf_code = f.read()

target_rf_list = """    # INYECTAR DATOS DEL REPORTE INICIAL
    try:
        reportes_data = leer_json("reportes.json").get("reportes", [])
        reportes_dict = {str(r.get("id")): r for r in reportes_data}
        
        for f in facturas:
            retro = f.get("retro", "")
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                ticket_id = match.group(1).strip()
                if ticket_id in reportes_dict:
                    f["reporte_inicial"] = reportes_dict[ticket_id]
    except Exception as e:
        pass

    return jsonify({"facturas": facturas})"""

repl_rf_list = """    # INYECTAR DATOS DEL REPORTE INICIAL
    try:
        reportes_data = leer_json("reportes.json").get("reportes", [])
        reportes_dict = {str(r.get("id")): r for r in reportes_data}
        
        for f in facturas:
            retro = f.get("retro", "")
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                ticket_id = match.group(1).strip()
                if ticket_id in reportes_dict:
                    f["reporte_inicial"] = reportes_dict[ticket_id]
    except Exception as e:
        pass

    # INYECTAR ESTADO DE RETRABAJO ACTIVO
    try:
        retrabajos_data = leer_json("retrabajos.json").get("retrabajos", [])
        activos_retrabajo = {}
        for ret in retrabajos_data:
            st = str(ret.get("estado", "")).strip().lower()
            if st not in ["finalizado", "cancelado"]:
                for key_name in ["id", "ticket", "ticket_original", "factura_id"]:
                    val = str(ret.get(key_name) or "").strip().upper()
                    if val:
                        activos_retrabajo[val] = ret.get("estado")
                        activos_retrabajo[val.replace("REP-", "")] = ret.get("estado")

        for f in facturas:
            fid = str(f.get("id", "")).strip().upper()
            frep = str(f.get("id_reporte") or f.get("numero_reporte") or "").strip().upper()
            retro = str(f.get("retro", "")).upper()
            m = re.search(r"\[TICKET:(.*?)\]", retro)
            fretro_rep = m.group(1).strip().upper() if m else ""

            keys_to_test = [fid, frep, frep.replace("REP-", ""), fretro_rep, fretro_rep.replace("REP-", "")]
            es_activo = False
            for k in keys_to_test:
                if k and k in activos_retrabajo:
                    es_activo = True
                    if not f.get("estado_retrabajo"):
                        f["estado_retrabajo"] = activos_retrabajo[k]
                    break

            st_ret = str(f.get("estado_retrabajo", "")).strip().lower()
            if st_ret in ["pendiente", "reasignado", "por liberar", "por_liberar", "listo_taller"]:
                es_activo = True
            if str(f.get("estado", "")).strip().lower() in ["retrabajo", "en asignacion/retrabajo"]:
                es_activo = True

            if es_activo and st_ret != "finalizado" and str(f.get("retrabajo_unidad_entregada", "")).strip().lower() not in ["sí", "si"]:
                f["en_retrabajo_activo"] = True
            else:
                f["en_retrabajo_activo"] = False
    except Exception as e:
        print(f"Error enriqueciendo facturas con retrabajo activo: {e}")

    return jsonify({"facturas": facturas})"""

if target_rf_list in rf_code:
    rf_code = rf_code.replace(target_rf_list, repl_rf_list, 1)
    print("✓ rutas_facturas.py: inyección de en_retrabajo_activo en listar_facturas")
else:
    print("! AVISO: target_rf_list no encontrado en rutas_facturas.py")

# Filtrar activos en lista_archivados
target_rf_arch = """        for r in reportes:
            if str(r.get('id')) == ticket_id:
                f['unidad'] = r.get('unidad', f.get('unidad', 'N/A'))
                break
                
    return jsonify({"status": "success", "archivados": archivados})"""

repl_rf_arch = """        for r in reportes:
            if str(r.get('id')) == ticket_id:
                f['unidad'] = r.get('unidad', f.get('unidad', 'N/A'))
                break

    try:
        retrabajos_data = leer_json("retrabajos.json").get("retrabajos", [])
        activos_set = set()
        for ret in retrabajos_data:
            st = str(ret.get("estado", "")).strip().lower()
            if st not in ["finalizado", "cancelado"]:
                for k in ["id", "ticket", "ticket_original", "factura_id"]:
                    val = str(ret.get(k) or "").strip().upper()
                    if val:
                        activos_set.add(val)
                        activos_set.add(val.replace("REP-", ""))

        archivados = [
            f for f in archivados
            if str(f.get("id", "")).strip().upper() not in activos_set
            and str(f.get("id_reporte", "") or f.get("numero_reporte", "")).strip().upper() not in activos_set
            and str(f.get("estado", "")).strip().lower() not in ["retrabajo", "en asignacion/retrabajo"]
            and str(f.get("estado_retrabajo", "")).strip().lower() not in ["pendiente", "reasignado", "por liberar", "por_liberar", "listo_taller"]
        ]
    except Exception as e:
        print(f"Error filtrando archivados activos en retrabajo: {e}")
                
    return jsonify({"status": "success", "archivados": archivados})"""

if target_rf_arch in rf_code:
    rf_code = rf_code.replace(target_rf_arch, repl_rf_arch, 1)
    print("✓ rutas_facturas.py: lista_archivados filtra tickets activos en retrabajo")
else:
    print("! AVISO: target_rf_arch no encontrado en rutas_facturas.py")

with open('rutas_facturas.py', 'w', encoding='utf-8') as f:
    f.write(rf_code)

# 5. static/script.js (refrescar facturas al marcar retrabajo finalizado por taller)
with open('static/script.js', 'r', encoding='utf-8') as f:
    sc_code = f.read()

target_sc_fin = """            alert(data.message || 'La unidad ha sido marcada como lista y enviada a Supervisión para su liberación.');
            if (typeof cargarRetrabajosProveedor === 'function') {
                cargarRetrabajosProveedor();
            }"""

repl_sc_fin = """            alert(data.message || 'La unidad ha sido marcada como lista y enviada a Supervisión para su liberación.');
            if (typeof cargarRetrabajosProveedor === 'function') {
                cargarRetrabajosProveedor();
            }
            if (typeof cargarFacturas === 'function') {
                cargarFacturas();
            }"""

if target_sc_fin in sc_code:
    sc_code = sc_code.replace(target_sc_fin, repl_sc_fin, 1)
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(sc_code)
    print("✓ static/script.js: marcarRetrabajoFinalizado ahora refresca facturas inmediatamente")
else:
    print("! AVISO: target_sc_fin no encontrado en static/script.js")

print("--- Parchado completado con éxito ---")

