import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# =======================================================
# CONFIGURACIÓN DEL "CARTERO" (Tu correo emisor)
# =======================================================
CORREO_REMITENTE = "armandoramireztelnor2026@gmail.com" 
CONTRASENA_REMITENTE = "zgdhbgcpuobszybi" 

def generar_codigo_liberacion():
    """Genera un número aleatorio de 8 dígitos matemáticamente seguro."""
    return str(random.randint(10000000, 99999999))

def disparar_correo(destino, asunto, cuerpo_html):
    msg = MIMEMultipart()
    msg['From'] = CORREO_REMITENTE
    msg['To'] = destino
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo_html, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_REMITENTE, CONTRASENA_REMITENTE)
        server.send_message(msg)
        server.quit()
        return True, "Enviado"
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False, str(e)

def enviar_correo_liberacion(correo_destino, ticket, unidad, codigo, nombre_chofer, telefono_chofer):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Aviso de Liberación: Unidad 8090-{unidad} (Ticket: {ticket})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0b1c30; padding: 20px; text-align: center;">
                <h2 style="color: #10b981; margin: 0;">✔️ LA UNIDAD ESTÁ LISTA</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_chofer}</strong>,</p>
                <p>El taller mecánico ha notificado que la reparación de la unidad <strong>8090-{unidad}</strong> ha sido finalizada y se encuentra lista para su recolección física.</p>
                <p>Para proceder con la liberación del vehículo, presente el siguiente código de autorización en la ventanilla de Automotriz:</p>
                <div style="background-color: #0b1c30; color: #10b981; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; border-radius: 8px; letter-spacing: 5px; margin: 25px 0;">
                    {codigo}
                </div>
                <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                    <li style="margin-bottom: 8px;"><strong>Folio de Reporte:</strong> {ticket}</li>
                    <li style="margin-bottom: 8px;"><strong>Unidad:</strong> 8090-{unidad}</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_nueva_orden(correo_destino, nombre_proveedor, ticket, unidad, falla):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Nueva Orden de Trabajo: Unidad 8090-{unidad} (Ticket: {ticket})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #f59e0b; padding: 20px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">NUEVA ORDEN ASIGNADA</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_proveedor}</strong>,</p>
                <p>Se le notifica que se ha asignado una nueva orden de trabajo para ser atendida en sus instalaciones.</p>
                <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                    <li style="margin-bottom: 8px;"><strong>Ticket asignado:</strong> {ticket}</li>
                    <li style="margin-bottom: 8px;"><strong>Unidad a recibir:</strong> 8090-{unidad}</li>
                    <li style="margin-bottom: 8px;"><strong>Falla reportada:</strong> <em>"{falla}"</em></li>
                </ul>
                <p>Ingrese al portal de proveedores para consultar la documentación y emitir su cotización.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_nueva_factura(lista_admins, proveedor, unidad, precio):
    if not lista_admins:
        return False, "No hay correos"

    asunto = f"Revisión de Cotización: Proveedor {proveedor} (Unidad 8090-{unidad})"
    for admin in lista_admins:
        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <div style="background-color: #0b1c30; padding: 20px; text-align: center;">
                    <h2 style="color: #0ea5e9; margin: 0;">COTIZACIÓN RECIBIDA PARA VALIDACIÓN</h2>
                </div>
                <div style="padding: 20px;">
                    <p>Hola <strong>{admin['nombre']} ({admin['puesto']})</strong>,</p>
                    <p>Se le notifica que ha recibido una nueva cotización mecánica pendiente de validación y asignación de orden.</p>
                    <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                        <li style="margin-bottom: 8px;"><strong>Taller Emisor:</strong> {proveedor}</li>
                        <li style="margin-bottom: 8px;"><strong>Unidad atendida:</strong> 8090-{unidad}</li>
                        <li style="margin-bottom: 8px;"><strong>Costo Estimado:</strong> ${precio:,.2f} MXN (Sin IVA)</li>
                    </ul>
                    <p>Ingrese al panel de Automotriz para proceder con la revisión técnica y emitir su fallo.</p>
                </div>
            </div>
        </body>
        </html>
        """
        disparar_correo(admin['correo'], asunto, cuerpo_html)
    return True, "Enviado"

def enviar_correo_nueva_factura_corp(lista_corps, proveedor, unidad, precio):
    if not lista_corps:
        return False, "No hay correos"

    asunto = f"Autorización Financiera Requerida: {proveedor} (Unidad 8090-{unidad})"
    for corp in lista_corps:
        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <div style="background-color: #0284c7; padding: 20px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0;">REVISIÓN DE GASTO MAYOR (COTIZACIÓN)</h2>
                </div>
                <div style="padding: 20px;">
                    <p>Hola <strong>{corp['nombre']}</strong>,</p>
                    <p>Se le notifica que se requiere su autorización financiera para procesar una cotización que supera los $10,000 MXN establecidos.</p>
                    <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                        <li style="margin-bottom: 8px;"><strong>Taller Emisor:</strong> {proveedor}</li>
                        <li style="margin-bottom: 8px;"><strong>Unidad atendida:</strong> 8090-{unidad}</li>
                        <li style="margin-bottom: 8px;"><strong>Monto por autorizar:</strong> ${precio:,.2f} MXN (Sin IVA)</li>
                    </ul>
                    <p>Ingrese al portal corporativo para analizar la cotización anexada y emitir la autorización correspondiente.</p>
                </div>
            </div>
        </body>
        </html>
        """
        disparar_correo(corp['correo'], asunto, cuerpo_html)
    return True, "Enviado"

def enviar_correo_nuevo_ticket(lista_admins, ticket, unidad, ciudad, falla, empleado):
    if not lista_admins:
        return False, "No hay correos"

    asunto = f"Nuevo Reporte de Incidencia: Unidad 8090-{unidad} ({ciudad})"
    for admin in lista_admins:
        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <div style="background-color: #b45309; padding: 20px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0;">NUEVO REPORTE REGISTRADO</h2>
                </div>
                <div style="padding: 20px;">
                    <p>Hola <strong>{admin['nombre']} ({admin['puesto']})</strong>,</p>
                    <p>Se le notifica que un operador ha registrado un nuevo reporte de falla en el sistema que requiere su atención.</p>
                    <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                        <li style="margin-bottom: 8px;"><strong>Folio:</strong> {ticket}</li>
                        <li style="margin-bottom: 8px;"><strong>Unidad afectada:</strong> 8090-{unidad}</li>
                        <li style="margin-bottom: 8px;"><strong>Ubicación Base:</strong> {ciudad}</li>
                        <li style="margin-bottom: 8px;"><strong>Operador a cargo:</strong> {empleado}</li>
                        <li style="margin-bottom: 8px;"><strong>Falla reportada:</strong> <em>"{falla}"</em></li>
                    </ul>
                    <p>Ingrese a la plataforma Automotriz para evaluar la incidencia y canalizarla al proveedor correspondiente.</p>
                </div>
            </div>
        </body>
        </html>
        """
        disparar_correo(admin['correo'], asunto, cuerpo_html)
    return True, "Enviado"

def enviar_correo_confirmacion_reporte(correo_destino, nombre_empleado, ticket, unidad, falla):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"✅ Confirmación de Reporte Generado (Ticket: {ticket})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #112641; padding: 20px; text-align: center;">
                <h2 style="color: #10b981; margin: 0;">REPORTE ENVIADO CON ÉXITO</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_empleado}</strong>,</p>
                <p>Le confirmamos que su reporte de incidencia ha sido registrado correctamente en nuestro sistema y ya se encuentra en la bandeja de Automotriz para su revisión.</p>
                <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                    <li style="margin-bottom: 8px;"><strong>Folio de Reporte (Ticket):</strong> {ticket}</li>
                    <li style="margin-bottom: 8px;"><strong>Unidad:</strong> 8090-{unidad}</li>
                    <li style="margin-bottom: 8px;"><strong>Falla registrada:</strong> <em>"{falla}"</em></li>
                </ul>
                <p>Nos pondremos en contacto con usted en cuanto se le asigne un taller a su unidad o cuando el servicio haya concluido.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_confirmacion_factura(correo_destino, nombre_proveedor, unidad, precio):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"✅ Confirmación de Cotización Enviada (Unidad 8090-{unidad})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #112641; padding: 20px; text-align: center;">
                <h2 style="color: #10b981; margin: 0;">COTIZACIÓN ENVIADA CON ÉXITO</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_proveedor}</strong>,</p>
                <p>Le confirmamos que su cotización ha sido cargada al sistema exitosamente y ya se encuentra en la bandeja del departamento Automotriz para su revisión técnica y financiera.</p>
                <ul style="background-color: #f9fafb; padding: 15px 30px; border-radius: 8px; border: 1px solid #e5e7eb; list-style-type: none; margin-left: 0;">
                    <li style="margin-bottom: 8px;"><strong>Unidad Atendida:</strong> 8090-{unidad}</li>
                    <li style="margin-bottom: 8px;"><strong>Costo Estimado:</strong> ${precio:,.2f} MXN (Sin IVA)</li>
                </ul>
                <p>El sistema le notificará cuando la orden sea aprobada para que inicie la reparación.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_factura_rechazada(correo_destino, nombre_proveedor, unidad, motivo):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"❌ COTIZACIÓN / TRÁMITE RECHAZADO: Unidad 8090-{unidad}"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #dc2626; padding: 20px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">TRÁMITE RECHAZADO / CANCELADO</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_proveedor}</strong>,</p>
                <p>Se le notifica que la administración de Automotriz ha rechazado o eliminado su cotización/trámite correspondiente a la unidad <strong>8090-{unidad}</strong>.</p>
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <h4 style="margin: 0 0 10px 0; color: #991b1b;">Motivo del rechazo:</h4>
                    <p style="margin: 0; font-style: italic; color: #7f1d1d;">"{motivo}"</p>
                </div>
                <p>Por favor, ingrese al Portal de Proveedores para realizar las modificaciones pertinentes y volver a enviar su documentación si así se requiere.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_ticket_rechazado(correo_destino, nombre_empleado, ticket, unidad, motivo):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"❌ REPORTE CANCELADO: Ticket {ticket} (Unidad 8090-{unidad})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #dc2626; padding: 20px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">REPORTE CANCELADO / RECHAZADO</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_empleado}</strong>,</p>
                <p>Se le notifica que el departamento Automotriz ha cancelado o cerrado su reporte de incidencia (Ticket: <strong>{ticket}</strong>).</p>
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <h4 style="margin: 0 0 10px 0; color: #991b1b;">Mensaje de Administración (Motivo):</h4>
                    <p style="margin: 0; font-style: italic; color: #7f1d1d;">"{motivo}"</p>
                </div>
                <p>Si cree que esto es un error, por favor comuníquese directamente con el departamento Automotriz.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_factura_fiscal_subida(correo_destino, proveedor, unidad, titulo, folio):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Factura Final Recibida: {proveedor} (Folio: {folio})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #10b981; color: white; padding: 20px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">NUEVA FACTURA FISCAL RECIBIDA</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>Administración</strong>,</p>
                <p>El proveedor <strong>{proveedor}</strong> ha subido su factura final (CFDI) para pago.</p>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin-bottom: 10px;"><strong>Unidad:</strong> 8090-{unidad}</li>
                    <li style="margin-bottom: 10px;"><strong>Concepto:</strong> {titulo}</li>
                    <li style="margin-bottom: 10px;"><strong>Folio Fiscal:</strong> {folio}</li>
                </ul>
                <p style="margin-top: 20px;">Puede ingresar al sistema para descargar el archivo PDF de la factura y proceder con el trámite correspondiente.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)

def enviar_correo_factura_fiscal_rechazada(correo_destino, proveedor, unidad, folio_rechazado, motivo):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Aviso Importante: Factura Rechazada (Unidad {unidad})"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #ef4444; color: white; padding: 20px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0;">FACTURA FISCAL RECHAZADA</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{proveedor}</strong>,</p>
                <p>Le notificamos que el departamento de Administración Automotriz ha <strong>rechazado</strong> la factura fiscal que subió para la unidad <strong>8090-{unidad}</strong> (Folio reportado: {folio_rechazado}).</p>
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <h4 style="margin: 0 0 10px 0; color: #991b1b;">Motivo del Rechazo:</h4>
                    <p style="margin: 0; font-style: italic; color: #7f1d1d;">"{motivo}"</p>
                </div>
                <p>El archivo PDF anterior ha sido eliminado de nuestro sistema. Por favor ingrese a la plataforma, vaya a la sección "Facturas" y vuelva a subir su factura corregida.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return disparar_correo(correo_destino, asunto, cuerpo_html)