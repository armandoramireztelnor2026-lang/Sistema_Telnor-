import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, session

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

