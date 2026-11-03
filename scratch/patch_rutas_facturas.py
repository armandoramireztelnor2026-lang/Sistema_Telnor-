import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
    code = f.read()

functions_to_add = '''
def despachar_orden_al_taller(f):
    """
    Despacha las notificaciones por correo para que el taller comience a trabajar
    y para que el administrador quede avisado de la espera de liberación contable (Doc 50).
    """
    try:
        from notificaciones import enviar_correo_taller_aprobado, enviar_correo_esperando_liberacion
        cope_fact = obtener_cope_de_factura(f)
        correo_admin, nombre_admin = encontrar_admin_por_cope(cope_fact)
        nombre_sup = f.get("supervisor_aprobador") or f.get("responsable") or "Supervisor"

        if correo_admin and f.get("liberado_admin") is False:
            try:
                enviar_correo_esperando_liberacion(
                    correo_admin,
                    nombre_admin,
                    f.get("id_reporte", f.get("id", "N/A")),
                    f.get("unidad", ""),
                    f.get("numero_orden", "N/A"),
                    f.get("numero_cotizacion_asignacion", "N/A"),
                    nombre_supervisor=nombre_sup
                )
            except Exception as e:
                print("Error enviando esperando liberacion:", e)

        proveedor_nombre = f.get('proveedor', '')
        usuarios_data = leer_json("usuarios.json")
        correo_prov = ""
        for u in usuarios_data.get("usuarios", []):
            if u.get('rol') == 'proveedores' and u.get('datos_perfil', {}).get('nombre_proveedor') == proveedor_nombre:
                correo_prov = u.get('datos_perfil', {}).get('correo', '')
                break

        if correo_prov:
            vehiculo_info = f.get("vehiculo", "Vehículo no especificado")
            enviar_correo_taller_aprobado(
                correo_prov,
                proveedor_nombre,
                f.get("id", "N/A"),
                f.get("unidad", "S/N"),
                vehiculo_info,
                nombre_supervisor=nombre_sup
            )
    except Exception as e:
        print("Error en despachar_orden_al_taller:", e)


def revaluar_cotizaciones_por_limite(nuevo_limite):
    """
    Aplica las 3 reglas de negocio al cambiar el límite global de cotizaciones caras:
    Regla 1: Si un ticket ya fue aprobado por el supervisor para que empiece a trabajar el taller
             (o ya está trabajando, reparado, finalizado o entregado), NO le afecta si la cotización era cara o no.
    Regla 2: Si el ticket está en proceso de aprobación, se aplica en automático el cambio
             (según si el precio ahora es mayor o menor al nuevo límite) para que vaya a corporativos o no.
    Regla 3: Si un ticket era cotización cara y tocaba que lo apruebe el administrador porque el supervisor
             ya la aprobó, si ahora con el nuevo límite deja de ser cara (precio < nuevo_limite),
             se va DIRECTO a que la arregle el taller porque ya no requiere aprobación corporativa.
    """
    data = leer_json("facturas.json")
    modificado = False
    tickets_a_taller = []

    for f in data.get("facturas", []):
        st = str(f.get("estado", "")).lower()
        entregado = f.get("entregado") in ["Sí", "Si", "S"]

        # Regla 1: Ya finalizado, archivado, cancelado o entregado -> Inmutable
        if st in ["archivado", "archivado_final", "finalizado", "entregado", "cancelado", "rechazado", "eliminado"] or entregado:
            continue

        # Regla 1: Si ya fue aprobado y el taller ya está trabajando o concluyó el trabajo -> Inmutable
        if f.get("taller_trabajando") or f.get("reparado") or (f.get("aprobado_admin") and f.get("aprobado_corp") and f.get("liberado_admin") is not None):
            continue

        precio_float = float(f.get("precio_estimado", f.get("precio", 0)) or 0)
        es_cara = precio_float >= float(nuevo_limite)
        sup_aprobado = (f.get("aprobado_admin") is True)

        # Regla 3: Era cotización cara detenida esperando Admin/Corp, pero el supervisor ya la había aprobado.
        # Al subir el límite global (o bajar el umbral requerido), el ticket ahora es MENOR al límite (< nuevo_limite):
        # ¡Se va directo a que la arregle el taller sin pasar por corporativos!
        if sup_aprobado and not es_cara:
            # Estaba pendiente de aprobación de corporativos o admin_10k
            if not f.get("aprobado_corp") or not f.get("aprobado_admin_10k"):
                f["aprobado_admin_10k"] = True
                f["aprobado_corp"] = True
                f["liberado_admin"] = False
                f["estado_custom"] = "Exenta de Corporativos por ajuste de límite global"
                modificado = True
                tickets_a_taller.append(f)

        # Regla 2: Si ahora califica como cara (precio >= nuevo_limite) y estaba en proceso de aprobación
        # pero aún no se despachaba al taller, debe canalizarse a Corporativos:
        elif sup_aprobado and es_cara:
            if f.get("aprobado_corp") is True and f.get("liberado_admin") is None:
                f["aprobado_corp"] = False
                f["aprobado_admin_10k"] = False
                f["estado_custom"] = "Canalizada a Validación +10,000 por nuevo límite global"
                modificado = True

    if modificado:
        escribir_json("facturas.json", data)
        for t in tickets_a_taller:
            despachar_orden_al_taller(t)

    return len(tickets_a_taller)
'''

target_anchor = 'def obtener_limite_cotizaciones_caras():'
if target_anchor in code and 'def revaluar_cotizaciones_por_limite' not in code:
    # Buscar el final de obtener_limite_cotizaciones_caras
    pos_anchor = code.find(target_anchor)
    pos_return = code.find('return 10000.0', pos_anchor)
    pos_end_fn = code.find('\n', pos_return) + 1
    code = code[:pos_end_fn] + '\n' + functions_to_add + '\n' + code[pos_end_fn:]
    print("Funciones despachar_orden_al_taller y revaluar_cotizaciones_por_limite agregadas correctamente.")
else:
    print("Aviso: Ya existían o no se encontró target_anchor")

# Update editar_factura
old_editar_block = """            precio_float = float(precio_limpio)
            f["precio"] = precio_float
            necesita_corp = precio_float >= obtener_limite_cotizaciones_caras()
            f["aprobado_admin"] = True
            if necesita_corp:
                f["aprobado_corp"] = False
                f["estado_custom"] = "Actualizada por sistema (Pend. Corp)"
            else:
                f["aprobado_corp"] = True
                f["estado_custom"] = "Actualizada por sistema\""""

new_editar_block = """            precio_float = float(precio_limpio)
            f["precio"] = precio_float
            limite_actual = obtener_limite_cotizaciones_caras()
            necesita_corp = precio_float >= limite_actual

            # Regla 1: Si ya fue aprobado y el taller ya empezó a trabajar o concluyó, su estatus de taller no se altera
            ya_en_taller = f.get("taller_trabajando") or f.get("reparado") or f.get("entregado") in ["Sí", "Si", "S"] or (f.get("aprobado_admin") and f.get("aprobado_corp") and f.get("liberado_admin") is not None)

            if not ya_en_taller:
                sup_aprobado = (f.get("aprobado_admin") is True)
                if sup_aprobado:
                    # Regla 3: Si el supervisor ya la aprobó y el precio baja del límite, se va directo al taller
                    if not necesita_corp:
                        f["aprobado_admin_10k"] = True
                        f["aprobado_corp"] = True
                        f["liberado_admin"] = False
                        f["estado_custom"] = "Aprobada por Supervisor (Precio ajustado < límite)"
                        despachar_orden_al_taller(f)
                    else:
                        # Regla 2: Si el precio sube o se mantiene sobre el límite, requiere Corporativos
                        f["aprobado_admin_10k"] = False
                        f["aprobado_corp"] = False
                        f["estado_custom"] = "Actualizada por sistema (Pend. Corp)"
                else:
                    # Aún pendiente de aprobación de supervisor
                    f["aprobado_corp"] = not necesita_corp
                    f["estado_custom"] = "Actualizada por sistema\""""

if old_editar_block in code:
    code = code.replace(old_editar_block, new_editar_block, 1)
    print("Bloque de editar_factura actualizado con las 3 reglas de negocio.")
else:
    print("Aviso: No se encontró exacto old_editar_block")

with open('rutas_facturas.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_facturas.py guardado con éxito!")

