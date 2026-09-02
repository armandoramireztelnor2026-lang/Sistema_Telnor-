def nueva_factura():
    if "usuario" not in session or session["usuario"]["rol"] != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"})

    proveedor = session["usuario"]["datos_perfil"]["nombre_proveedor"]
    unidad_sola = request.form.get("unidad")
    unidad = f"8090-{unidad_sola}"

    precio_str = request.form.get("precio", "0")
    precio_limpio = "".join(c for c in precio_str if c.isdigit() or c == ".")
    precio_float = float(precio_limpio)
    necesita_corp = precio_float >= 10001.0
    
    retro = request.form.get("retro", "")
    compania_asignada = "RUMN"
    import re
    match = re.search(r"\[TICKET:(.*?)\]", retro)
    if match:
        ticket_id = match.group(1).strip()
        rep_data = leer_json("reportes.json")
        for r in rep_data.get("reportes", []):
            if str(r.get("id")) == str(ticket_id):
                compania_asignada = r.get("compania", "RUMN")
                break

    nueva_factura = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "proveedor": proveedor,
        "unidad": unidad,
        "responsable": request.form.get("responsable"),
        "telefono": request.form.get("telefono"),
        "titulo": request.form.get("titulo"),
        "retro": retro,
        "diagnostico": request.form.get("diagnostico", ""),
        "trabajo_realizar": request.form.get("trabajo_realizar", ""),
        "mantenimiento": request.form.get("mantenimiento"),
        "precio": precio_float,
        "fecha": request.form.get("fecha"),
        "numero_orden": "",
        "compania": compania_asignada,
        "aprobado_admin": False,
        "aprobado_corp": not necesita_corp,
        "timestamp": datetime.datetime.now().isoformat(),
        "estado_custom": "",
        "fotos_cotizacion": [],
        "fotos_evidencia": [],
        "codigo_liberacion": "",
        "entregado": "No",
    }

    for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
        archivos = request.files.getlist(tipo)
        for archivo in archivos:
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                nombre_unico = f"{tipo}_{nueva_factura['id']}_{filename}"
                archivo.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                nueva_factura[tipo].append(nombre_unico)

    data = leer_json("facturas.json")
    data.setdefault("facturas", []).append(nueva_factura)
    escribir_json("facturas.json", data)

    usuarios_data = leer_json("usuarios.json")
    admins_data = []
    corps_data = []
    
    proveedor_ciudad = session["usuario"]["datos_perfil"].get("ciudad", "")

    for u in usuarios_data.get("usuarios", []):
        if u["rol"] == "administracion":
            subrol = u["datos_perfil"].get("subrol", "Administración")
            ciudad_admin = u["datos_perfil"].get("ciudad", "")
            
            # Solo notificar a la Jefatura general o al Supervisor local
            if subrol == "Jefatura" or ciudad_admin == proveedor_ciudad:
                correo = u["datos_perfil"].get("correo")
                if correo:
                    nombre = f"{u['datos_perfil'].get('nombres', '')} {u['datos_perfil'].get('apellido_paterno', '')}".strip()
                    admins_data.append({"correo": correo, "nombre": nombre, "puesto": subrol})

        elif u["rol"] == "corporativos":
            correo = u["datos_perfil"].get("correo")
            if correo:
                nombre = f"{u['datos_perfil'].get('nombres', '')} {u['datos_perfil'].get('apellido_paterno', '')}".strip()
                corps_data.append({"correo": correo, "nombre": nombre})

    if admins_data: enviar_correo_nueva_factura(admins_data, proveedor, unidad_sola, precio_float)
    if necesita_corp and corps_data: enviar_correo_nueva_factura_corp(corps_data, proveedor, unidad_sola, precio_float)

    correo_proveedor = session["usuario"]["datos_perfil"].get("correo")
    if correo_proveedor and correo_proveedor.strip():
        enviar_correo_confirmacion_factura(correo_proveedor, proveedor, unidad_sola, precio_float)

    return jsonify({"status": "success", "message": "Cotización enviada correctamente a revisión."})


