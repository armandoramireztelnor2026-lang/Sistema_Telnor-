import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Parchando rutas_reportes.py con enriquecimiento de retrabajo y cotización cara ---")

with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Enriquecer lista_reportes
target_lista = """            # Solo dejamos los reportes que coincidan con el COPE (o COPEs extra) del Supervisor
            data['reportes'] = [r for r in data.get('reportes', []) if r.get('cope') in copes_permitidos]
            
    return jsonify(data)"""

repl_lista = """            # Solo dejamos los reportes que coincidan con el COPE (o COPEs extra) del Supervisor
            data['reportes'] = [r for r in data.get('reportes', []) if r.get('cope') in copes_permitidos]

    try:
        retrabajos_data = leer_json("retrabajos.json").get("retrabajos", [])
        retrabajo_set = set()
        for ret in retrabajos_data:
            st = str(ret.get("estado", "")).strip().lower()
            if st != "cancelado":
                for k in ["ticket_original", "ticket", "id"]:
                    val = str(ret.get(k) or "").strip().upper()
                    if val:
                        retrabajo_set.add(val)
                        retrabajo_set.add(val.replace("REP-", ""))
        for r in data.get("reportes", []):
            r_id = str(r.get("id", "")).strip().upper()
            if r_id in retrabajo_set or r_id.replace("REP-", "") in retrabajo_set:
                r["es_retrabajo"] = True
                if not r.get("retrabajo"):
                    r["retrabajo"] = "Sí"
    except Exception as e:
        print(f"Error enriqueciendo reportes con retrabajo: {e}")
            
    return jsonify(data)"""

if target_lista in code:
    code = code.replace(target_lista, repl_lista, 1)
    print("✓ rutas_reportes.py: lista_reportes enriquecido con estatus de retrabajo")
else:
    print("! AVISO: target_lista no encontrado")

# 2. Enriquecer nuevo_retrabajo en guardar_retrabajo
target_nuevo_ret = """        "supervisor_usuario": sup_usuario,
        "supervisor_correo": sup_correo,
        "estado": "Pendiente",
        "seccion_1": seccion_1,
        "seccion_2": seccion_2
    }"""

repl_nuevo_ret = """        "supervisor_usuario": sup_usuario,
        "supervisor_correo": sup_correo,
        "estado": "Pendiente",
        "reactivado_desde_caras": bool(factura_correspondiente.get("reactivado_desde_caras") or reporte_encontrado.get("reactivado_desde_caras")),
        "seccion_1": seccion_1,
        "seccion_2": seccion_2
    }"""

if target_nuevo_ret in code:
    code = code.replace(target_nuevo_ret, repl_nuevo_ret, 1)
    print("✓ rutas_reportes.py: nuevo_retrabajo ahora almacena reactivado_desde_caras")
else:
    print("! AVISO: target_nuevo_ret no encontrado")

# 3. Enriquecer obtener_retrabajos_supervisor con reactivado_desde_caras
target_ret_sup = """    filtrados = []
    for ret in todos:
        ret_cope = str(ret.get("cope", "")).strip().upper()
        if subrol in ["Jefatura", "Administrador"]:
            filtrados.append(ret)
        elif ret_cope in copes_permitidos or not ret_cope:
            filtrados.append(ret)

    return jsonify({"""

repl_ret_sup = """    # Enriquecer con reactivado_desde_caras si aplica
    if facturas_data_cache is None:
        facturas_data_cache = leer_json("facturas.json").get("facturas", [])
    caras_set = set()
    for f_item in facturas_data_cache:
        if f_item.get("reactivado_desde_caras"):
            f_rep_id = str(f_item.get("id_reporte") or f_item.get("numero_reporte") or f_item.get("id") or "").strip().upper()
            if f_rep_id:
                caras_set.add(f_rep_id)
                caras_set.add(f_rep_id.replace("REP-", ""))

    filtrados = []
    for ret in todos:
        t_check = str(ret.get("ticket_original") or ret.get("ticket") or ret.get("id") or "").strip().upper()
        if t_check in caras_set or t_check.replace("REP-", "") in caras_set:
            ret["reactivado_desde_caras"] = True
        ret_cope = str(ret.get("cope", "")).strip().upper()
        if subrol in ["Jefatura", "Administrador"]:
            filtrados.append(ret)
        elif ret_cope in copes_permitidos or not ret_cope:
            filtrados.append(ret)

    return jsonify({"""

if target_ret_sup in code:
    code = code.replace(target_ret_sup, repl_ret_sup, 1)
    print("✓ rutas_reportes.py: obtener_retrabajos_supervisor enriquecido con reactivado_desde_caras")
else:
    print("! AVISO: target_ret_sup no encontrado")

# 4. Enriquecer obtener_retrabajos_proveedor con reactivado_desde_caras
target_ret_prov = """        if coincide and estado in ["reasignado", "reasignado_taller", "retrabajo"]:
            filtrados.append(ret)

    return jsonify({"""

repl_ret_prov = """        if coincide and estado in ["reasignado", "reasignado_taller", "retrabajo"]:
            f_asoc = facturas_dict.get(str(ret.get("factura_id", "")).strip().upper())
            if f_asoc and f_asoc.get("reactivado_desde_caras"):
                ret["reactivado_desde_caras"] = True
            filtrados.append(ret)

    return jsonify({"""

if target_ret_prov in code:
    code = code.replace(target_ret_prov, repl_ret_prov, 1)
    print("✓ rutas_reportes.py: obtener_retrabajos_proveedor enriquecido con reactivado_desde_caras")
else:
    print("! AVISO: target_ret_prov no encontrado")

# 5. Enriquecer obtener_retrabajos_por_liberar con reactivado_desde_caras
target_ret_lib = """            if subrol in ["Jefatura", "Administrador"]:
                filtrados.append(ret)
            elif ret_cope in copes_permitidos or not ret_cope:
                filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })"""

repl_ret_lib = """            f_id_lib = str(ret.get("factura_id", "")).strip().upper()
            try:
                for f_lib in leer_json("facturas.json").get("facturas", []):
                    if str(f_lib.get("id", "")).strip().upper() == f_id_lib or str(ret.get("ticket_original", "")).strip().upper() in str(f_lib.get("retro", "")).upper():
                        if f_lib.get("reactivado_desde_caras"):
                            ret["reactivado_desde_caras"] = True
                        break
            except Exception:
                pass
            if subrol in ["Jefatura", "Administrador"]:
                filtrados.append(ret)
            elif ret_cope in copes_permitidos or not ret_cope:
                filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })"""

if target_ret_lib in code:
    code = code.replace(target_ret_lib, repl_ret_lib, 1)
    print("✓ rutas_reportes.py: obtener_retrabajos_por_liberar enriquecido con reactivado_desde_caras")
else:
    print("! AVISO: target_ret_lib no encontrado")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("--- Completado enriquecimiento en rutas_reportes.py ---")

