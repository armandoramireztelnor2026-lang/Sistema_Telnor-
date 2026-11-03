import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. En confirmar_admin
old_confirmar = """    for f in data.get("facturas", []):
        if str(f["id"]) == str(factura_id):
            f["aprobado_admin"] = True"""

new_confirmar = """    for f in data.get("facturas", []):
        if str(f["id"]) == str(factura_id):
            precio_float = float(f.get("precio", 0) or f.get("precio_estimado", 0) or 0)

            # VALIDACIÓN ESTRICTA DE PRESUPUESTO (SUPERVISORES / JEFATURA):
            # Si el presupuesto no alcanza, el sistema no deja aprobarla y avisa que no hay presupuesto
            if not f.get("aprobado_admin"):
                try:
                    from rutas_configuracion import obtener_configuracion, calcular_metricas_presupuesto
                    conf = obtener_configuracion()
                    metricas = calcular_metricas_presupuesto(conf)
                    saldo_disponible = float(metricas.get("presupuesto_restante", 0.0))
                    if precio_float > saldo_disponible or saldo_disponible <= 0:
                        return jsonify({
                            "status": "error",
                            "message": f"🚫 Presupuesto Insuficiente: No se puede aprobar la cotización. El costo (${precio_float:,.2f} MXN) excede el saldo de presupuesto disponible ($ {saldo_disponible:,.2f} MXN). Contacte a Jefatura para ampliar o resetear el presupuesto."
                        }), 400
                except Exception as ex_pres:
                    print("Error verificando presupuesto en confirmar_admin:", ex_pres)

            f["aprobado_admin"] = True"""

assert old_confirmar in code, "old_confirmar not found"
code = code.replace(old_confirmar, new_confirmar, 1)
print("Validación de presupuesto agregada en confirmar_admin")

# 2. En aprobar_10k
old_aprobar_10k = """            if accion == "aprobar":
                # REGLA DE COTIZACIONES (EXCEPCIÓN CORPORATIVA PARA SUPLENCIA):"""

new_aprobar_10k = """            if accion == "aprobar":
                # VALIDACIÓN ESTRICTA DE PRESUPUESTO (SUPERVISORES / JEFATURA):
                if not f.get("aprobado_admin_10k") and not f.get("aprobado_corp"):
                    try:
                        from rutas_configuracion import obtener_configuracion, calcular_metricas_presupuesto
                        conf = obtener_configuracion()
                        metricas = calcular_metricas_presupuesto(conf)
                        saldo_disponible = float(metricas.get("presupuesto_restante", 0.0))
                        if precio_float > saldo_disponible or saldo_disponible <= 0:
                            return jsonify({
                                "status": "error",
                                "message": f"🚫 Presupuesto Insuficiente: No se puede aprobar la cotización. El costo (${precio_float:,.2f} MXN) excede el saldo de presupuesto disponible ($ {saldo_disponible:,.2f} MXN). Contacte a Jefatura para ampliar o resetear el presupuesto."
                            }), 400
                    except Exception as ex_pres:
                        print("Error verificando presupuesto en aprobar_10k:", ex_pres)

                # REGLA DE COTIZACIONES (EXCEPCIÓN CORPORATIVA PARA SUPLENCIA):"""

assert old_aprobar_10k in code, "old_aprobar_10k not found"
code = code.replace(old_aprobar_10k, new_aprobar_10k, 1)
print("Validación de presupuesto agregada en aprobar_10k")

with open('rutas_facturas.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_facturas.py actualizado con éxito!")

