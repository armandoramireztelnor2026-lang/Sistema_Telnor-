with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update nuevo_reporte
target_0 = """    # 0. Check if the unit is inactive or in Juridicos
    unidades_data = leer_json("unidades.json")
    if unidad_req in unidades_data:
        if unidades_data[unidad_req].get("Juridicos") == True:
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra en Jurídicos y no puede ser reportada."})
        if unidades_data[unidad_req].get("Estado") == "Inactiva":
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra Inhabilitada/Incosteable y no puede ser reportada."})"""

replacement_0 = """    # 0. Check if the unit is inactive, in Juridicos or in Reasignacion/Garantia
    unidades_data = leer_json("unidades.json")
    if unidad_req in unidades_data:
        if unidades_data[unidad_req].get("Juridicos") == True:
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra en Jurídicos y no puede ser reportada."})
        if unidades_data[unidad_req].get("Estado") == "Inactiva":
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra Inhabilitada/Incosteable y no puede ser reportada."})

    retrabajos_data = leer_json("retrabajos.json").get("retrabajos", [])
    u_req_norm = str(unidad_req).replace("8090-", "").strip()
    for ret in retrabajos_data:
        u_ret = str(ret.get("unidad", "")).replace("8090-", "").strip()
        st_ret = str(ret.get("estado", "")).strip().lower()
        if (u_ret == u_req_norm or (len(u_ret) >= 4 and len(u_req_norm) >= 4 and u_ret[-4:] == u_req_norm[-4:])):
            if st_ret in ["pendiente", "reasignado"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_finalizacion_taller")):
                return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra actualmente en proceso de reasignación / garantía y no puede ser reportada hasta que sea concluida por el taller."})"""

if target_0 in content:
    content = content.replace(target_0, replacement_0)
    print("Replaced nuevo_reporte check")
else:
    target_0_crlf = target_0.replace('\n', '\r\n')
    replacement_0_crlf = replacement_0.replace('\n', '\r\n')
    if target_0_crlf in content:
        content = content.replace(target_0_crlf, replacement_0_crlf)
        print("Replaced nuevo_reporte check (CRLF)")
    else:
        print("Warning: target_0 not found in rutas_reportes.py")

# 2. Update obtener_unidades
target_unidades = """        info["activa_en_taller"] = (est == "En Taller")
        info["inhabilitada_caras"] = (est == "Inhabilitada")"""

replacement_unidades = """        info["activa_en_taller"] = (est == "En Taller")
        info["activa_en_garantia"] = (est == "En Garantía")
        info["inhabilitada_caras"] = (est == "Inhabilitada")"""

if target_unidades in content:
    content = content.replace(target_unidades, replacement_unidades)
    print("Replaced obtener_unidades")
else:
    target_u_crlf = target_unidades.replace('\n', '\r\n')
    repl_u_crlf = replacement_unidades.replace('\n', '\r\n')
    if target_u_crlf in content:
        content = content.replace(target_u_crlf, repl_u_crlf)
        print("Replaced obtener_unidades (CRLF)")
    else:
        print("Warning: target_unidades not found in rutas_reportes.py")

# 3. Update is_unidad_active
target_active = """    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        if str(r.get("unidad")) == eco_4 and r.get("estado") != "Eliminado":
            if str(r.get("id")) not in facturas_report_ids:
                return True
                
    return False"""

replacement_active = """    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        if str(r.get("unidad")) == eco_4 and r.get("estado") != "Eliminado":
            if str(r.get("id")) not in facturas_report_ids:
                return True

    retrabajos_data = leer_json("retrabajos.json")
    for ret in retrabajos_data.get("retrabajos", []):
        u_ret = str(ret.get("unidad", "")).replace("8090-", "").strip()
        st_ret = str(ret.get("estado", "")).strip().lower()
        if len(u_ret) >= 4 and u_ret[-4:] == eco_4:
            if st_ret in ["pendiente", "reasignado"] or (st_ret not in ["finalizado", "cancelado"] and not ret.get("fecha_finalizacion_taller")):
                return True
                
    return False"""

if target_active in content:
    content = content.replace(target_active, replacement_active)
    print("Replaced is_unidad_active")
else:
    target_a_crlf = target_active.replace('\n', '\r\n')
    repl_a_crlf = replacement_active.replace('\n', '\r\n')
    if target_a_crlf in content:
        content = content.replace(target_a_crlf, repl_a_crlf)
        print("Replaced is_unidad_active (CRLF)")
    else:
        print("Warning: target_active not found in rutas_reportes.py")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated rutas_reportes.py successfully")

