import os
import re
import json

def patch_rutas_reportes():
    with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Update reasignar_retrabajo to save proveedor at root
    target_reasig = '''    encontrado["estado"] = "Reasignado"
    encontrado["fecha_reasignacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encontrado["supervisor_reasigno"] = sup_nombre
    escribir_json("retrabajos.json", retrabajos_data)'''

    replacement_reasig = '''    s2 = encontrado.get("seccion_2", {})
    nombre_taller = s2.get("proveedor") or encontrado.get("proveedor", "Taller")
    unidad = encontrado.get("unidad", "S/N")
    motivo_chofer = encontrado.get("motivo_chofer", "Falla persistente no reparada de manera correcta")
    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket

    encontrado["estado"] = "Reasignado"
    encontrado["fecha_reasignacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encontrado["supervisor_reasigno"] = sup_nombre
    if nombre_taller and nombre_taller != "Taller":
        encontrado["proveedor"] = nombre_taller
    escribir_json("retrabajos.json", retrabajos_data)'''

    if target_reasig in code:
        code = code.replace(target_reasig, replacement_reasig, 1)
        print("Updated reasignar_retrabajo in rutas_reportes.py")
    else:
        print("target_reasig not found in rutas_reportes.py")

    # 2. Update obtener_retrabajos_proveedor with robust matching
    old_func = '''@reportes_bp.route("/api/garantia/proveedor/lista", methods=["GET"])
def obtener_retrabajos_proveedor():
    if "usuario" not in session or session["usuario"].get("rol") != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    dp = session["usuario"].get("datos_perfil", {})
    mi_proveedor = str(dp.get("nombre_proveedor", "")).strip().upper()
    mi_usuario = str(session["usuario"].get("usuario", "")).strip().upper()

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    filtrados = []
    for ret in todos:
        s2 = ret.get("seccion_2", {})
        prov_ret = str(s2.get("proveedor") or ret.get("proveedor") or ret.get("taller") or "").strip().upper()
        estado = str(ret.get("estado", "")).strip()
        
        coincide = False
        if mi_proveedor and (prov_ret == mi_proveedor or prov_ret in mi_proveedor or mi_proveedor in prov_ret):
            coincide = True
        elif mi_usuario and (prov_ret == mi_usuario or mi_usuario in prov_ret):
            coincide = True

        if coincide and estado in ["Reasignado", "Reasignado_Taller"]:
            filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })'''

    new_func = '''@reportes_bp.route("/api/garantia/proveedor/lista", methods=["GET"])
def obtener_retrabajos_proveedor():
    if "usuario" not in session:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    rol = str(session["usuario"].get("rol", "")).strip().lower()
    if rol not in ["proveedores", "proveedor"]:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    import unicodedata
    def _norm(texto):
        if not texto:
            return ""
        t = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[^A-Z0-9]', '', t.upper())

    dp = session["usuario"].get("datos_perfil", {}) or {}
    mi_proveedor = str(dp.get("nombre_proveedor") or session["usuario"].get("nombre_proveedor") or dp.get("nombre") or session["usuario"].get("nombre", "")).strip()
    mi_usuario = str(session["usuario"].get("usuario", "")).strip()

    mi_prov_norm = _norm(mi_proveedor)
    mi_usr_norm = _norm(mi_usuario)

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    facturas_dict = {}
    try:
        facturas_data = leer_json("facturas.json")
        for f in facturas_data.get("facturas", []):
            fid = str(f.get("id", "")).strip().upper()
            if fid:
                facturas_dict[fid] = f
    except Exception:
        pass

    filtrados = []
    for ret in todos:
        s2 = ret.get("seccion_2", {}) or {}
        prov_ret = str(s2.get("proveedor") or ret.get("proveedor") or ret.get("taller") or "").strip()
        prov_user = str(ret.get("proveedor_usuario") or ret.get("proveedor_id") or "").strip()
        estado = str(ret.get("estado", "")).strip().lower()

        prov_ret_norm = _norm(prov_ret)
        prov_user_norm = _norm(prov_user)

        coincide = False
        if mi_prov_norm and prov_ret_norm:
            if prov_ret_norm == mi_prov_norm or prov_ret_norm in mi_prov_norm or mi_prov_norm in prov_ret_norm:
                coincide = True
        if not coincide and mi_usr_norm:
            if (prov_ret_norm and (prov_ret_norm == mi_usr_norm or mi_usr_norm in prov_ret_norm)) or \
               (prov_user_norm and (prov_user_norm == mi_usr_norm or mi_usr_norm in prov_user_norm)):
                coincide = True

        if not coincide and (mi_prov_norm or mi_usr_norm):
            f_id = str(ret.get("factura_id", "")).strip().upper()
            f_obj = facturas_dict.get(f_id)
            if f_obj:
                prov_f = _norm(f_obj.get("proveedor") or f_obj.get("taller") or "")
                if prov_f and mi_prov_norm and (prov_f == mi_prov_norm or prov_f in mi_prov_norm or mi_prov_norm in prov_f):
                    coincide = True
                elif prov_f and mi_usr_norm and (prov_f == mi_usr_norm or mi_usr_norm in prov_f):
                    coincide = True

        if coincide and estado in ["reasignado", "reasignado_taller", "retrabajo"]:
            filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })'''

    if old_func in code:
        code = code.replace(old_func, new_func, 1)
        print("Updated obtener_retrabajos_proveedor in rutas_reportes.py")
    else:
        print("old_func not found in rutas_reportes.py")

    with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
        f.write(code)

patch_rutas_reportes()

