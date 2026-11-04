import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, session, send_file
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

configuracion_bp = Blueprint('configuracion', __name__)

CONFIG_FILE = "configuracion_sistema.json"
FACTURAS_FILE = "facturas.json"

def leer_json(ruta):
    if not os.path.exists(ruta):
        return {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error leyendo {ruta}: {e}")
        return {}

def escribir_json(ruta, data):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error escribiendo {ruta}: {e}")
        return False

def obtener_configuracion():
    data = leer_json(CONFIG_FILE)
    if not data:
        data = {
            "correo_emisor": "armandoramireztelnor2026@gmail.com",
            "codigo_emisor": "zgdhbgcpuobszybi",
            "servidor_smtp": "smtp.gmail.com",
            "puerto_smtp": 587,
            "nombre_remitente": "Sistema Automotriz Telnor",
            "cuentas_correo": [
                {
                    "id": "1",
                    "correo": "armandoramireztelnor2026@gmail.com",
                    "codigo": "zgdhbgcpuobszybi",
                    "servidor_smtp": "smtp.gmail.com",
                    "puerto_smtp": 587,
                    "nombre": "Principal (Gmail)",
                    "activa": True,
                    "fecha_registro": "2026-11-02 22:45:00"
                }
            ],
            "presupuesto_total": 500000.0,
            "limite_cotizaciones_caras": 10000.0,
            "fecha_actualizacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actualizado_por": "Sistema"
        }
        escribir_json(CONFIG_FILE, data)
    return data

def calcular_metricas_presupuesto(conf=None):
    if conf is None:
        conf = obtener_configuracion()
    presupuesto_total = float(conf.get("presupuesto_total", 500000.0) or 500000.0)
    ids_reseteados = set(str(i) for i in conf.get("ids_reseteados", []))
    fecha_reseteo = str(conf.get("fecha_reseteo_presupuesto", "")).strip()

    facturas_data = leer_json(FACTURAS_FILE)
    facs = facturas_data.get("facturas", [])

    comprometido = 0.0
    confirmadas = []

    for fc in facs:
        # Excluir rechazadas o canceladas
        st = str(fc.get("estado", "")).strip().lower()
        if st in ["rechazada", "cancelada", "cancelado_cotizacion_cara"] or fc.get("cancelado"):
            continue

        es_confirmada = False
        if fc.get("aprobado_admin") is True or fc.get("aprobado_corp") is True:
            es_confirmada = True
        elif st in ["confirmada", "archivado", "revision_factura", "espera_aprobacion_pin", "retrabajo", "en asignacion/retrabajo"]:
            es_confirmada = True

        if es_confirmada:
            fc_id = str(fc.get("id"))
            # Si el ticket ya formaba parte del ciclo reseteado por Jefatura, se excluye del consumo actual
            if fc_id in ids_reseteados:
                continue

            if fecha_reseteo:
                ts_factura = str(fc.get("timestamp_aprobacion") or fc.get("fecha") or fc.get("fecha_creacion") or "")
                if ts_factura and ts_factura < fecha_reseteo and not fc.get("nuevo_ciclo_presupuesto"):
                    continue

            p = float(fc.get("precio", 0) or fc.get("precio_estimado", 0) or 0)
            comprometido += p
            confirmadas.append({
                "id": fc.get("id"),
                "id_reporte": fc.get("id_reporte") or fc.get("numero_reporte") or fc.get("id"),
                "unidad": fc.get("unidad") or "N/A",
                "proveedor": fc.get("proveedor") or fc.get("taller") or "N/A",
                "cope": fc.get("cope") or "N/A",
                "precio": p,
                "estado": fc.get("estado") or "Confirmada",
                "fecha": str(fc.get("timestamp_aprobacion") or fc.get("fecha_creacion") or fc.get("timestamp") or "").split("T")[0] or "--"
            })

    # Ordenar por fecha descendente
    confirmadas.sort(key=lambda x: str(x.get("id", "")), reverse=True)

    restante = max(0.0, presupuesto_total - comprometido)
    pct = round((comprometido / presupuesto_total) * 100, 2) if presupuesto_total > 0 else 0.0

    return {
        "presupuesto_total": presupuesto_total,
        "dinero_comprometido": comprometido,
        "presupuesto_restante": restante,
        "porcentaje_consumido": pct,
        "total_confirmadas": len(confirmadas),
        "cotizaciones_confirmadas": confirmadas,
        "fecha_reseteo_presupuesto": conf.get("fecha_reseteo_presupuesto", "--"),
        "monto_reseteado_acumulado": float(conf.get("monto_reseteado_acumulado", 0.0) or 0.0)
    }



def es_usuario_autorizado():
    u = session.get("usuario")
    if not isinstance(u, dict):
        return False
    return u.get("rol") == "administracion"

# =========================================================================
# RUTAS DE CONSULTA Y EDICIÓN DE CONFIGURACIÓN
# =========================================================================

@configuracion_bp.route("/api/configuracion", methods=["GET"])
def obtener_configuracion_completa():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    conf = obtener_configuracion()
    metricas = calcular_metricas_presupuesto(conf)

    codigo_raw = str(conf.get("codigo_emisor", "")).strip()
    codigo_enmascarado = (codigo_raw[:3] + "••••••••••" + codigo_raw[-3:]) if len(codigo_raw) >= 6 else "••••••••"

    return jsonify({
        "status": "success",
        "configuracion": {
            "correo_emisor": conf.get("correo_emisor", "armandoramireztelnor2026@gmail.com"),
            "codigo_emisor": codigo_raw,
            "codigo_emisor_enmascarado": codigo_enmascarado,
            "servidor_smtp": conf.get("servidor_smtp", "smtp.gmail.com"),
            "puerto_smtp": conf.get("puerto_smtp", 587),
            "nombre_remitente": conf.get("nombre_remitente", "Sistema Automotriz Telnor"),
            "cuentas_correo": conf.get("cuentas_correo", []),
            "envio_automatico_activo": conf.get("envio_automatico_activo", True),
            "limite_cotizaciones_caras": float(conf.get("limite_cotizaciones_caras", 10000.0) or 10000.0),
            "fecha_actualizacion": conf.get("fecha_actualizacion", "--"),
            "actualizado_por": conf.get("actualizado_por", "--")
        },
        "presupuesto": metricas
    })


@configuracion_bp.route("/api/configuracion/correo/guardar", methods=["POST"])
def guardar_correo_emisor():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    correo = str(datos.get("correo", "")).strip()
    codigo = str(datos.get("codigo", "")).strip()
    servidor = str(datos.get("servidor_smtp", "")).strip() or "smtp.gmail.com"
    puerto = int(datos.get("puerto_smtp", 587) or 587)
    nombre = str(datos.get("nombre", "")).strip() or "Emisor Telnor"

    if not correo or "@" not in correo:
        return jsonify({"status": "error", "message": "Debes proporcionar un correo electrónico válido."}), 400

    if not codigo:
        return jsonify({"status": "error", "message": "Debes proporcionar el código o contraseña de aplicación."}), 400

    conf = obtener_configuracion()
    if (str(conf.get("correo_emisor", "")).strip().lower() == correo.lower() and
        str(conf.get("codigo_emisor", "")).strip() == codigo and
        str(conf.get("servidor_smtp", "smtp.gmail.com")).strip().lower() == servidor.lower() and
        int(conf.get("puerto_smtp", 587) or 587) == puerto):
        return jsonify({"status": "no_change", "message": "⚠️ Debes actualizar como mínimo un dato."}), 200

    conf["correo_emisor"] = correo
    conf["codigo_emisor"] = codigo
    conf["servidor_smtp"] = servidor
    conf["puerto_smtp"] = puerto
    conf["nombre_remitente"] = nombre

    # Actualizar o agregar en cuentas_correo
    cuentas = conf.get("cuentas_correo", [])
    encontrada = False
    for c in cuentas:
        if c.get("correo", "").strip().lower() == correo.lower():
            c["codigo"] = codigo
            c["servidor_smtp"] = servidor
            c["puerto_smtp"] = puerto
            c["nombre"] = nombre
            c["activa"] = True
            encontrada = True
        else:
            c["activa"] = False

    if not encontrada:
        nuevo_id = str(len(cuentas) + 1)
        cuentas.append({
            "id": nuevo_id,
            "correo": correo,
            "codigo": codigo,
            "servidor_smtp": servidor,
            "puerto_smtp": puerto,
            "nombre": nombre,
            "activa": True,
            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    conf["cuentas_correo"] = cuentas
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    conf["actualizado_por"] = f"{subrol}: {session['usuario'].get('usuario')}"

    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Credenciales de correo emisor actualizadas correctamente ({correo}).",
        "correo_emisor": correo
    })


@configuracion_bp.route("/api/configuracion/correo/agregar", methods=["POST"])
def agregar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    correo = str(datos.get("correo", "")).strip()
    codigo = str(datos.get("codigo", "")).strip()
    servidor = str(datos.get("servidor_smtp", "")).strip() or "smtp.gmail.com"
    puerto = int(datos.get("puerto_smtp", 587) or 587)
    nombre = str(datos.get("nombre", "")).strip() or "Cuenta Secundaria"
    activar = bool(datos.get("activar", False))

    if not correo or "@" not in correo or not codigo:
        return jsonify({"status": "error", "message": "Faltan datos obligatorios (correo o código)."}), 400

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])

    for c in cuentas:
        if c.get("correo", "").strip().lower() == correo.lower():
            return jsonify({"status": "error", "message": f"La cuenta {correo} ya se encuentra registrada."}), 400

    if activar:
        for c in cuentas:
            c["activa"] = False
        conf["correo_emisor"] = correo
        conf["codigo_emisor"] = codigo
        conf["servidor_smtp"] = servidor
        conf["puerto_smtp"] = puerto
        conf["nombre_remitente"] = nombre

    cuentas.append({
        "id": str(len(cuentas) + 1),
        "correo": correo,
        "codigo": codigo,
        "servidor_smtp": servidor,
        "puerto_smtp": puerto,
        "nombre": nombre,
        "activa": activar,
        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    conf["cuentas_correo"] = cuentas
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {correo} agregada exitosamente.",
        "cuentas": cuentas
    })


@configuracion_bp.route("/api/configuracion/correo/activar", methods=["POST"])
def activar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    cuenta_id = str(datos.get("id", "")).strip()
    correo = str(datos.get("correo", "")).strip().lower()

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])
    cuenta_seleccionada = None

    for c in cuentas:
        if (cuenta_id and str(c.get("id")) == cuenta_id) or (correo and c.get("correo", "").lower() == correo):
            c["activa"] = True
            cuenta_seleccionada = c
        else:
            c["activa"] = False

    if not cuenta_seleccionada:
        return jsonify({"status": "error", "message": "Cuenta de correo no encontrada."}), 404

    conf["correo_emisor"] = cuenta_seleccionada.get("correo")
    conf["codigo_emisor"] = cuenta_seleccionada.get("codigo")
    conf["servidor_smtp"] = cuenta_seleccionada.get("servidor_smtp", "smtp.gmail.com")
    conf["puerto_smtp"] = cuenta_seleccionada.get("puerto_smtp", 587)
    conf["nombre_remitente"] = cuenta_seleccionada.get("nombre", "Sistema Automotriz Telnor")
    conf["envio_automatico_activo"] = True
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {conf['correo_emisor']} activada para el envío de correos automáticos.",
        "correo_activo": conf["correo_emisor"],
        "envio_automatico_activo": True
    })


@configuracion_bp.route("/api/configuracion/correo/desactivar", methods=["POST"])
def desactivar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    cuenta_id = str(datos.get("id", "")).strip()
    correo = str(datos.get("correo", "")).strip().lower()

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])
    cuenta_desactivada = None

    for c in cuentas:
        if (cuenta_id and str(c.get("id")) == cuenta_id) or (correo and c.get("correo", "").lower() == correo):
            c["activa"] = False
            cuenta_desactivada = c

    if not cuenta_desactivada:
        return jsonify({"status": "error", "message": "Cuenta de correo no encontrada."}), 404

    # Pausar el emisor automático
    conf["envio_automatico_activo"] = False
    conf["correo_emisor_anterior"] = conf.get("correo_emisor")
    conf["correo_emisor"] = ""
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {cuenta_desactivada.get('correo')} desactivada. Los correos automáticos han sido pausados hasta activar una cuenta.",
        "correo_activo": "",
        "envio_automatico_activo": False
    })


@configuracion_bp.route("/api/configuracion/correo/eliminar", methods=["POST"])
def eliminar_cuenta_correo():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    cuenta_id = str(datos.get("id", "")).strip()
    correo = str(datos.get("correo", "")).strip().lower()

    conf = obtener_configuracion()
    cuentas = conf.get("cuentas_correo", [])
    if len(cuentas) <= 1:
        return jsonify({"status": "error", "message": "No se puede eliminar la única cuenta registrada."}), 400

    nuevas_cuentas = []
    eliminada = None
    for c in cuentas:
        if (cuenta_id and str(c.get("id")) == cuenta_id) or (correo and c.get("correo", "").lower() == correo):
            eliminada = c
        else:
            nuevas_cuentas.append(c)

    if not eliminada:
        return jsonify({"status": "error", "message": "Cuenta no encontrada."}), 404

    if eliminada.get("activa") or (conf.get("correo_emisor", "").lower() == eliminada.get("correo", "").lower()):
        nuevas_cuentas[0]["activa"] = True
        conf["correo_emisor"] = nuevas_cuentas[0]["correo"]
        conf["codigo_emisor"] = nuevas_cuentas[0]["codigo"]
        conf["servidor_smtp"] = nuevas_cuentas[0].get("servidor_smtp", "smtp.gmail.com")
        conf["puerto_smtp"] = nuevas_cuentas[0].get("puerto_smtp", 587)
        conf["envio_automatico_activo"] = True

    conf["cuentas_correo"] = nuevas_cuentas
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json(CONFIG_FILE, conf)

    return jsonify({
        "status": "success",
        "message": f"Cuenta {eliminada.get('correo')} eliminada exitosamente.",
        "cuentas": nuevas_cuentas,
        "correo_activo": conf.get("correo_emisor", "")
    })


@configuracion_bp.route("/api/configuracion/correo/probar", methods=["POST"])
def probar_correo_smtp():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    destino = str(datos.get("correo_destino", "")).strip()
    
    # Credenciales a probar (pueden ser las que se envíen en el form o las activas)
    conf = obtener_configuracion()
    correo_test = str(datos.get("correo", "")).strip() or conf.get("correo_emisor")
    codigo_test = str(datos.get("codigo", "")).strip() or conf.get("codigo_emisor")
    servidor_test = str(datos.get("servidor_smtp", "")).strip() or conf.get("servidor_smtp", "smtp.gmail.com")
    puerto_test = int(datos.get("puerto_smtp", 587) or conf.get("puerto_smtp", 587) or 587)

    if not destino or "@" not in destino:
        # Fallback al correo de sesion del usuario o al propio emisor
        destino = session["usuario"].get("datos_perfil", {}).get("correo") or correo_test

    if not correo_test or not codigo_test:
        return jsonify({"status": "error", "message": "Faltan credenciales (correo o código de emisor) para realizar la prueba."}), 400

    try:
        msg = MIMEMultipart()
        msg['From'] = correo_test
        msg['To'] = destino
        msg['Subject'] = "✅ Prueba Exitosa de Conexión SMTP - Telnor Automotriz"

        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario_actor = session["usuario"].get("usuario", "Jefatura")

        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f1f5f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border-left: 6px solid #10b981; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #0f172a; margin-top: 0;">✅ Verificación de Conexión SMTP Exitosa</h2>
                <p style="color: #334155; font-size: 15px; line-height: 1.5;">
                    Este correo confirma que el servidor de notificaciones de <strong>Telnor Automotriz</strong> está conectado y autenticado correctamente con el servidor SMTP.
                </p>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 4px 0; color: #475569; font-size: 13px;"><strong>Correo Emisor:</strong> {correo_test}</p>
                    <p style="margin: 4px 0; color: #475569; font-size: 13px;"><strong>Servidor SMTP:</strong> {servidor_test}:{puerto_test}</p>
                    <p style="margin: 4px 0; color: #475569; font-size: 13px;"><strong>Destinatario de Prueba:</strong> {destino}</p>
                    <p style="margin: 4px 0; color: #475569; font-size: 13px;"><strong>Prueba realizada por:</strong> {usuario_actor}</p>
                    <p style="margin: 4px 0; color: #475569; font-size: 13px;"><strong>Fecha y Hora:</strong> {fecha_hora}</p>
                </div>
                <p style="color: #10b981; font-weight: bold; font-size: 14px; margin-bottom: 0;">
                    El sistema de notificaciones está listo para enviar códigos y alertas de tickets de forma automática.
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo, 'html', 'utf-8'))

        server = smtplib.SMTP(servidor_test, puerto_test, timeout=12)
        server.starttls()
        server.login(correo_test, codigo_test)
        server.send_message(msg)
        server.quit()

        return jsonify({
            "status": "success",
            "message": f"✅ Correo de prueba enviado con éxito a {destino} usando {correo_test}."
        })
    except Exception as e:
        print(f"Error en prueba SMTP: {e}")
        return jsonify({
            "status": "error",
            "message": f"❌ Error de autenticación SMTP: {str(e)}. Verifica que el correo sea correcto y que el código sea una 'Contraseña de Aplicación' válida generada en tu cuenta de Google."
        }), 400


@configuracion_bp.route("/api/configuracion/presupuesto/guardar", methods=["POST"])
def guardar_presupuesto():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    try:
        nuevo_presupuesto = float(datos.get("presupuesto_total", 0))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "El monto del presupuesto debe ser un número válido."}), 400

    if nuevo_presupuesto < 0:
        return jsonify({"status": "error", "message": "El presupuesto no puede ser negativo."}), 400

    conf = obtener_configuracion()
    conf["presupuesto_total"] = nuevo_presupuesto
    conf["fecha_actualizacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    conf["actualizado_por"] = f"{subrol}: {session['usuario'].get('usuario')}"

    escribir_json(CONFIG_FILE, conf)
    metricas = calcular_metricas_presupuesto(conf)

    return jsonify({
        "status": "success",
        "message": f"Presupuesto total actualizado a ${nuevo_presupuesto:,.2f} MXN con éxito.",
        "presupuesto": metricas
    })


@configuracion_bp.route("/api/configuracion/presupuesto/resetear", methods=["POST"])
def resetear_presupuesto():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    conf = obtener_configuracion()
    metricas = calcular_metricas_presupuesto(conf)
    monto_utilizado_previo = float(metricas.get("dinero_comprometido", 0.0))

    facturas_data = leer_json(FACTURAS_FILE)
    facs = facturas_data.get("facturas", [])

    ids_confirmadas = []
    for fc in facs:
        st = str(fc.get("estado", "")).strip().lower()
        if st in ["rechazada", "cancelada", "cancelado_cotizacion_cara"] or fc.get("cancelado"):
            continue
        es_confirmada = False
        if fc.get("aprobado_admin") is True or fc.get("aprobado_corp") is True:
            es_confirmada = True
        elif st in ["confirmada", "archivado", "revision_factura", "espera_aprobacion_pin", "retrabajo", "en asignacion/retrabajo"]:
            es_confirmada = True
        if es_confirmada:
            ids_confirmadas.append(str(fc.get("id")))

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subrol = session["usuario"].get("datos_perfil", {}).get("subrol") or "Jefatura"
    usuario_nom = session["usuario"].get("usuario", "Jefatura")

    conf["fecha_reseteo_presupuesto"] = now_str
    conf["ids_reseteados"] = ids_confirmadas
    conf["monto_reseteado_acumulado"] = monto_utilizado_previo
    conf["reseteado_por"] = f"{subrol}: {usuario_nom}"
    conf["fecha_actualizacion"] = now_str
    conf["actualizado_por"] = f"{subrol}: {usuario_nom}"

    escribir_json(CONFIG_FILE, conf)

    metricas_nuevas = calcular_metricas_presupuesto(conf)

    return jsonify({
        "status": "success",
        "message": f"Presupuesto utilizado reseteado correctamente. Se eliminaron ${monto_utilizado_previo:,.2f} MXN del cálculo acumulado. Saldo disponible restablecido a ${metricas_nuevas['presupuesto_restante']:,.2f} MXN.",
        "presupuesto": metricas_nuevas
    })


@configuracion_bp.route("/api/configuracion/limite_caras/guardar", methods=["POST"])
def guardar_limite_caras():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    datos = request.get_json(silent=True) or request.form
    try:
        nuevo_limite = float(datos.get("limite_cotizaciones_caras", 10000.0))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "El límite de cotización debe ser un número válido."}), 400

    if nuevo_limite <= 0:
        return jsonify({"status": "error", "message": "El límite debe ser mayor a 0."}), 400

    conf = obtener_configuracion()
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
    })

@configuracion_bp.route("/api/configuracion/presupuesto/exportar_excel", methods=["GET"])
def exportar_presupuesto_excel():
    if not es_usuario_autorizado():
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    conf = obtener_configuracion()
    metricas = calcular_metricas_presupuesto(conf)
    cotizaciones = metricas.get("cotizaciones_confirmadas", [])

    wb = openpyxl.Workbook()

    # PALETA DE COLORES INSTITUCIONAL ANALÍTICA / CONFIGURACIONES
    fill_navy = PatternFill(start_color="112641", end_color="112641", fill_type="solid")
    fill_green = PatternFill(start_color="40916C", end_color="40916C", fill_type="solid")
    fill_sub_header = PatternFill(start_color="1F395A", end_color="1F395A", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_card = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_card_amber = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    fill_card_green = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    fill_card_blue = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

    font_title = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="CBD5E1")
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_section = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_normal = Font(name="Segoe UI", size=10, color="1E293B")
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
    font_total = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_amber_bold = Font(name="Segoe UI", size=10, bold=True, color="B45309")
    font_green_bold = Font(name="Segoe UI", size=10, bold=True, color="047857")
    font_blue_bold = Font(name="Segoe UI", size=10, bold=True, color="0284C7")

    border_thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================
    # HOJA 1: DESGLOSE PRESUPUESTO
    # =========================================================
    ws1 = wb.active
    ws1.title = "Desglose Presupuesto"
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:G1")
    ws1["A1"] = "SISTEMA DE FACTURACION CENTRAL - CONTROL PRESUPUESTAL Y DESGLOSE"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_navy
    ws1["A1"].alignment = align_center
    ws1.row_dimensions[1].height = 36

    ws1.merge_cells("A2:G2")
    ws1["A2"] = f"Reporte de Desglose de Cotizaciones Confirmadas | Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Jefatura Automotriz"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = fill_navy
    ws1["A2"].alignment = align_center
    ws1.row_dimensions[2].height = 22

    # SECCIÓN METRICAS
    ws1.merge_cells("A4:G4")
    ws1["A4"] = "📊 BALANCE FINANCIERO DEL CICLO ACTUAL (CONFIGURACIONES DE JEFATURA)"
    ws1["A4"].font = font_section
    ws1["A4"].fill = fill_sub_header
    ws1["A4"].alignment = align_left
    ws1.row_dimensions[4].height = 24

    total_pres = float(metricas.get("presupuesto_total", 0))
    comp_pres = float(metricas.get("dinero_comprometido", 0))
    rest_pres = float(metricas.get("presupuesto_restante", 0))
    pct_pres = float(metricas.get("porcentaje_consumido", 0))

    # Tarjetas Fila 5 (Etiquetas) y Fila 6 (Valores)
    ws1.merge_cells("A5:B5")
    ws1["A5"] = "PRESUPUESTO ASIGNADO"
    ws1["A5"].font = Font(name="Segoe UI", size=9, bold=True, color="0369A1")
    ws1["A5"].fill = fill_card_blue
    ws1["A5"].alignment = align_center
    for c in ["A5", "B5"]: ws1[c].border = border_thin

    ws1.merge_cells("A6:B6")
    ws1["A6"] = f"${total_pres:,.2f} MXN"
    ws1["A6"].font = Font(name="Segoe UI", size=13, bold=True, color="0284C7")
    ws1["A6"].fill = fill_card_blue
    ws1["A6"].alignment = align_center
    for c in ["A6", "B6"]: ws1[c].border = border_thin

    ws1.merge_cells("C5:D5")
    ws1["C5"] = "DINERO EN COTIZACIONES"
    ws1["C5"].font = Font(name="Segoe UI", size=9, bold=True, color="B45309")
    ws1["C5"].fill = fill_card_amber
    ws1["C5"].alignment = align_center
    for c in ["C5", "D5"]: ws1[c].border = border_thin

    ws1.merge_cells("C6:D6")
    ws1["C6"] = f"${comp_pres:,.2f} MXN"
    ws1["C6"].font = Font(name="Segoe UI", size=13, bold=True, color="D97706")
    ws1["C6"].fill = fill_card_amber
    ws1["C6"].alignment = align_center
    for c in ["C6", "D6"]: ws1[c].border = border_thin

    ws1.merge_cells("E5:F5")
    ws1["E5"] = "PRESUPUESTO DISPONIBLE"
    ws1["E5"].font = Font(name="Segoe UI", size=9, bold=True, color="047857")
    ws1["E5"].fill = fill_card_green
    ws1["E5"].alignment = align_center
    for c in ["E5", "F5"]: ws1[c].border = border_thin

    ws1.merge_cells("E6:F6")
    ws1["E6"] = f"${rest_pres:,.2f} MXN"
    ws1["E6"].font = Font(name="Segoe UI", size=13, bold=True, color="10B981")
    ws1["E6"].fill = fill_card_green
    ws1["E6"].alignment = align_center
    for c in ["E6", "F6"]: ws1[c].border = border_thin

    ws1["G5"] = "% UTILIZADO"
    ws1["G5"].font = Font(name="Segoe UI", size=9, bold=True, color="475569")
    ws1["G5"].fill = fill_card
    ws1["G5"].alignment = align_center
    ws1["G5"].border = border_thin

    ws1["G6"] = f"{pct_pres:.2f} %"
    ws1["G6"].font = Font(name="Segoe UI", size=13, bold=True, color="0F172A")
    ws1["G6"].fill = fill_card
    ws1["G6"].alignment = align_center
    ws1["G6"].border = border_thin

    ws1.row_dimensions[5].height = 20
    ws1.row_dimensions[6].height = 26

    # TABLA DE COTIZACIONES
    ws1.merge_cells("A8:G8")
    ws1["A8"] = f"📋 LISTADO DETALLADO DE COTIZACIONES CONFIRMADAS ({len(cotizaciones)} tickets que restan presupuesto)"
    ws1["A8"].font = font_section
    ws1["A8"].fill = fill_sub_header
    ws1["A8"].alignment = align_left
    ws1.row_dimensions[8].height = 24

    headers = [
        "No. Ticket / Folio",
        "No. Unidad (Eco)",
        "Taller Mecánico / Proveedor",
        "Centro de Trabajo (COPE)",
        "Monto Recortado (s/IVA)",
        "Estado Operativo",
        "Fecha Confirmación"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws1.cell(row=9, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_green
        cell.alignment = align_center
        cell.border = border_thin
    ws1.row_dimensions[9].height = 28

    row_num = 10
    for item in cotizaciones:
        p = float(item.get("precio", 0) or 0)
        raw_u = str(item.get("unidad", "")).strip()
        u_str = raw_u if raw_u.startswith("8090-") else (f"8090-{raw_u}" if raw_u else "--")
        is_zebra = (row_num % 2 == 0)

        c1 = ws1.cell(row=row_num, column=1, value=str(item.get("id_reporte") or item.get("id") or ""))
        c1.font = font_amber_bold
        c1.alignment = align_center

        c2 = ws1.cell(row=row_num, column=2, value=u_str)
        c2.font = font_blue_bold
        c2.alignment = align_center

        c3 = ws1.cell(row=row_num, column=3, value=str(item.get("proveedor") or "Sin especificar"))
        c3.font = font_normal
        c3.alignment = align_left

        c4 = ws1.cell(row=row_num, column=4, value=str(item.get("cope") or "--"))
        c4.font = font_normal
        c4.alignment = align_center

        c5 = ws1.cell(row=row_num, column=5, value=p)
        c5.font = font_green_bold
        c5.alignment = align_right
        c5.number_format = "$#,##0.00"

        c6 = ws1.cell(row=row_num, column=6, value=str(item.get("estado") or "Confirmada"))
        c6.font = font_normal
        c6.alignment = align_center

        c7 = ws1.cell(row=row_num, column=7, value=str(item.get("fecha") or "--"))
        c7.font = font_normal
        c7.alignment = align_center

        for c_i in range(1, 8):
            c_obj = ws1.cell(row=row_num, column=c_i)
            c_obj.border = border_thin
            if is_zebra: c_obj.fill = fill_zebra

        ws1.row_dimensions[row_num].height = 22
        row_num += 1

    # Fila de Totales
    if row_num > 10:
        ws1.merge_cells(f"A{row_num}:D{row_num}")
        ws1[f"A{row_num}"] = "TOTAL COMPROMETIDO EN EL CICLO ACTUAL:"
        ws1[f"A{row_num}"].font = font_total
        ws1[f"A{row_num}"].fill = fill_navy
        ws1[f"A{row_num}"].alignment = align_right

        for ci in range(1, 5):
            ws1[f"{get_column_letter(ci)}{row_num}"].border = border_thin
            ws1[f"{get_column_letter(ci)}{row_num}"].fill = fill_navy

        c_sum = ws1[f"E{row_num}"]
        c_sum.value = f"=SUM(E10:E{row_num-1})"
        c_sum.font = font_total
        c_sum.fill = fill_navy
        c_sum.alignment = align_right
        c_sum.number_format = "$#,##0.00"
        c_sum.border = border_thin

        for ci in (6, 7):
            c_b = ws1[f"{get_column_letter(ci)}{row_num}"]
            c_b.value = ""
            c_b.fill = fill_navy
            c_b.border = border_thin

        ws1.row_dimensions[row_num].height = 26

    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 18)
    ws1.column_dimensions['C'].width = 34
    ws1.column_dimensions['E'].width = 24

    # =========================================================
    # HOJA 2: RESUMEN POR TALLER Y COPE
    # =========================================================
    ws2 = wb.create_sheet(title="Resumen por Taller y COPE")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:E1")
    ws2["A1"] = "DISTRIBUCIÓN DEL GASTO PRESUPUESTAL POR TALLER Y POR COPE"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_navy
    ws2["A1"].alignment = align_center
    ws2.row_dimensions[1].height = 36

    ws2.merge_cells("A2:E2")
    ws2["A2"] = f"Agrupación y Estadísticas de Presupuesto Comprometido | Jefatura Automotriz"
    ws2["A2"].font = font_subtitle
    ws2["A2"].fill = fill_navy
    ws2["A2"].alignment = align_center
    ws2.row_dimensions[2].height = 22

    # Agrupar por Taller
    taller_gastos = {}
    taller_counts = {}
    cope_gastos = {}
    cope_counts = {}

    for it in cotizaciones:
        t = str(it.get("proveedor") or "Sin especificar")
        cp = str(it.get("cope") or "No especificado")
        pr = float(it.get("precio", 0) or 0)

        taller_gastos[t] = taller_gastos.get(t, 0.0) + pr
        taller_counts[t] = taller_counts.get(t, 0) + 1
        cope_gastos[cp] = cope_gastos.get(cp, 0.0) + pr
        cope_counts[cp] = cope_counts.get(cp, 0) + 1

    # Tabla Talleres
    ws2.merge_cells("A4:E4")
    ws2["A4"] = "🔧 CONSUMO DE PRESUPUESTO POR TALLER MECÁNICO PROVEEDOR"
    ws2["A4"].font = font_section
    ws2["A4"].fill = fill_sub_header
    ws2["A4"].alignment = align_left
    ws2.row_dimensions[4].height = 24

    h_taller = ["Taller Mecánico / Proveedor", "Tickets Atendidos", "Monto Total Consumido (s/IVA)", "% del Gasto Comprometido", "Ticket Promedio"]
    for col_idx, h in enumerate(h_taller, 1):
        cell = ws2.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_green
        cell.alignment = align_center
        cell.border = border_thin
    ws2.row_dimensions[5].height = 26

    r_t = 6
    total_gastado = sum(taller_gastos.values()) or 1.0

    for t_nom, monto in sorted(taller_gastos.items(), key=lambda x: x[1], reverse=True):
        cnt = taller_counts.get(t_nom, 0)
        pct = (monto / total_gastado) * 100
        prom = monto / cnt if cnt > 0 else 0

        c1 = ws2.cell(row=r_t, column=1, value=t_nom)
        c1.alignment = align_left
        c2 = ws2.cell(row=r_t, column=2, value=cnt)
        c2.alignment = align_center
        c3 = ws2.cell(row=r_t, column=3, value=monto)
        c3.alignment = align_right
        c3.number_format = "$#,##0.00"
        c4 = ws2.cell(row=r_t, column=4, value=f"{pct:.2f} %")
        c4.alignment = align_center
        c5 = ws2.cell(row=r_t, column=5, value=prom)
        c5.alignment = align_right
        c5.number_format = "$#,##0.00"

        for ci in range(1, 6):
            c_obj = ws2.cell(row=r_t, column=ci)
            c_obj.font = font_normal
            c_obj.border = border_thin
            if r_t % 2 == 0: c_obj.fill = fill_zebra

        ws2.row_dimensions[r_t].height = 22
        r_t += 1

    # Tabla COPEs
    r_c_start = r_t + 2
    ws2.merge_cells(f"A{r_c_start}:E{r_c_start}")
    ws2[f"A{r_c_start}"] = "🏢 CONSUMO DE PRESUPUESTO POR CENTRO DE TRABAJO (COPE)"
    ws2[f"A{r_c_start}"].font = font_section
    ws2[f"A{r_c_start}"].fill = fill_sub_header
    ws2[f"A{r_c_start}"].alignment = align_left
    ws2.row_dimensions[r_c_start].height = 24

    h_cope = ["Centro de Trabajo (COPE)", "Tickets Confirmados", "Monto Total Consumido (s/IVA)", "% del Gasto Comprometido", "Ticket Promedio"]
    for col_idx, h in enumerate(h_cope, 1):
        cell = ws2.cell(row=r_c_start+1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_green
        cell.alignment = align_center
        cell.border = border_thin
    ws2.row_dimensions[r_c_start+1].height = 26

    r_c = r_c_start + 2
    for cp_nom, monto in sorted(cope_gastos.items(), key=lambda x: x[1], reverse=True):
        cnt = cope_counts.get(cp_nom, 0)
        pct = (monto / total_gastado) * 100
        prom = monto / cnt if cnt > 0 else 0

        c1 = ws2.cell(row=r_c, column=1, value=cp_nom)
        c1.alignment = align_left
        c2 = ws2.cell(row=r_c, column=2, value=cnt)
        c2.alignment = align_center
        c3 = ws2.cell(row=r_c, column=3, value=monto)
        c3.alignment = align_right
        c3.number_format = "$#,##0.00"
        c4 = ws2.cell(row=r_c, column=4, value=f"{pct:.2f} %")
        c4.alignment = align_center
        c5 = ws2.cell(row=r_c, column=5, value=prom)
        c5.alignment = align_right
        c5.number_format = "$#,##0.00"

        for ci in range(1, 6):
            c_obj = ws2.cell(row=r_c, column=ci)
            c_obj.font = font_normal
            c_obj.border = border_thin
            if r_c % 2 == 0: c_obj.fill = fill_zebra

        ws2.row_dimensions[r_c].height = 22
        r_c += 1

    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 20)
    ws2.column_dimensions['A'].width = 34

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"Desglose_Presupuesto_Jefatura_{timestamp}.xlsx"

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre_archivo
    )
