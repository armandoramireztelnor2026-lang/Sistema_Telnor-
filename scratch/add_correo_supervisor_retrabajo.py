# -*- coding: utf-8 -*-

# 1. Add function to notificaciones.py
with open('notificaciones.py', 'r', encoding='utf-8') as f:
    notif_code = f.read()

nueva_funcion = '''

def enviar_correo_retrabajo_exitoso_supervisor(correo_supervisor, nombre_supervisor, ticket, unidad, nombre_taller, motivo_retrabajo):
    """
    Notifica al supervisor del ticket que la reasignación de la unidad al taller
    por concepto de retrabajo / garantía fue procesada exitosamente en el sistema.
    """
    if not correo_supervisor or str(correo_supervisor).strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    unidad_limpia = str(unidad).replace('8090-', '')
    asunto = f"✅ Reasignación Exitosa al Taller - Retrabajo Unidad 8090-{unidad_limpia} - Ticket #{ticket}"

    bloque_obs = (
        f'<div style="background-color: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #166534; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Falla Reportada por Corregir en Taller (Garantía):'
        f'</div>'
        f'<div style="color: #14532d; font-size: 14px; font-style: italic; line-height: 1.5;">'
        f'"{motivo_retrabajo}"'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Reasignación de Retrabajo Exitosa",
        subtitulo_header="Confirmación de reasignación a taller por garantía",
        categoria_badge="REASIGNACIÓN CONFIRMADA",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_supervisor or 'Supervisor'}</strong>,",
        mensaje_intro=(
            f"Te confirmamos que la orden de <strong>retrabajo por garantía</strong> para la unidad <strong>8090-{unidad_limpia}</strong> "
            f"(Ticket <strong>#{ticket}</strong>) ha sido <strong>reasignada exitosamente</strong> al taller <strong>{nombre_taller}</strong>.<br><br>"
            f"Se ha notificado formalmente al taller por correo electrónico con las observaciones del fallo que persiste para que procedan con la corrección inmediata de la unidad bajo garantía de servicio sin costo adicional."
        ),
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{unidad_limpia}"),
            ("🔧 Taller Notificado", nombre_taller),
            ("📋 Estado Actual", "<span style='color: #16a34a; font-weight: bold;'>Reasignado al Taller</span>"),
            ("👨‍💼 Supervisor Responsable", nombre_supervisor or "Supervisión Vehicular")
        ],
        bloque_destacado=bloque_obs,
        callout_texto="El ticket ya está disponible en el panel del taller dentro de su módulo de <strong>Garantía / Retrabajo</strong>. Podrás consultar el avance o dar seguimiento a la orden en cualquier momento desde tu panel de Supervisión.",
        callout_tipo="exito",
        autor_proceso=formatear_nombre_rol(nombre_supervisor, "Supervisor") if nombre_supervisor else None
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)
'''

if 'enviar_correo_retrabajo_exitoso_supervisor' not in notif_code:
    notif_code += nueva_funcion
    with open('notificaciones.py', 'w', encoding='utf-8') as f:
        f.write(notif_code)
    print("OK: Agregada enviar_correo_retrabajo_exitoso_supervisor en notificaciones.py")
else:
    print("Nota: enviar_correo_retrabajo_exitoso_supervisor ya existía en notificaciones.py")


# 2. Update rutas_reportes.py
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    rutas_code = f.read()

# Update import
old_import = """from notificaciones import (
    enviar_correo_nueva_orden,
    enviar_correo_nuevo_ticket,
    enviar_correo_confirmacion_reporte,
    enviar_correo_ticket_rechazado,
    enviar_correo_retrabajo_taller,
    enviar_correo_cancelacion_retrabajo_chofer,
)"""

new_import = """from notificaciones import (
    enviar_correo_nueva_orden,
    enviar_correo_nuevo_ticket,
    enviar_correo_confirmacion_reporte,
    enviar_correo_ticket_rechazado,
    enviar_correo_retrabajo_taller,
    enviar_correo_cancelacion_retrabajo_chofer,
    enviar_correo_retrabajo_exitoso_supervisor,
)"""

if old_import in rutas_code:
    rutas_code = rutas_code.replace(old_import, new_import, 1)
    print("OK: Import actualizado en rutas_reportes.py (LF)")
elif old_import.replace('\n', '\r\n') in rutas_code:
    rutas_code = rutas_code.replace(old_import.replace('\n', '\r\n'), new_import.replace('\n', '\r\n'), 1)
    print("OK: Import actualizado en rutas_reportes.py (CRLF)")
else:
    print("Aviso: No se encontró bloque exacto de import en rutas_reportes.py")

# Update reasignar_retrabajo logic to send email to supervisor
old_dispatch = """    try:
        enviar_correo_retrabajo_taller(
            correo_taller=correo_taller,
            nombre_taller=nombre_taller,
            ticket=ticket_display,
            unidad=unidad,
            motivo_retrabajo=motivo_chofer,
            nombre_supervisor=sup_nombre
        )
    except Exception as e:
        print(f"Error al enviar correo de retrabajo al taller: {e}")"""

new_dispatch = """    try:
        enviar_correo_retrabajo_taller(
            correo_taller=correo_taller,
            nombre_taller=nombre_taller,
            ticket=ticket_display,
            unidad=unidad,
            motivo_retrabajo=motivo_chofer,
            nombre_supervisor=sup_nombre
        )
    except Exception as e:
        print(f"Error al enviar correo de retrabajo al taller: {e}")

    # Determinar correo del supervisor del ticket
    correo_supervisor = encontrado.get("supervisor_correo") or dp.get("correo") or session["usuario"].get("correo")
    nombre_supervisor_dest = sup_nombre or encontrado.get("supervisor_asignado") or "Supervisor"

    if not correo_supervisor:
        sup_target_user = encontrado.get("supervisor_usuario") or session["usuario"].get("usuario")
        for u in usuarios_data.get("usuarios", []):
            if u.get("usuario") == sup_target_user or (u.get("rol") == "administracion" and u.get("datos_perfil", {}).get("subrol") == "Supervisor"):
                correo_supervisor = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                if correo_supervisor:
                    break

    if not correo_supervisor:
        correo_supervisor = "armandoramireztelnor2026@gmail.com"

    try:
        enviar_correo_retrabajo_exitoso_supervisor(
            correo_supervisor=correo_supervisor,
            nombre_supervisor=nombre_supervisor_dest,
            ticket=ticket_display,
            unidad=unidad,
            nombre_taller=nombre_taller,
            motivo_retrabajo=motivo_chofer
        )
    except Exception as e:
        print(f"Error al enviar correo de confirmación de retrabajo al supervisor: {e}")"""

if old_dispatch in rutas_code:
    rutas_code = rutas_code.replace(old_dispatch, new_dispatch, 1)
    print("OK: Envío de correo al supervisor agregado en rutas_reportes.py (LF)")
elif old_dispatch.replace('\n', '\r\n') in rutas_code:
    rutas_code = rutas_code.replace(old_dispatch.replace('\n', '\r\n'), new_dispatch.replace('\n', '\r\n'), 1)
    print("OK: Envío de correo al supervisor agregado en rutas_reportes.py (CRLF)")
else:
    print("Aviso: No se encontró old_dispatch en rutas_reportes.py")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(rutas_code)

print("Saved rutas_reportes.py")

