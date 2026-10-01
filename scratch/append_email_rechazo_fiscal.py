import json
with open('notificaciones.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def enviar_correo_admin_rechazo_fiscal(lista_admins, ticket, unidad, motivo, nombre_supervisor="Supervisor"):
    for correo_admin in lista_admins:
        if not correo_admin: continue
        asunto = f"El Supervisor ha rechazado la factura fiscal de la Unidad: {unidad}"
        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f87171; padding: 15px; border-radius: 5px 5px 0 0;">
                <h2 style="color: white; margin: 0;">Rechazo de Factura Fiscal</h2>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>Hola Administrador,</p>
                <p>El <strong>{nombre_supervisor}</strong> ha rechazado la factura fiscal (documento contable) del ticket <strong>{ticket}</strong> para la unidad <strong>{unidad}</strong>.</p>
                <p><strong>Motivo del rechazo:</strong></p>
                <blockquote style="border-left: 4px solid #f87171; padding-left: 10px; color: #555; font-style: italic;">
                    {motivo}
                </blockquote>
                <p>El proceso de liberación del documento contable se ha reiniciado.</p>
                <p>Por favor, revisa los datos correspondientes para liberar nuevamente el campo contable o verifica si el supervisor necesita actualizar los datos del pedido/orden.</p>
                <p>Atentamente,<br><strong>Sistema Telnor</strong></p>
            </div>
        </body>
        </html>
        """
        enviar_correo(correo_admin, asunto, cuerpo)
'''

if 'enviar_correo_admin_rechazo_fiscal' not in content:
    with open('notificaciones.py', 'a', encoding='utf-8') as f:
        f.write(new_func)
    print("Function appended")
else:
    print("Function already exists")
