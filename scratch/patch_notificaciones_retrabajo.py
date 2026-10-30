# -*- coding: utf-8 -*-

codigo_nuevas_funciones = '''

def enviar_correo_retrabajo_listo_chofer(correo_chofer, nombre_chofer, ticket, unidad, nombre_taller, codigo_chofer):
    """
    Notifica al chofer que el taller concluyo los trabajos de garantia / retrabajo de su unidad,
    y le proporciona el codigo de validacion de entrega.
    """
    if not correo_chofer or str(correo_chofer).strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    unidad_limpia = str(unidad).replace('8090-', '')
    asunto = f"🔔 Unidad 8090-{unidad_limpia} Lista en Taller - Codigo de Validacion: {codigo_chofer} - Ticket #{ticket}"

    bloque_codigo = (
        f'<div style="background-color: #ecfdf5; border: 2px dashed #10b981; border-radius: 8px; padding: 18px 20px; text-align: center; margin: 18px 0;">'
        f'<div style="color: #065f46; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">'
        f'Código de Validación de Entrega (Chofer):'
        f'</div>'
        f'<div style="color: #047857; font-size: 32px; font-weight: 800; letter-spacing: 6px; font-family: monospace; margin: 6px 0;">'
        f'{codigo_chofer}'
        f'</div>'
        f'<div style="color: #059669; font-size: 12px; margin-top: 6px;">'
        f'Proporciona este código al supervisor al recibir tu unidad para validar formalmente la entrega.'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Unidad Reparada y Lista en Taller",
        subtitulo_header="Validación de Entrega por Retrabajo / Garantía",
        categoria_badge="RETRABAJO CONCLUIDO",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_chofer or 'Chofer'}</strong>,",
        mensaje_intro=(
            f"Se le notifica que el taller <strong>{nombre_taller}</strong> ha marcado como <strong>concluidos y listos</strong> "
            f"los trabajos de garantía / retrabajo para su unidad <strong>8090-{unidad_limpia}</strong> (Ticket <strong>#{ticket}</strong>)."
        ),
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{unidad_limpia}"),
            ("🔧 Taller que Reparó", nombre_taller),
            ("🔐 Código de Validación", f"<span style='color: #047857; font-size: 16px; font-weight: 800; font-family: monospace;'>{codigo_chofer}</span>")
        ],
        bloque_destacado=bloque_codigo,
        callout_texto="Al momento de acudir por la unidad o verificar su entrega, entrega este código de 6 dígitos a supervisión para que el ticket sea liberado y marcado formalmente como entregado.",
        callout_tipo="exito"
    )
    return disparar_correo(correo_chofer, asunto, cuerpo_html)


def enviar_correo_retrabajo_listo_taller(correo_taller, nombre_taller, ticket, unidad, nombre_chofer=None):
    """
    Notifica al taller que su confirmacion de retrabajo listo fue registrada en el sistema.
    """
    if not correo_taller or str(correo_taller).strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    unidad_limpia = str(unidad).replace('8090-', '')
    asunto = f"✅ Retrabajo Concluido Registrado - Unidad 8090-{unidad_limpia} - Ticket #{ticket}"

    cuerpo_html = generar_plantilla_base(
        titulo_header="Retrabajo Marcado como Listo",
        subtitulo_header="Notificación de registro de conclusión en taller",
        categoria_badge="GARANTÍA REGISTRADA",
        color_tema="azul",
        saludo=f"Hola <strong>{nombre_taller}</strong>,",
        mensaje_intro=(
            f"Te confirmamos que has marcado formalmente como <strong>lista</strong> la unidad <strong>8090-{unidad_limpia}</strong> "
            f"(Ticket <strong>#{ticket}</strong>).<br><br>"
            f"El sistema ha generado y notificado los códigos de validación al chofer responsable y a supervisión vehicular para proceder con la entrega y liberación."
        ),
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{unidad_limpia}"),
            ("👤 Chofer Notificado", nombre_chofer or "Chofer"),
            ("📋 Estado Actual", "<span style='color: #0284c7; font-weight: bold;'>Por Liberar (En Supervisión)</span>")
        ],
        callout_texto="La unidad se encuentra ahora en espera de validación de entrega por parte de Supervisión para concluir formalmente el proceso de garantía.",
        callout_tipo="info"
    )
    return disparar_correo(correo_taller, asunto, cuerpo_html)


def enviar_correo_retrabajo_listo_supervisor_respaldo(correo_supervisor, nombre_supervisor, ticket, unidad, nombre_taller, nombre_chofer, codigo_supervisor):
    """
    Notifica al supervisor de respaldo con su codigo de respaldo para validar la liberacion del retrabajo.
    """
    if not correo_supervisor or str(correo_supervisor).strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    unidad_limpia = str(unidad).replace('8090-', '')
    asunto = f"🛡️ Código de Respaldo: Unidad 8090-{unidad_limpia} Lista en Taller - Ticket #{ticket}"

    bloque_codigo = (
        f'<div style="background-color: #fffbeb; border: 2px dashed #f59e0b; border-radius: 8px; padding: 18px 20px; text-align: center; margin: 18px 0;">'
        f'<div style="color: #92400e; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">'
        f'Código de Respaldo de Supervisión:'
        f'</div>'
        f'<div style="color: #d97706; font-size: 32px; font-weight: 800; letter-spacing: 6px; font-family: monospace; margin: 6px 0;">'
        f'{codigo_supervisor}'
        f'</div>'
        f'<div style="color: #b45309; font-size: 12px; margin-top: 6px;">'
        f'Puedes ingresar este código de respaldo o el código del chofer en "Liberar/Retrabajo" para validar la entrega.'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Retrabajo Listo para Liberación",
        subtitulo_header="Código de Respaldo para Supervisión Vehicular",
        categoria_badge="CÓDIGO DE RESPALDO",
        color_tema="ambar",
        saludo=f"Hola <strong>{nombre_supervisor or 'Supervisor'}</strong>,",
        mensaje_intro=(
            f"El taller <strong>{nombre_taller}</strong> ha marcado como <strong>lista</strong> la unidad <strong>8090-{unidad_limpia}</strong> "
            f"(Ticket <strong>#{ticket}</strong>).<br><br>"
            f"Se envió un código de validación al chofer <strong>{nombre_chofer or 'Chofer'}</strong>. De manera adicional, a continuación se proporciona tu <strong>código de respaldo</strong> de supervisión:"
        ),
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{unidad_limpia}"),
            ("🔧 Taller", nombre_taller),
            ("👤 Chofer", nombre_chofer or "Chofer"),
            ("🛡️ Código Respaldo", f"<span style='color: #d97706; font-size: 16px; font-weight: 800; font-family: monospace;'>{codigo_supervisor}</span>")
        ],
        bloque_destacado=bloque_codigo,
        callout_texto="Ingresa al botón <strong>Liberar/Retrabajo</strong> en tu panel de supervisión e introduce este código de respaldo o el código del chofer para liberar la unidad y marcarla como entregada.",
        callout_tipo="advertencia",
        autor_proceso=formatear_nombre_rol(nombre_supervisor, "Supervisor") if nombre_supervisor else None
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)
'''

with open("notificaciones.py", "r", encoding="utf-8") as f:
    orig = f.read()

is_crlf = "\r\n" in orig
norm = orig.replace("\r\n", "\n")

if "enviar_correo_retrabajo_listo_chofer" not in norm:
    norm += codigo_nuevas_funciones
    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open("notificaciones.py", "w", encoding="utf-8") as f:
        f.write(final)
    print("notificaciones.py patched successfully.")
else:
    print("Already in notificaciones.py")

