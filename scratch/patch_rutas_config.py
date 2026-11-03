with open('rutas_configuracion.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    conf = obtener_configuracion()
    conf["limite_cotizaciones_caras"] = nuevo_limite
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    conf["actualizado_por"] = f"{subrol}: {session['usuario'].get('usuario')}"

    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Límite de cotizaciones caras actualizado a ${nuevo_limite:,.2f} MXN con éxito.",
        "limite_cotizaciones_caras": nuevo_limite
    })"""

replacement = """    conf = obtener_configuracion()
    conf["limite_cotizaciones_caras"] = nuevo_limite
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    conf["actualizado_por"] = f"{subrol}: {session['usuario'].get('usuario')}"

    escribir_json(CONFIG_FILE, conf)

    # Revaluar en tiempo real todas las cotizaciones aplicando las 3 reglas de negocio
    tickets_despachados = 0
    try:
        from rutas_facturas import revaluar_cotizaciones_por_limite
        tickets_despachados = revaluar_cotizaciones_por_limite(nuevo_limite)
    except Exception as e:
        print("Error revaluando cotizaciones por nuevo límite:", e)

    msg = f"Límite de cotizaciones caras actualizado a ${nuevo_limite:,.2f} MXN con éxito."
    if tickets_despachados > 0:
        msg += f" {tickets_despachados} cotización(es) previamente aprobadas por supervisión fueron canalizadas directo al taller."

    return jsonify({
        "status": "success",
        "message": msg,
        "limite_cotizaciones_caras": nuevo_limite,
        "tickets_liberados": tickets_despachados
    })"""

code = code.replace(target, replacement, 1)

with open('rutas_configuracion.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_configuracion.py actualizado con revaluar_cotizaciones_por_limite!")

