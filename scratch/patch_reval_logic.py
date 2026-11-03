import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_fn_start = code.find('def revaluar_cotizaciones_por_limite')
old_fn_end = code.find('\n\ndef es_ticket_corporativo', old_fn_start)
if old_fn_end == -1:
    old_fn_end = code.find('def es_ticket_corporativo', old_fn_start)

new_fn = '''def revaluar_cotizaciones_por_limite(nuevo_limite):
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

        # Si el supervisor aún NO la aprueba (proceso de cotización inicial):
        if not sup_aprobado:
            if es_cara:
                if f.get("aprobado_corp") is not False:
                    f["aprobado_corp"] = False
                    f["aprobado_admin_10k"] = False
                    modificado = True
            else:
                if f.get("aprobado_corp") is False:
                    f["aprobado_corp"] = True
                    modificado = True

        # Regla 3: Era cotización cara detenida esperando Admin/Corp, pero el supervisor ya la había aprobado.
        # Al subir el límite global (o bajar el precio), el ticket ahora es MENOR al límite (< nuevo_limite):
        # ¡Se va directo a que la arregle el taller sin pasar por corporativos!
        elif sup_aprobado and not es_cara:
            # Estaba pendiente de aprobación de corporativos o admin_10k
            if (not f.get("aprobado_corp") or not f.get("aprobado_admin_10k")) and f.get("liberado_admin") is None:
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

code = code[:old_fn_start] + new_fn.strip() + '\n\n' + code[old_fn_end:].lstrip()

with open('rutas_facturas.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("revaluar_cotizaciones_por_limite actualizada correctamente!")

