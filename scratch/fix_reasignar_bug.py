# -*- coding: utf-8 -*-
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = """    # Buscar correo del taller en usuarios.json
    usuarios = leer_json("usuarios.json")
    correo_taller = None
    for u in usuarios:
        if u.get("rol") == "proveedores":
            perf = u.get("datos_perfil", {})
            if perf.get("nombre_proveedor") == nombre_taller or u.get("nombre_proveedor") == nombre_taller:
                correo_taller = u.get("correo") or perf.get("correo")
                break"""

replacement = """    # Buscar correo del taller en usuarios.json
    usuarios_data = leer_json("usuarios.json")
    correo_taller = None
    target_taller = str(nombre_taller or "").strip().upper()
    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "proveedores":
            perf = u.get("datos_perfil", {})
            nom_prov = str(perf.get("nombre_proveedor") or u.get("nombre_proveedor") or "").strip().upper()
            user_prov = str(u.get("usuario") or "").strip().upper()
            if nom_prov == target_taller or user_prov == target_taller or (nom_prov and nom_prov in target_taller) or (target_taller and target_taller in nom_prov):
                correo_taller = perf.get("correo") or u.get("correo")
                break"""

if target in c:
    c = c.replace(target, replacement, 1)
    print("OK: Replaced target with LF")
elif target.replace('\n', '\r\n') in c:
    c = c.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'), 1)
    print("OK: Replaced target with CRLF")
else:
    print("ERROR: Target not found")

# Also enhance obtener_retrabajos_proveedor matching
target_prov_list = """    dp = session["usuario"].get("datos_perfil", {})
    mi_proveedor = str(dp.get("nombre_proveedor", "")).strip().upper()

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    filtrados = []
    for ret in todos:
        s2 = ret.get("seccion_2", {})
        prov_ret = str(s2.get("proveedor") or ret.get("proveedor", "")).strip().upper()
        estado = str(ret.get("estado", "")).strip()
        if prov_ret == mi_proveedor and estado in ["Reasignado", "Reasignado_Taller"]:
            filtrados.append(ret)"""

repl_prov_list = """    dp = session["usuario"].get("datos_perfil", {})
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
            filtrados.append(ret)"""

if target_prov_list in c:
    c = c.replace(target_prov_list, repl_prov_list, 1)
    print("OK: Replaced target_prov_list with LF")
elif target_prov_list.replace('\n', '\r\n') in c:
    c = c.replace(target_prov_list.replace('\n', '\r\n'), repl_prov_list.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_prov_list with CRLF")
else:
    print("ERROR: target_prov_list not found")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Saved rutas_reportes.py")

