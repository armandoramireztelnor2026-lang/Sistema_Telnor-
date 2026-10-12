import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import random
import re
import json

# =======================================================
# CONFIGURACIÓN DEL "CARTERO" (Correo emisor Telnor)
# =======================================================
CORREO_REMITENTE = "armandoramireztelnor2026@gmail.com" 
CONTRASENA_REMITENTE = "zgdhbgcpuobszybi" 

def generar_codigo_liberacion():
    """Genera un número aleatorio de 8 dígitos matemáticamente seguro."""
    return str(random.randint(10000000, 99999999))

def obtener_actor_sesion(default=None):
    """Extrae el nombre y rol del usuario logueado en la sesión activa si existe contexto Flask."""
    try:
        from flask import session, has_request_context
        if has_request_context() and 'usuario' in session:
            perf = session['usuario'].get('datos_perfil', {})
            nombres = perf.get('nombres', '').strip()
            apellido = perf.get('apellido_paterno', '').strip()
            nombre_completo = f"{nombres} {apellido}".strip()
            rol = perf.get('subrol') or session['usuario'].get('rol', '')
            if rol and nombre_completo:
                return f"{str(rol).capitalize()}: {nombre_completo}"
            elif nombre_completo:
                return nombre_completo
    except Exception:
        pass
    return default

def formatear_nombre_rol(nombre, rol_default=None):
    """Formatea un nombre con su prefijo de rol si no lo tiene."""
    if not nombre or not str(nombre).strip():
        return None
    nombre_str = str(nombre).strip()
    if ":" in nombre_str:
        return nombre_str
    if rol_default:
        rol_limpio = str(rol_default).strip().capitalize()
        if not nombre_str.lower().startswith(rol_limpio.lower()):
            return f"{rol_limpio}: {nombre_str}"
    return nombre_str

def obtener_autorizacion_admin_o_supervisor(autor_proceso=None):
    """
    Valida si el usuario que genera o desencadena el correo tiene el rol de
    'administrador' o 'supervisor'.
    
    Retorna el nombre formateado del usuario (ej. 'Samuel Girón (Supervisor)')
    ÚNICAMENTE si el rol es Administrador o Supervisor.
    Si el usuario tiene cualquier otro rol (Taller, Proveedor, Operador, Chofer,
    Corporativo, etc.), retorna None para que la línea se omita por completo.
    """
    rol_detectado = None
    nombre_detectado = None

    # 1. Analizar autor_proceso explícito
    if autor_proceso and str(autor_proceso).strip():
        autor_str = str(autor_proceso).strip()
        lower_autor = autor_str.lower()

        # Exclusión terminante para roles ajenos a administración/supervisión
        roles_excluidos = [
            'taller', 'proveedor', 'proveedores', 'operador',
            'chofer', 'empleado', 'corporativo', 'corporativos', 'sistema'
        ]
        if any(excl in lower_autor for excl in roles_excluidos):
            return None

        # Si viene en formato "Rol: Nombre"
        if ":" in autor_str:
            partes = autor_str.split(":", 1)
            posible_rol = partes[0].strip()
            posible_nombre = partes[1].strip()
            p_rol_lower = posible_rol.lower()
            if any(r in p_rol_lower for r in ['supervisor', 'administrador', 'admin', 'jefatura', 'administracion', 'administración']):
                rol_detectado = posible_rol
                nombre_detectado = posible_nombre
            else:
                return None
        else:
            nombre_detectado = autor_str

    # 2. Consultar sesión activa de Flask si existe contexto
    try:
        from flask import session, has_request_context
        if has_request_context() and 'usuario' in session:
            usr = session['usuario']
            rol_sesion = str(usr.get('rol', '')).strip().lower()
            perf = usr.get('datos_perfil', {})
            subrol_sesion = str(perf.get('subrol', '')).strip()

            # Descartar inmediatamente roles de taller, chofer o corporativo
            if any(excl in rol_sesion for excl in ['proveedor', 'proveedores', 'corporativo', 'corporativos']):
                return None

            subrol_lower = subrol_sesion.lower()
            roles_validos = ['supervisor', 'administrador', 'admin', 'jefatura', 'administracion', 'administración']
            if any(r in subrol_lower for r in roles_validos) or any(r in rol_sesion for r in roles_validos):
                if not rol_detectado:
                    rol_detectado = subrol_sesion if subrol_sesion else ('Supervisor' if 'supervisor' in rol_sesion else 'Administrador')
                if not nombre_detectado:
                    n = perf.get('nombres', '').strip()
                    ap = perf.get('apellido_paterno', '').strip()
                    nombre_detectado = f"{n} {ap}".strip() or usr.get('usuario', '')
            else:
                return None
    except Exception:
        pass

    # 3. Si tenemos nombre pero no rol verificado, consultar usuarios.json
    if nombre_detectado and not rol_detectado:
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_usr = os.path.join(base_dir, 'usuarios.json')
            if os.path.exists(ruta_usr):
                with open(ruta_usr, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                nombre_clean = nombre_detectado.lower()
                for u in data.get('usuarios', []):
                    dp = u.get('datos_perfil', {})
                    n_full = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".lower().strip()
                    if nombre_clean in n_full or n_full in nombre_clean or nombre_clean == u.get('usuario', '').lower():
                        u_rol = str(u.get('rol', '')).lower()
                        u_subrol = str(dp.get('subrol', '')).lower()
                        roles_validos = ['supervisor', 'administrador', 'admin', 'jefatura', 'administracion', 'administración']
                        if any(r in u_subrol for r in roles_validos) or any(r in u_rol for r in roles_validos):
                            rol_detectado = dp.get('subrol') or ('Supervisor' if 'supervisor' in u_rol else 'Administrador')
                            nombre_detectado = f"{dp.get('nombres', '').strip()} {dp.get('apellido_paterno', '').strip()}".strip()
                        break
        except Exception:
            pass

    # 4. Validación final estricta: Solo Administrador o Supervisor
    if not rol_detectado or not nombre_detectado:
        return None

    rol_lower = rol_detectado.lower()
    if not any(r in rol_lower for r in ['supervisor', 'administrador', 'admin', 'jefatura', 'administracion', 'administración']):
        return None

    if 'supervisor' in rol_lower:
        rol_etiqueta = 'Supervisor'
    elif 'jefatura' in rol_lower:
        rol_etiqueta = 'Jefatura'
    else:
        rol_etiqueta = 'Administrador'

    # Limpiar prefijos redundantes del nombre si ya venían
    nombre_limpio = nombre_detectado
    for prefix in ['supervisor:', 'administrador:', 'jefatura:', 'admin:', 'supervisor', 'administrador', 'jefatura']:
        if nombre_limpio.lower().startswith(prefix):
            nombre_limpio = nombre_limpio[len(prefix):].strip(" :")

    return f"{nombre_limpio} ({rol_etiqueta})"

def generar_plantilla_base(
    titulo_header,
    subtitulo_header=None,
    categoria_badge=None,
    color_tema="azul",          # "azul", "verde", "rojo", "ambar"
    saludo="Estimado(a),",
    mensaje_intro="",
    detalles_items=None,        # Lista de tuplas (etiqueta, valor)
    bloque_destacado=None,      # Bloque HTML personalizado (PIN, tablas de precios, etc.)
    callout_texto=None,         # Texto para recuadro de aviso o accion requerida
    callout_tipo="info",        # "info", "alerta", "exito", "peligro"
    autor_proceso=None          # "Supervisor: Juan Pérez", "Administrador: Carlos López", etc.
):
    """
    PLANTILLA BASE CORPORATIVA UNIFICADA TELNOR.
    Absolutamente todos los correos del sistema utilizan esta misma estructura, diseño y formato.
    """
    paletas = {
        "azul": {
            "borde_header": "#0284c7",
            "badge_bg": "rgba(2, 132, 199, 0.18)",
            "badge_border": "rgba(56, 189, 248, 0.4)",
            "badge_txt": "#38bdf8",
        },
        "verde": {
            "borde_header": "#10b981",
            "badge_bg": "rgba(16, 185, 129, 0.18)",
            "badge_border": "rgba(52, 211, 153, 0.4)",
            "badge_txt": "#34d399",
        },
        "rojo": {
            "borde_header": "#ef4444",
            "badge_bg": "rgba(239, 68, 68, 0.18)",
            "badge_border": "rgba(248, 113, 113, 0.4)",
            "badge_txt": "#f87171",
        },
        "ambar": {
            "borde_header": "#f59e0b",
            "badge_bg": "rgba(245, 158, 11, 0.18)",
            "badge_border": "rgba(251, 191, 36, 0.4)",
            "badge_txt": "#fbbf24",
        }
    }
    tema = paletas.get(color_tema, paletas["azul"])

    badge_html = ""
    if categoria_badge:
        badge_html = (
            f'<div style="margin: 6px 0 2px 0;">'
            f'<span style="display: inline-block; background-color: {tema["badge_bg"]}; border: 1px solid {tema["badge_border"]}; color: {tema["badge_txt"]}; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; padding: 2px 10px; border-radius: 12px; text-transform: uppercase;">'
            f'{categoria_badge}'
            f'</span>'
            f'</div>'
        )

    subtitulo_html = ""
    if subtitulo_header:
        subtitulo_html = f'<p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 13px; font-weight: 400;">{subtitulo_header}</p>'

    detalles_html = ""
    if detalles_items:
        rows = []
        for idx, (label, val) in enumerate(detalles_items):
            is_last = (idx == len(detalles_items) - 1)
            border_bottom = "none" if is_last else "1px solid #edf2f7"
            rows.append(
                f'<tr>'
                f'<td style="padding: 8px 6px; width: 42%; color: #64748b; font-weight: 600; border-bottom: {border_bottom}; vertical-align: top; font-size: 13px;">'
                f'{label}:'
                f'</td>'
                f'<td style="padding: 8px 6px; width: 58%; color: #0f172a; font-weight: 500; text-align: right; border-bottom: {border_bottom}; vertical-align: top; font-size: 13px;">'
                f'{val}'
                f'</td>'
                f'</tr>'
            )
        detalles_html = (
            f'<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 18px 0;">'
            f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">'
            f'{"".join(rows)}'
            f'</table>'
            f'</div>'
        )

    callout_html = ""
    if callout_texto:
        estilos_callout = {
            "info": {"bg": "#eff6ff", "border": "#3b82f6", "txt": "#1e40af"},
            "alerta": {"bg": "#fffbeb", "border": "#f59e0b", "txt": "#92400e"},
            "exito": {"bg": "#f0fdf4", "border": "#10b981", "txt": "#166534"},
            "peligro": {"bg": "#fef2f2", "border": "#ef4444", "txt": "#991b1b"},
        }
        c_est = estilos_callout.get(callout_tipo, estilos_callout["info"])
        callout_html = (
            f'<div style="background-color: {c_est["bg"]}; border-left: 4px solid {c_est["border"]}; border-radius: 6px; padding: 13px 16px; margin: 18px 0; color: {c_est["txt"]}; font-size: 13px; line-height: 1.55;">'
            f'{callout_texto}'
            f'</div>'
        )

    # Lógica condicional de autorización: SÓLO rol Administrador o Supervisor
    linea_autor = obtener_autorizacion_admin_o_supervisor(autor_proceso)
    autor_html = ""
    if linea_autor:
        autor_html = (
            f'<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 6px; padding: 12px 16px; margin: 20px 0 8px 0;">'
            f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">'
            f'<tr>'
            f'<td style="width: 28px; vertical-align: middle; font-size: 18px;">🛡️</td>'
            f'<td style="vertical-align: middle;">'
            f'<p style="margin: 0; font-size: 13px; color: #0f172a; font-weight: 600;">'
            f'Proceso autorizado por: <span style="color: #0284c7; font-weight: 700;">{linea_autor}</span>'
            f'</p>'
            f'</td>'
            f'</tr>'
            f'</table>'
            f'</div>'
        )

    bloque_destacado_html = bloque_destacado or ""

    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_header}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #334155; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 25px 10px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 620px; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);">
          <!-- HEADER CORPORATIVO UNIFICADO -->
          <tr>
            <td style="background-color: #0b1c30; padding: 28px 24px 24px 24px; text-align: center; border-bottom: 3px solid {tema['borde_header']};">
              <div style="display: inline-block; background-color: rgba(2, 132, 199, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 20px; padding: 3px 12px; margin-bottom: 10px;">
                <span style="font-size: 11px; font-weight: 700; letter-spacing: 1.2px; color: #38bdf8; text-transform: uppercase;">
                  Sistema de Facturacion Central
                </span>
              </div>
              {badge_html}
              <h1 style="color: #ffffff; margin: 8px 0 4px 0; font-size: 19px; font-weight: 700; letter-spacing: 0.3px; line-height: 1.35;">
                {titulo_header}
              </h1>
              {subtitulo_html}
            </td>
          </tr>
          <!-- CUERPO UNIFICADO -->
          <tr>
            <td style="padding: 28px 30px;">
              <p style="margin: 0 0 14px 0; font-size: 15px; color: #0f172a; font-weight: 600;">
                {saludo}
              </p>
              <p style="margin: 0 0 18px 0; font-size: 14px; color: #475569; line-height: 1.6;">
                {mensaje_intro}
              </p>
              {detalles_html}
              {bloque_destacado_html}
              {callout_html}
              {autor_html}
              <!-- FOOTER CORPORATIVO UNIFICADO -->
              <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 24px; text-align: center;">
                <p style="margin: 0 0 5px 0; font-size: 12px; font-weight: 600; color: #64748b;">
                  Sistema de Facturacion Central
                </p>
                <p style="margin: 0; font-size: 11px; color: #94a3b8; line-height: 1.4;">
                  Notificación institucional automática generada por la plataforma.<br>
                  Favor de no responder a este correo electrónico.
                </p>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    # Regla: Eliminar cualquier aparición de la frase 'Telnor - Rumn' al final o en cualquier parte del correo
    html_limpio = re.sub(r'(?i)telnor\s*[-–—]\s*rumn', '', html_template)
    html_limpio = html_limpio.replace("TELNOR • FACTURACIÓN CENTRAL", "Sistema de Facturacion Central")
    html_limpio = html_limpio.replace(
        "Sistema de Gestión Vehicular • <strong>Telnor</strong>",
        "Sistema de Facturacion Central"
    ).replace(
        "Sistema de Gestión Vehicular",
        "Sistema de Facturacion Central"
    )
    return html_limpio

def disparar_correo(destino, asunto, cuerpo_html, adjuntos=None):
    """Envía el correo electrónico empaquetado en MIME."""
    # Sanitización: eliminar 'Telnor - Rumn' y normalizar nombre del sistema
    if cuerpo_html:
        cuerpo_html = re.sub(r'(?i)telnor\s*[-–—]\s*rumn', '', cuerpo_html)
        cuerpo_html = cuerpo_html.replace("TELNOR • FACTURACIÓN CENTRAL", "Sistema de Facturacion Central")
        cuerpo_html = cuerpo_html.replace(
            "Sistema de Gestión Vehicular • <strong>Telnor</strong>",
            "Sistema de Facturacion Central"
        ).replace(
            "Sistema de Gestión Vehicular",
            "Sistema de Facturacion Central"
        )
        cuerpo_html = cuerpo_html.replace("Acción generada / autorizada por:", "Proceso autorizado por:")

    # Validación condicional de autorización: SÓLO si el usuario es Administrador o Supervisor
    if "Proceso autorizado por:" not in (cuerpo_html or ""):
        linea_autor = obtener_autorizacion_admin_o_supervisor()
        if linea_autor and cuerpo_html and '</body>' in cuerpo_html:
            autor_box = (
                f'<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 6px; padding: 12px 16px; margin: 20px 0 8px 0; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">'
                f'<table width="100%" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">'
                f'<tr>'
                f'<td style="width: 28px; vertical-align: middle; font-size: 18px;">🛡️</td>'
                f'<td style="vertical-align: middle;">'
                f'<p style="margin: 0; font-size: 13px; color: #0f172a; font-weight: 600;">'
                f'Proceso autorizado por: <span style="color: #0284c7; font-weight: 700;">{linea_autor}</span>'
                f'</p>'
                f'</td>'
                f'</tr>'
                f'</table>'
                f'</div>'
            )
            if '<!-- FOOTER CORPORATIVO UNIFICADO -->' in cuerpo_html:
                cuerpo_html = cuerpo_html.replace('<!-- FOOTER CORPORATIVO UNIFICADO -->', f'{autor_box}\n<!-- FOOTER CORPORATIVO UNIFICADO -->')
            else:
                cuerpo_html = cuerpo_html.replace('</body>', f'{autor_box}\n</body>')

    msg = MIMEMultipart()
    msg['From'] = CORREO_REMITENTE
    msg['To'] = destino
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))
    
    if adjuntos:
        for adjunto in adjuntos:
            if os.path.exists(adjunto):
                try:
                    with open(adjunto, "rb") as file_adj:
                        part = MIMEApplication(file_adj.read(), Name=os.path.basename(adjunto))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(adjunto)}"'
                    msg.attach(part)
                except Exception as ex:
                    print(f"Error adjuntando {adjunto}: {ex}")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_REMITENTE, CONTRASENA_REMITENTE)
        server.send_message(msg)
        server.quit()
        return True, "Enviado"
    except Exception as e:
        print(f"Error enviando correo a {destino}: {e}")
        return False, str(e)


# =========================================================================
# FUNCIONES DE NOTIFICACIÓN CON LA PLANTILLA UNIFICADA
# =========================================================================

def enviar_correo_liberacion_doc50_supervisor(correo_destino, nombre_supervisor, unidad, ticket, nombre_admin=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"Aviso de Liberación para Captura de Doc. Contable (Unidad 8090-{str(unidad).replace('8090-', '')})"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Documento 50 Habilitado",
        subtitulo_header="Liberación de candado contable para captura fiscal",
        categoria_badge="DOC 50 HABILITADO",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro="El área de <strong>Administración</strong> ha liberado oficialmente el candado para la carga del Documento Contable (DOC 50) correspondiente al servicio indicado:",
        detalles_items=[
            ("🎫 Número de Ticket", f"<span style='color: #0284c7; font-weight: bold;'>{ticket}</span>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}")
        ],
        callout_texto="Ya puede ingresar al sistema y capturar el folio correspondiente para que el trámite avance hacia la fase de carga de factura (CFDI) por parte del proveedor.",
        callout_tipo="exito",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_liberacion(correo_destino, ticket, unidad, codigo, nombre_chofer, telefono_chofer, nombre_taller=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Notificación de Liberación de Unidad 8090-{str(unidad).replace('8090-', '')} - Folio {ticket}"
    bloque_pin = (
        f'<div style="background-color: #0b1c30; border: 2px solid #10b981; border-radius: 8px; text-align: center; padding: 18px; margin: 20px 0;">'
        f'<div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px;">'
        f'Código de Autorización (PIN)'
        f'</div>'
        f'<div style="color: #10b981; font-size: 32px; font-weight: 700; letter-spacing: 6px; font-family: monospace;">'
        f'{codigo}'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Unidad Lista para Recolección",
        subtitulo_header="Reparación finalizada por el taller mecánico",
        categoria_badge="VEHÍCULO LISTO",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_chofer}</strong>,",
        mensaje_intro=f"El taller mecánico ha notificado que la reparación de la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> ha concluido satisfactoriamente y se encuentra lista para su entrega física.",
        detalles_items=[
            ("🎫 Folio de Reporte", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad Asignada", f"8090-{str(unidad).replace('8090-', '')}"),
        ],
        bloque_destacado=bloque_pin,
        callout_texto="Para proceder con la liberación y entrega del vehículo, presente el código PIN anterior en la ventanilla de Automotriz o ante el encargado del taller.",
        callout_tipo="info",
        autor_proceso=formatear_nombre_rol(nombre_taller, "Taller")
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_nueva_orden(correo_destino, nombre_proveedor, ticket, unidad, falla, nombre_supervisor=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_supervisor, "Supervisor")
    asunto = f"Asignación de Orden de Trabajo - Unidad 8090-{str(unidad).replace('8090-', '')} (Folio {ticket})"
    
    detalles = [
        ("🎫 Ticket Asignado", f"<strong>{ticket}</strong>"),
        ("🚚 Unidad a Recibir", f"8090-{str(unidad).replace('8090-', '')}"),
        ("⚠️ Falla Reportada", f"<em>{falla}</em>")
    ]
    if nombre_supervisor:
        detalles.append(("👤 Supervisor Asignador", f"<strong>{nombre_supervisor}</strong>"))

    cuerpo_html = generar_plantilla_base(
        titulo_header="Nueva Orden de Trabajo Asignada",
        subtitulo_header="Se requiere evaluación técnica y elaboración de cotización",
        categoria_badge="NUEVA ORDEN",
        color_tema="ambar",
        saludo=f"Hola <strong>{nombre_proveedor}</strong>,",
        mensaje_intro="Se le notifica que se le ha asignado formalmente una nueva orden de servicio para ser atendida e inspeccionada en sus instalaciones.",
        detalles_items=detalles,
        callout_texto="Por favor ingrese al Portal de Proveedores para consultar los antecedentes, inspeccionar el vehículo y subir su cotización con fotografías de evidencia.",
        callout_tipo="info",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_nueva_factura(lista_admins, proveedor, unidad, precio, titulo=None, cotizaciones=None):
    if not lista_admins:
        return False, "No hay correos"

    asunto = f"Revisión Técnica de Cotización - {proveedor} (Unidad 8090-{str(unidad).replace('8090-', '')})"
    
    bloque_cotizaciones = ""
    adjuntos = []
    
    if cotizaciones and len(cotizaciones) > 0:
        items_cots = []
        for idx, cot in enumerate(cotizaciones):
            precio_cot = cot.get('precio', 0.0)
            titulo_cot = cot.get('titulo', 'Sin Título')
            items_cots.append(
                f'<li style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #e2e8f0;">'
                f'<strong>Cotización #{idx+1}:</strong> {titulo_cot}<br>'
                f'<span style="color: #0284c7; font-weight: bold;">Costo: ${precio_cot:,.2f} MXN (Sin IVA)</span>'
                f'</li>'
            )
            
            base_dir = os.path.join(os.getcwd(), 'static', 'facturas_archivos')
            if cot.get("pdf_cotizacion"):
                adjuntos.append(os.path.join(base_dir, cot["pdf_cotizacion"]))
            for foto in cot.get("fotos_evidencia", []):
                adjuntos.append(os.path.join(base_dir, foto))
        
        bloque_cotizaciones = (
            f'<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 18px; margin: 15px 0;">'
            f'<div style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 8px;">'
            f'Desglose de Cotizaciones Recibidas:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #334155;">'
            f'{"".join(items_cots)}'
            f'</ul>'
            f'</div>'
        )

    for admin in lista_admins:
        correo_adm = admin.get('correo') if isinstance(admin, dict) else getattr(admin, 'correo', None)
        if not correo_adm:
            continue
        nombre_adm = admin.get('nombre', 'Administrador') if isinstance(admin, dict) else getattr(admin, 'nombre', 'Administrador')
        puesto_str = f" ({admin.get('puesto')})" if isinstance(admin, dict) and admin.get('puesto') else ""
        cuerpo_html = generar_plantilla_base(
            titulo_header="Cotización Recibida para Validación",
            subtitulo_header="Pendiente de revisión técnica y asignación presupuestal",
            categoria_badge="COTIZACIÓN RECIBIDA",
            color_tema="azul",
            saludo=f"Hola <strong>{nombre_adm}{puesto_str}</strong>,",
            mensaje_intro="Se le notifica que un taller ha subido una nueva cotización mecánica que requiere su evaluación técnica.",
            detalles_items=[
                ("🔧 Taller Emisor", f"<strong>{proveedor}</strong>"),
                ("🚚 Unidad Atendida", f"8090-{str(unidad).replace('8090-', '')}"),
                ("💰 Costo Total Estimado", f"<span style='color: #0284c7; font-weight: bold; font-size: 15px;'>${precio:,.2f} MXN (Sin IVA)</span>")
            ],
            bloque_destacado=bloque_cotizaciones,
            callout_texto="Los documentos PDF y fotos de evidencia han sido adjuntados a este correo para su inspección inmediata. Ingrese a la plataforma para emitir su fallo.",
            callout_tipo="info",
            autor_proceso=formatear_nombre_rol(proveedor, "Taller")
        )
        disparar_correo(correo_adm, asunto, cuerpo_html, adjuntos=adjuntos)
    return True, "Enviado"


def enviar_correo_nuevo_ticket(lista_admins, ticket, unidad, ciudad, falla, empleado):
    if not lista_admins:
        return False, "No hay correos"

    asunto = f"Registro de Nueva Incidencia - Unidad 8090-{str(unidad).replace('8090-', '')} ({ciudad})"
    for admin in lista_admins:
        correo_adm = admin.get('correo') if isinstance(admin, dict) else getattr(admin, 'correo', None)
        if not correo_adm:
            continue
        nombre_adm = admin.get('nombre', 'Administrador') if isinstance(admin, dict) else getattr(admin, 'nombre', 'Administrador')
        puesto_str = f" ({admin.get('puesto')})" if isinstance(admin, dict) and admin.get('puesto') else ""
        cuerpo_html = generar_plantilla_base(
            titulo_header="Nuevo Reporte de Falla Registrado",
            subtitulo_header="Incidencia vehicular levantada por operador",
            categoria_badge="NUEVO REPORTE",
            color_tema="ambar",
            saludo=f"Hola <strong>{nombre_adm}{puesto_str}</strong>,",
            mensaje_intro="Se le notifica que se ha registrado un nuevo reporte de falla vehicular en el sistema que requiere su atención y canalización.",
            detalles_items=[
                ("🎫 Folio de Reporte", f"<strong>{ticket}</strong>"),
                ("🚚 Unidad Afectada", f"8090-{str(unidad).replace('8090-', '')}"),
                ("📍 Ubicación Base", ciudad),
                ("👤 Operador a Cargo", empleado),
                ("⚠️ Falla Reportada", f"<em>{falla}</em>")
            ],
            callout_texto="Ingrese a la plataforma Automotriz para revisar la incidencia y canalizarla al taller mecánico correspondiente.",
            callout_tipo="info",
            autor_proceso=formatear_nombre_rol(empleado, "Operador")
        )
        disparar_correo(admin['correo'], asunto, cuerpo_html)
    return True, "Enviado"


def enviar_correo_confirmacion_reporte(correo_destino, nombre_empleado, ticket, unidad, falla):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"📋 Confirmación de Registro de Incidencia - Folio {ticket}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Reporte Registrado con Éxito",
        subtitulo_header="Su solicitud está en la bandeja de revisión",
        categoria_badge="REPORTE REGISTRADO",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_empleado}</strong>,",
        mensaje_intro="Le confirmamos que su reporte de incidencia ha sido registrado correctamente en nuestro sistema y ya se encuentra disponible para su revisión por parte de Automotriz.",
        detalles_items=[
            ("🎫 Folio de Ticket", f"<span style='color: #10b981; font-weight: bold;'>{ticket}</span>"),
            ("🚚 Unidad Reportada", f"8090-{str(unidad).replace('8090-', '')}"),
            ("📝 Falla Descrita", f"<em>{falla}</em>")
        ],
        callout_texto="Nos pondremos en contacto con usted en cuanto se le asigne un taller a su unidad o cuando el mantenimiento haya concluido.",
        callout_tipo="exito",
        autor_proceso="Sistema de Facturacion Central"
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_rechazada(correo_destino, nombre_proveedor, unidad, motivo, nombre_admin=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"❌ Notificación de Rechazo de Trámite - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    bloque_motivo = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Trámite Rechazado / Cancelado",
        subtitulo_header="Resolución administrativa de presupuesto",
        categoria_badge="TRÁMITE RECHAZADO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_proveedor}</strong>,",
        mensaje_intro=f"Se le notifica que la administración de Automotriz ha rechazado su trámite correspondiente a la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong>.",
        detalles_items=[
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Taller", nombre_proveedor)
        ],
        bloque_destacado=bloque_motivo,
        callout_texto="Por favor ingrese al Portal de Proveedores para realizar las modificaciones pertinentes y volver a enviar su documentación si así se requiere.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_rechazada_corp(correo_destino, nombre_proveedor, unidad, motivo, precios_recomendados, nombre_corp=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_corp, "Corporativo")
    asunto = f"❌ Rechazo por Evaluación Corporativa - Unidad 8090-{str(unidad).replace('8090-', '')} (Requiere Ajuste)"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: Ajustar a <strong>${p.get('precio_recomendado', 'N/A')} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Corporativo:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Observaciones y Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Presupuesto Mayor Rechazado por Corporativo",
        subtitulo_header="Se requieren ajustes presupuestales en la cotización",
        categoria_badge="RECHAZO CORPORATIVO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_proveedor}</strong>,",
        mensaje_intro=f"El área de <strong>Corporativo / Gastos Mayores</strong> ha evaluado su cotización para la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> y ha determinado observaciones en los costos.",
        detalles_items=[
            ("🚚 Unidad Evaluada", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Taller Emisor", nombre_proveedor)
        ],
        bloque_destacado=bloque_obs,
        callout_texto="El ticket original ha sido cancelado en el sistema. Por favor ingrese de nuevo al Portal de Proveedores para crear una cotización ajustada a los precios sugeridos.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_rechazada_admin(correo_destino, nombre_proveedor, unidad, motivo, precios_recomendados, nombre_admin=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"❌ Rechazo Técnico/Administrativo de Cotización - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            precio_val = p.get('precio') or p.get('precio_recomendado') or 'N/A'
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: Ajustar a <strong>${precio_val} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Administración:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Rechazada por Administración",
        subtitulo_header="Observaciones en costos y conceptos presupuestados",
        categoria_badge="COTIZACIÓN RECHAZADA",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_proveedor}</strong>,",
        mensaje_intro=f"La <strong>Administración</strong> ha evaluado su cotización para la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> y ha determinado observaciones en el costo propuesto.",
        detalles_items=[
            ("🚚 Unidad Evaluada", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Taller Emisor", nombre_proveedor)
        ],
        bloque_destacado=bloque_obs,
        callout_texto="El registro previo ha sido descartado. Por favor ingrese al Portal de Proveedores para capturar una nueva cotización aplicando las recomendaciones descritas.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_rechazada_super(correo_destino, nombre_proveedor, unidad, motivo, precios_recomendados, nombre_supervisor=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_supervisor, "Supervisor")
    asunto = f"❌ Rechazo Técnico/Administrativo de Cotización - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: Se recomienda ajustar a <strong>${p.get('precio_recomendado', 'N/A')} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Supervisión:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Rechazada por Supervisión",
        subtitulo_header="Corrección solicitada sin necesidad de crear nuevo ticket",
        categoria_badge="CORRECCIÓN SOLICITADA",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_proveedor}</strong>,",
        mensaje_intro=f"La <strong>Supervisión de Mantenimiento</strong> ha evaluado su cotización para la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> y solicita ajustes de precios.",
        detalles_items=[
            ("🚚 Unidad Evaluada", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Taller Emisor", nombre_proveedor)
        ],
        bloque_destacado=bloque_obs,
        callout_texto="El ticket se encuentra en estado de corrección. Ingrese a la plataforma de proveedores, ubique el ticket y actualice los precios y documentos solicitados.",
        callout_tipo="alerta",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_ticket_rechazado(correo_destino, nombre_empleado, ticket, unidad, motivo, nombre_admin=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administración")
    asunto = f"❌ Cancelación de Reporte - Folio {ticket} (Unidad 8090-{str(unidad).replace('8090-', '')})"
    
    bloque_motivo = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo de Cancelación:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Reporte Cancelado / Rechazado",
        subtitulo_header="Cierre de incidencia por parte de la administración",
        categoria_badge="REPORTE CANCELADO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_empleado}</strong>,",
        mensaje_intro=f"Se le notifica que el departamento Automotriz ha cancelado o cerrado su reporte de falla vehicular (Ticket: <strong>{ticket}</strong>).",
        detalles_items=[
            ("🎫 Folio de Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}")
        ],
        bloque_destacado=bloque_motivo,
        callout_texto="Si considera que esto es un error o su vehículo continúa con la falla, comuníquese directamente con su supervisor de Automotriz.",
        callout_tipo="info",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_fiscal_subida(correo_destino, proveedor, unidad, titulo, folio, nombre_supervisor="Supervisor"):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Recepción de Comprobante Fiscal (CFDI) - {proveedor} (Folio {folio})"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Nueva Factura Fiscal Recibida",
        subtitulo_header="Comprobante fiscal (CFDI) subido por el proveedor",
        categoria_badge="FACTURA FISCAL",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro=f"El proveedor <strong>{proveedor}</strong> ha subido su factura fiscal final (CFDI) para revisión y programación de pago.",
        detalles_items=[
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Proveedor Emisor", f"<strong>{proveedor}</strong>"),
            ("🧾 Folio Fiscal", f"<strong>{folio}</strong>"),
            ("📋 Concepto", titulo)
        ],
        callout_texto="Puede ingresar al sistema para descargar y validar el archivo PDF de la factura fiscal y continuar con la captura del Documento 50.",
        callout_tipo="exito",
        autor_proceso=formatear_nombre_rol(proveedor, "Taller")
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_factura_fiscal_rechazada(correo_destino, proveedor, unidad, folio_rechazado, motivo, nombre_supervisor=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_supervisor, "Supervisor")
    asunto = f"Notificación de Rechazo de Comprobante Fiscal - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    bloque_motivo = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo Fiscal:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Factura Fiscal Rechazada",
        subtitulo_header="Corrección documental requerida en comprobante",
        categoria_badge="FACTURA RECHAZADA",
        color_tema="rojo",
        saludo=f"Hola <strong>{proveedor}</strong>,",
        mensaje_intro=f"Le notificamos que el departamento de Supervisión Automotriz ha <strong>rechazado</strong> el archivo de factura fiscal subido para la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> (Folio: {folio_rechazado}).",
        detalles_items=[
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🧾 Folio Rechazado", f"<strong>{folio_rechazado}</strong>")
        ],
        bloque_destacado=bloque_motivo,
        callout_texto="El archivo anterior ha sido eliminado del expediente. Ingrese a la plataforma, ubique la sección Facturas y suba nuevamente su factura fiscal debidamente corregida.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_esperando_liberacion(correo_destino, nombre_admin, ticket, unidad, num_orden, num_pedido, nombre_supervisor=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_supervisor, "Supervisor")
    asunto = f"Solicitud de Revisión y Liberación Contable - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    detalles = [
        ("🎫 Ticket Vinculado", f"<strong>{ticket}</strong>"),
        ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
        ("📝 Número de Orden", f"<strong>{num_orden}</strong>"),
        ("📦 Solicitud de Pedido", f"<strong>{num_pedido}</strong>")
    ]
    if nombre_supervisor:
        detalles.append(("👤 Supervisor Solicitante", f"<strong>{nombre_supervisor}</strong>"))

    cuerpo_html = generar_plantilla_base(
        titulo_header="Acción Requerida: Liberación de Ticket",
        subtitulo_header="Folios de orden y pedido asignados por Supervisión",
        categoria_badge="LIBERACIÓN CONTABLE",
        color_tema="azul",
        saludo=f"Hola <strong>{nombre_admin}</strong>,",
        mensaje_intro=f"Se le notifica que se han registrado los datos de pedido y orden para la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong> y el ticket se encuentra en espera de su revisión técnica para habilitar la captura de documento contable.",
        detalles_items=detalles,
        callout_texto="Por favor ingrese al sistema, acceda a <strong>Liberar Doc. Contable</strong>, verifique los datos y autorice la liberación para que el proceso avance.",
        callout_tipo="info",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_recordatorio_doc_contable(lista_corps, ticket, unidad, proveedor, orden, pedido, factura, supervisor, ciudad):
    if not lista_corps:
        return False, "No hay correos"

    asunto = f"⚠️ Requerimiento de Documento Contable (50) - Unidad 8090-{str(unidad).replace('8090-', '')}"
    for corp in lista_corps:
        correo_c = corp.get('correo') if isinstance(corp, dict) else getattr(corp, 'correo', None)
        if not correo_c:
            continue
        nombre_c = corp.get('nombre', 'Corporativo') if isinstance(corp, dict) else getattr(corp, 'nombre', 'Corporativo')
        cuerpo_html = generar_plantilla_base(
            titulo_header="Requerimiento de Documento Contable (50)",
            subtitulo_header="Atención urgente requerida para cierre de expediente",
            categoria_badge="ACCIÓN REQUERIDA",
            color_tema="rojo",
            saludo=f"Hola <strong>{nombre_c}</strong>,",
            mensaje_intro=f"Se le notifica a través del Sistema Automotriz que el siguiente servicio ya ha avanzado en su proceso, pero nos encontramos detenidos ya que <strong>no se ha recibido la información correspondiente al Documento Contable (50)</strong>:",
            detalles_items=[
                ("🎫 Folio (Ticket)", f"<strong>{ticket}</strong>"),
                ("🚚 Unidad Atendida", f"8090-{str(unidad).replace('8090-', '')}"),
                ("🔧 Taller", proveedor),
                ("👤 Supervisor Solicitante", supervisor),
                ("📍 Ciudad / Base", ciudad),
                ("🧾 Folio(s) Factura", factura),
                ("📝 No(s). de Orden", orden),
                ("📦 No(s). de Pedido", pedido)
            ],
            callout_texto="Requerimos de su apoyo para generar o proporcionar los números contables correspondientes a este ticket lo antes posible.",
            callout_tipo="peligro",
            autor_proceso=formatear_nombre_rol(supervisor, "Supervisor")
        )
        disparar_correo(correo_c, asunto, cuerpo_html)
    return True, "Enviado"


def enviar_correo_ciudad_asignada(correo, nombre, ciudad, asignado_por):
    asunto = f"📋 Asignación de Jurisdicción Operativa - Ciudad: {ciudad}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Jurisdicción Operativa Asignada",
        subtitulo_header="Actualización de ciudades asignadas a su perfil",
        categoria_badge="CIUDAD ASIGNADA",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre}</strong>,",
        mensaje_intro=f"Se le notifica que <strong>{asignado_por}</strong> (Jefatura) le ha <strong>asignado</strong> una nueva ciudad/COPE a su perfil en el Sistema Automotriz.",
        detalles_items=[
            ("📍 Ciudad / COPE", f"<strong style='color: #10b981;'>{ciudad}</strong>"),
            ("👤 Asignado por", f"<strong>{asignado_por}</strong>")
        ],
        callout_texto="A partir de este momento usted podrá visualizar y gestionar los reportes e incidencias correspondientes a esta nueva plaza.",
        callout_tipo="exito",
        autor_proceso=formatear_nombre_rol(asignado_por, "Jefatura")
    )
    return disparar_correo(correo, asunto, cuerpo_html)


def enviar_correo_cambio_subrol(correo, nombre, nuevo_subrol, modificado_por):
    asunto = f"🔄 Actualización de Funciones y Permisos - Rol: {nuevo_subrol}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Actualización de Perfil Operativo",
        subtitulo_header="Sus funciones y nivel de acceso han sido modificados",
        categoria_badge="CAMBIO DE ROL",
        color_tema="azul",
        saludo=f"Hola <strong>{nombre}</strong>,",
        mensaje_intro=f"Se le notifica que <strong>{modificado_por}</strong> (Jefatura) ha actualizado su perfil operativo en el Sistema Automotriz.",
        detalles_items=[
            ("🛡️ Nuevo Puesto / Subrol", f"<strong style='color: #0284c7; font-size: 14px;'>{nuevo_subrol}</strong>"),
            ("👤 Modificado por", f"<strong>{modificado_por}</strong>")
        ],
        callout_texto="La próxima vez que inicie sesión, su menú principal, bandejas y permisos se ajustarán automáticamente a sus nuevas funciones.",
        callout_tipo="info",
        autor_proceso=formatear_nombre_rol(modificado_por, "Jefatura")
    )
    return disparar_correo(correo, asunto, cuerpo_html)


# =========================================================================
# FLUJO DE COTIZACIONES >$10,000 (INCLUYE NOMBRE DEL SUPERVISOR)
# =========================================================================

def enviar_correo_admin_revisa_10k(correo_admin, nombre_admin, ticket, unidad, proveedor, precio, numeros_orden, nombre_supervisor=None):
    """
    Notifica al Administrador que una cotización >$10k ha sido aprobada por el Supervisor y requiere su visto bueno.
    INCLUYE PROMINENTEMENTE EL NOMBRE DEL SUPERVISOR EN EL CORREO.
    """
    if not correo_admin or correo_admin.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    sup_nombre = nombre_supervisor or obtener_actor_sesion("Supervisor")
    if sup_nombre and str(sup_nombre).lower().startswith("supervisor:"):
        sup_nombre = str(sup_nombre).split(":", 1)[1].strip()

    precio_fmt = f"{float(precio):,.2f}"
    asunto = f"⚠️ Solicitud de Aprobación para Presupuesto Mayor (+$10,000 MXN) - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    detalles = [
        ("🎫 Ticket / Folio", f"<strong>{ticket}</strong>"),
        ("🚚 Unidad Vehicular", f"8090-{str(unidad).replace('8090-', '')}"),
        ("👤 Supervisor Aprobador", f"<span style='color: #0284c7; font-weight: bold;'>{sup_nombre}</span>"),
        ("🔧 Proveedor / Taller", proveedor),
        ("💰 Monto Total Estimado", f"<span style='color: #dc2626; font-weight: bold; font-size: 15px;'>${precio_fmt} MXN</span>"),
        ("📝 Números de Orden", f"<strong>{numeros_orden}</strong>")
    ]

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Mayor a $10,000 MXN",
        subtitulo_header="Aprobada por Supervisión • Pendiente de Validación Administrativa",
        categoria_badge="COTIZACIÓN +10000",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_admin}</strong>,",
        mensaje_intro=f"Se le notifica que el Supervisor <strong>{sup_nombre}</strong> ha evaluado, asignado números de orden y <strong>aprobado</strong> la cotización que supera los <strong>$10,000 MXN</strong>. El trámite requiere de su revisión y visto bueno técnico para poder avanzar hacia la autorización financiera de Corporativos.",
        detalles_items=detalles,
        callout_texto="<strong>Acción requerida:</strong> Ingrese al sistema, consulte la sección <strong>Cotizaciones +10000</strong> y valide si autoriza enviar a Corporativos, solicita corrección o canaliza a Cotizaciones Caras.",
        callout_tipo="alerta",
        autor_proceso=f"Supervisor: {sup_nombre}"
    )
    return disparar_correo(correo_admin, asunto, cuerpo_html)


def enviar_correo_admin_aprobado_a_corp(lista_corps, ticket, unidad, proveedor, precio, admin_nombre, nombre_supervisor=None):
    """
    Notifica a Corporativos que el Administrador aprobó técnicamente y requiere su autorización financiera.
    Incluye tanto el nombre del Administrador como el del Supervisor aprobador.
    """
    if not lista_corps:
        return 0

    sup_nombre = nombre_supervisor
    if not sup_nombre:
        actor = obtener_actor_sesion()
        if actor and "supervisor" in actor.lower():
            sup_nombre = actor.split(":", 1)[1].strip()

    precio_fmt = f"{float(precio):,.2f}"
    asunto = f"⏳ Aprobación Administrativa Emitida - En Espera de Autorización Financiera (${precio_fmt} MXN)"

    enviados = 0
    for corp in lista_corps:
        correo = corp.get("correo")
        nombre_corp = corp.get("nombre", "Miembro")
        if correo and correo.strip():
            detalles = [
                ("🎫 Folio / Ticket", f"<strong>{ticket}</strong>"),
                ("🚚 Unidad Vehicular", f"8090-{str(unidad).replace('8090-', '')}"),
                ("🔧 Proveedor / Taller", proveedor),
                ("💰 Monto a Autorizar", f"<span style='color: #10b981; font-weight: bold; font-size: 15px;'>${precio_fmt} MXN</span>"),
                ("👤 Aprobado por Administrador", f"<strong>{admin_nombre}</strong>")
            ]
            if sup_nombre:
                detalles.append(("👤 Supervisor Aprobador (+10k)", f"<span style='color: #0284c7; font-weight: bold;'>{sup_nombre}</span>"))

            intro_texto = (
                f"El Administrador <strong>{admin_nombre}</strong> ha validado técnicamente la cotización de más de $10,000 MXN aprobada inicialmente por el Supervisor <strong>{sup_nombre}</strong> para la siguiente unidad y requiere de su autorización financiera definitiva:"
                if sup_nombre
                else f"El Administrador <strong>{admin_nombre}</strong> ha aprobado técnicamente la cotización correspondiente a la siguiente unidad y requiere de su autorización financiera definitiva:"
            )

            cuerpo_html = generar_plantilla_base(
                titulo_header="Autorización Financiera Requerida",
                subtitulo_header="Presupuesto mayor aprobado técnicamente por Administración",
                categoria_badge="AUTORIZACIÓN FINANCIERA",
                color_tema="verde",
                saludo=f"Estimado(a) <strong>{nombre_corp} (Corporativos)</strong>,",
                mensaje_intro=intro_texto,
                detalles_items=detalles,
                callout_texto="<strong>Acción requerida:</strong> Por favor ingrese al sistema y consulte su bandeja de <strong>Cotizaciones >$10,000</strong> para autorizar o rechazar este gasto.",
                callout_tipo="info",
                autor_proceso=f"Administrador: {admin_nombre}"
            )
            exito, _ = disparar_correo(correo, asunto, cuerpo_html)
            if exito:
                enviados += 1
    return enviados


def enviar_correo_admin_rechaza_supervisor(correo_supervisor, nombre_supervisor, ticket, unidad, proveedor, motivo, precios_recomendados, nombre_admin=None):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"❌ Rechazo Administrativo - Se Requiere Ajuste Presupuestal (Unidad 8090-{str(unidad).replace('8090-', '')})"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: <strong style='color: #f59e0b;'>${p.get('precio_recomendado', 'N/A')} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Administración:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Rechazada por Administración",
        subtitulo_header="Se solicita corrección en órdenes y costos recomendados",
        categoria_badge="RECHAZO ADMINISTRATIVO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro="El Administrador ha <strong>rechazado</strong> la cotización que asignaste y solicita que se reajusten los números de orden con base en los precios recomendados:",
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Proveedor", proveedor)
        ],
        bloque_destacado=bloque_obs,
        callout_texto="Por favor ingresa al sistema, busca el ticket con el estado actualizado y <strong>reajusta los números de orden según las recomendaciones</strong> para volver a enviar a revisión.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_admin_cancela_caras(correo_supervisor, nombre_supervisor, ticket, unidad, motivo, nombre_admin=None):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"🚫 Trámite Clasificado como Presupuesto Extraordinario (Unidad 8090-{str(unidad).replace('8090-', '')})"
    
    bloque_motivo = (
        f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #9a3412; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Comentario del Administrador:'
        f'</div>'
        f'<div style="color: #7c2d12; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Enviada a Cotizaciones Caras",
        subtitulo_header="Trámite clasificado para análisis especial fuera del flujo normal",
        categoria_badge="COTIZACIONES CARAS",
        color_tema="ambar",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro="El Administrador ha clasificado la siguiente cotización como presupuesto extraordinario y la ha movido al archivo de <strong>Cotizaciones Caras</strong>:",
        detalles_items=[
            ("🎫 Folio / Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}")
        ],
        bloque_destacado=bloque_motivo,
        callout_texto="Este ticket se encuentra en el archivo histórico de Cotizaciones Caras y requerirá reactivación o tratamiento específico.",
        callout_tipo="alerta",
        autor_proceso=autor
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_corp_rechaza_admin(correo_admin, nombre_admin, ticket, unidad, proveedor, precio, motivo, precios_recomendados, nombre_corp=None):
    if not correo_admin or correo_admin.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_corp, "Corporativo")
    precio_fmt = f"{float(precio):,.2f}"
    asunto = f"❌ Resolución Corporativa: Presupuesto Rechazado - Requiere Reevaluación (${precio_fmt} MXN)"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: <strong style='color: #f59e0b;'>${p.get('precio_recomendado', 'N/A')} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Corporativo:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Rechazada por Corporativos",
        subtitulo_header="Resolución de evaluación financiera de gastos mayores",
        categoria_badge="RECHAZO CORPORATIVO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_admin}</strong>,",
        mensaje_intro="Corporativos ha <strong>rechazado</strong> la cotización que aprobaste técnicamente. Requiere reevaluación con base en los precios recomendados:",
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Proveedor", proveedor),
            ("💰 Monto Rechazado", f"<span style='color: #dc2626; font-weight: bold;'>${precio_fmt} MXN</span>")
        ],
        bloque_destacado=bloque_obs,
        callout_texto="Por favor revisa el ticket, consulta con el taller si es factible ajustar a los costos sugeridos y reaprueba si es viable, o envía a Cotizaciones Caras.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_admin, asunto, cuerpo_html)


def enviar_correo_corp_rechaza_supervisor(correo_supervisor, nombre_supervisor, ticket, unidad, proveedor, motivo, precios_recomendados, nombre_corp=None):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_corp, "Corporativo")
    asunto = f"❌ Resolución Corporativa: Presupuesto Rechazado - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    precios_html = ""
    if precios_recomendados and len(precios_recomendados) > 0:
        lis = []
        for p in precios_recomendados:
            lis.append(f"<li>Cotización {int(p.get('idx', 0)) + 1}: <strong style='color: #f59e0b;'>${p.get('precio_recomendado', 'N/A')} MXN</strong></li>")
        precios_html = (
            f'<div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 16px; margin: 12px 0;">'
            f'<div style="color: #b45309; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
            f'Precios Recomendados por Corporativo:'
            f'</div>'
            f'<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #92400e;">'
            f'{"".join(lis)}'
            f'</ul>'
            f'</div>'
        )

    bloque_obs = (
        f'<div style="background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 6px; padding: 13px 16px; margin: 15px 0;">'
        f'<div style="color: #991b1b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">'
        f'Motivo del Rechazo:'
        f'</div>'
        f'<div style="color: #7f1d1d; font-size: 14px; font-style: italic;">'
        f'"{motivo}"'
        f'</div>'
        f'</div>'
        f'{precios_html}'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Rechazada por Corporativos",
        subtitulo_header="Se solicita renegociación de precios con el taller",
        categoria_badge="RECHAZO CORPORATIVO",
        color_tema="rojo",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro="Corporativos ha <strong>rechazado</strong> la cotización que asignaste y solicita renegociar las cotizaciones de acuerdo con los costos recomendados:",
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Proveedor", proveedor)
        ],
        bloque_destacado=bloque_obs,
        callout_texto="Por favor contacta al taller mecánico para acordar el ajuste de precios. Una vez pactado, sube este trámite como una nueva cotización.",
        callout_tipo="peligro",
        autor_proceso=autor
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_corp_aprobado(correo_supervisor, nombre_supervisor, ticket, unidad, proveedor, precio, nombre_corp=None):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_corp, "Corporativo")
    precio_fmt = f"{float(precio):,.2f}"
    asunto = f"✅ Resolución Corporativa: Presupuesto Aprobado - Unidad 8090-{str(unidad).replace('8090-', '')}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Aprobación Financiera Completa",
        subtitulo_header="Autorización emitida por el área corporativa",
        categoria_badge="PRESUPUESTO APROBADO",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro="¡Excelente noticia! Corporativos ha <strong>APROBADO</strong> la cotización y la autorización financiera está completa. Ya puedes proceder con la continuidad del servicio:",
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("👤 Supervisor Aprobador", f"<strong>{nombre_supervisor}</strong>"),
            ("🔧 Proveedor", proveedor),
            ("💰 Monto Aprobado", f"<span style='color: #10b981; font-weight: bold; font-size: 15px;'>${precio_fmt} MXN</span>")
        ],
        callout_texto="<strong>Próximos pasos:</strong> Continúa con el monitoreo en el sistema y marca la unidad como lista en cuanto el taller concluya la reparación física.",
        callout_tipo="exito",
        autor_proceso=autor
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_taller_aprobado(correo_taller, nombre_taller, ticket, unidad, vehiculo_info, nombre_supervisor=None):
    if not correo_taller or correo_taller.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_supervisor, "Supervisor")
    asunto = f"Autorización Oficial para Inicio de Reparación - Unidad 8090-{str(unidad).replace('8090-', '')}"
    
    detalles = [
        ("🎫 Ticket Vinculado", f"<strong>{ticket}</strong>"),
        ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
        ("🚗 Vehículo", vehiculo_info)
    ]
    if nombre_supervisor:
        detalles.append(("👤 Aprobado por Supervisor", f"<strong>{nombre_supervisor}</strong>"))

    cuerpo_html = generar_plantilla_base(
        titulo_header="Cotización Aprobada: Inicio de Reparación",
        subtitulo_header="Presupuesto y orden autorizados formalmente",
        categoria_badge="COTIZACIÓN APROBADA",
        color_tema="verde",
        saludo=f"Hola <strong>{nombre_taller}</strong>,",
        mensaje_intro="Te informamos que tu cotización ha sido <strong>APROBADA</strong> por la administración automotriz. <strong>Ya puedes empezar a trabajar en la unidad.</strong>",
        detalles_items=detalles,
        callout_texto="<strong>RECORDATORIO:</strong> Cuando concluyas las labores de arreglo o mantenimiento, recuerda <strong>marcar la unidad como ya liberada</strong> en el sistema (botón Entregar Material/Servicio).",
        callout_tipo="exito",
        autor_proceso=autor
    )
    return disparar_correo(correo_taller, asunto, cuerpo_html)


def enviar_correo_taller_facturar(correo_taller, nombre_taller, ticket, unidad, nombre_admin=None):
    if not correo_taller or correo_taller.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"Confirmación de Entrega Técnica - Solicitud de Comprobante Fiscal (Unidad 8090-{str(unidad).replace('8090-', '')})"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Facturación Fiscal Autorizada",
        subtitulo_header="Expediente verificado y validado por Administración",
        categoria_badge="FACTURACIÓN AUTORIZADA",
        color_tema="azul",
        saludo=f"Hola <strong>{nombre_taller}</strong>,",
        mensaje_intro="Te confirmamos que la Administración ha verificado la entrega satisfactoria de la unidad y ha <strong>autorizado el inicio de tu trámite de facturación</strong>.",
        detalles_items=[
            ("🎫 Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad Atendida", f"8090-{str(unidad).replace('8090-', '')}")
        ],
        callout_texto="<strong>Próximo Paso:</strong> Ya puedes ingresar al sistema y subir tu <strong>Factura Fiscal Final (PDF/XML)</strong> correspondiente a este servicio para programar tu pago.",
        callout_tipo="info",
        autor_proceso=autor
    )
    return disparar_correo(correo_taller, asunto, cuerpo_html)


def enviar_correo_liberacion_supervisor(correo_supervisor, nombre_supervisor, ticket, unidad, codigo, nombre_chofer, nombre_taller=None):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_taller, "Taller") if nombre_taller else "Taller Mecánico"
    asunto = f"🔑 Respaldo de Credenciales de Acceso (PIN) - Unidad 8090-{str(unidad).replace('8090-', '')} (Folio {ticket})"
    bloque_pin = (
        f'<div style="background-color: #f8fafc; border: 2px dashed #94a3b8; border-radius: 8px; text-align: center; padding: 18px; margin: 18px 0;">'
        f'<div style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px;">'
        f'PIN de Liberación Generado'
        f'</div>'
        f'<div style="color: #0f172a; font-size: 30px; font-weight: 700; letter-spacing: 6px; font-family: monospace;">'
        f'{codigo}'
        f'</div>'
        f'</div>'
    )

    cuerpo_html = generar_plantilla_base(
        titulo_header="Respaldo de PIN de Liberación",
        subtitulo_header="Credencial generada para recolección de vehículo",
        categoria_badge="RESPALDO DE PIN",
        color_tema="ambar",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro=f"El taller acaba de marcar la unidad como lista y se ha generado el siguiente PIN de liberación para el operador <strong>{nombre_chofer}</strong>:",
        detalles_items=[
            ("🎫 Folio / Ticket", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("👤 Chofer / Operador", nombre_chofer)
        ],
        bloque_destacado=bloque_pin,
        callout_texto="<strong>Nota de Respaldo:</strong> Este correo es un respaldo para supervisión. Si el operador experimenta problemas para visualizar su correo, puedes proporcionarle este PIN para validar la salida física.",
        callout_tipo="info",
        autor_proceso=autor
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_confirmacion_aprobacion_actor(correo_destino, actor, unidad, precio, rol_aprobador="Supervisor"):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"✅ Confirmación de Aprobación Exitosa - Unidad 8090-{str(unidad).replace('8090-', '')}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Aprobación Registrada en Sistema",
        subtitulo_header="Acuse de validación técnica ejecutada exitosamente",
        categoria_badge="APROBACIÓN EXITOSA",
        color_tema="verde",
        saludo=f"Hola <strong>{actor}</strong>,",
        mensaje_intro=f"El sistema ha registrado correctamente su validación y aprobación operativa como <strong>{rol_aprobador}</strong> para el presupuesto de la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong>.",
        detalles_items=[
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("💰 Monto Aprobado", f"<span style='color: #10b981; font-weight: bold;'>${precio:,.2f} MXN</span>"),
            ("🛡️ Rol de Autorización", rol_aprobador)
        ],
        callout_texto="El trámite ha avanzado automáticamente a la siguiente fase operativa en la plataforma.",
        callout_tipo="exito",
        autor_proceso=f"{rol_aprobador}: {actor}"
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_correccion_orden(correo_destino, supervisor, unidad, nombre_admin=None):
    if not correo_destino or correo_destino.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    autor = formatear_nombre_rol(nombre_admin, "Administrador")
    asunto = f"Corrección Requerida: Números de Pedido/Orden - Unidad 8090-{str(unidad).replace('8090-', '')}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Actualización Requerida en Datos de Orden",
        subtitulo_header="Se requiere revisar o corregir números de orden y pedido",
        categoria_badge="CORRECCIÓN REQUERIDA",
        color_tema="ambar",
        saludo=f"Hola <strong>{supervisor}</strong>,",
        mensaje_intro=f"Se le notifica que es necesario <strong>actualizar los datos (números de orden y solicitud de pedido)</strong> correspondientes a la unidad <strong>8090-{str(unidad).replace('8090-', '')}</strong>.",
        detalles_items=[
            ("🚚 Unidad Afectada", f"8090-{str(unidad).replace('8090-', '')}"),
            ("👤 Notificado a", supervisor)
        ],
        callout_texto="El sistema o la administración detectó una discrepancia con estos números. Le solicitamos ingresar a la plataforma, ubicar este ticket en su bandeja de Facturas y actualizar los datos mediante la opción 'Actualizar Datos (Pedido/Orden)'.",
        callout_tipo="alerta",
        autor_proceso=autor
    )
    return disparar_correo(correo_destino, asunto, cuerpo_html)


def enviar_correo_taller_corrige_cotizacion(correo_supervisor, nombre_supervisor, nombre_proveedor, ticket, unidad):
    if not correo_supervisor or correo_supervisor.strip() in ["", "No proporcionado"]:
        return False, "Sin correo"

    asunto = f"Corrección de Cotización Recibida - {unidad}"
    cuerpo_html = generar_plantilla_base(
        titulo_header="Corrección de Cotización Enviada",
        subtitulo_header="El taller ha atendido las observaciones emitidas",
        categoria_badge="COTIZACIÓN CORREGIDA",
        color_tema="azul",
        saludo=f"Hola <strong>{nombre_supervisor}</strong>,",
        mensaje_intro=f"El taller mecánico <strong>{nombre_proveedor}</strong> ha enviado los nuevos precios y los archivos corregidos para el ticket <strong>{ticket}</strong> de la unidad <strong>{unidad}</strong>.",
        detalles_items=[
            ("🎫 Ticket Vinculado", f"<strong>{ticket}</strong>"),
            ("🚚 Unidad", f"8090-{str(unidad).replace('8090-', '')}"),
            ("🔧 Taller Emisor", nombre_proveedor)
        ],
        callout_texto="Por favor ingrese al sistema para revisar los nuevos costos y documentación actualizada, y proceder con la aprobación.",
        callout_tipo="info",
        autor_proceso=formatear_nombre_rol(nombre_proveedor, "Taller")
    )
    return disparar_correo(correo_supervisor, asunto, cuerpo_html)


def enviar_correo_correccion_cotizacion(lista_supervisores, proveedor, unidad, ticket):
    if not lista_supervisores:
        return False, "No hay correos"

    asunto = f"Correcciones de Cotización Recibidas - {proveedor} (Unidad 8090-{str(unidad).replace('8090-', '')})"
    for admin in lista_supervisores:
        correo_sup = admin.get('correo') if isinstance(admin, dict) else getattr(admin, 'correo', None)
        if not correo_sup:
            continue
        nombre_sup = admin.get('nombre', 'Supervisor') if isinstance(admin, dict) else getattr(admin, 'nombre', 'Supervisor')
        puesto_str = f" ({admin.get('puesto')})" if isinstance(admin, dict) and admin.get('puesto') else ""
        cuerpo_html = generar_plantilla_base(
            titulo_header="Correcciones de Cotización Recibidas",
            subtitulo_header="Recomendaciones atendidas por el taller",
            categoria_badge="CORRECCIONES LISTAS",
            color_tema="azul",
            saludo=f"Hola <strong>{nombre_sup}{puesto_str}</strong>,",
            mensaje_intro="Se le notifica que el taller mecánico ha atendido sus recomendaciones previas y ha subido los precios corregidos y los PDFs actualizados:",
            detalles_items=[
                ("🔧 Taller Emisor", f"<strong>{proveedor}</strong>"),
                ("🚚 Unidad Atendida", f"8090-{str(unidad).replace('8090-', '')}"),
                ("🎫 Ticket Vinculado", f"<strong>{ticket}</strong>")
            ],
            callout_texto="Ingrese al panel de Supervisión para continuar con la validación técnica y asignación de órdenes de la cotización modificada.",
            callout_tipo="info",
            autor_proceso=formatear_nombre_rol(proveedor, "Taller")
        )
        disparar_correo(correo_sup, asunto, cuerpo_html)
    return True, "Enviado"
