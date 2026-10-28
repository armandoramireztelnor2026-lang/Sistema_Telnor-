# =========================================================
# ARCHIVO: rutas_reportes.py
# PROPÓSITO: Backend exclusivo para la gestión de reportes
# =========================================================
from flask import Blueprint, request, jsonify, session
import os
from werkzeug.utils import secure_filename
import json
import datetime

from notificaciones import (
    enviar_correo_nueva_orden,
    enviar_correo_nuevo_ticket,
    enviar_correo_confirmacion_reporte,
    enviar_correo_ticket_rechazado,
    enviar_correo_retrabajo_taller,
    enviar_correo_cancelacion_retrabajo_chofer,
)

reportes_bp = Blueprint("reportes_bp", __name__)

def leer_json(archivo):
    if not os.path.exists(archivo):
        if "retrabajo" in archivo: return {"retrabajos": []}
        if "factura" in archivo: return {"facturas": []}
        if "ticket" in archivo: return {"tickets": []}
        return {"reportes": []}
    with open(archivo, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            if "retrabajo" in archivo: return {"retrabajos": []}
            return {}

def escribir_json(archivo, data):
    with open(archivo, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)


@reportes_bp.route("/api/reportes/nuevo", methods=["POST"])
def nuevo_reporte():
    unidad_req = request.form.get("unidad")
    eco_full = f"8090-{unidad_req}"
    
    # 0. Check if the unit is inactive or in Juridicos
    unidades_data = leer_json("unidades.json")
    if unidad_req in unidades_data:
        if unidades_data[unidad_req].get("Juridicos") == True:
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra en Jurídicos y no puede ser reportada."})
        if unidades_data[unidad_req].get("Estado") == "Inactiva":
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} se encuentra Inhabilitada/Incosteable y no puede ser reportada."})

    
    # 1. Check facturas.json (tickets in taller not yet delivered/closed)
    facturas_data = leer_json("facturas.json")
    facturas_report_ids = set()
    for f in facturas_data.get("facturas", []):
        # Collect report IDs to know which reports have moved to facturas
        r_id = f.get("id_reporte") or f.get("numero_reporte")
        if not r_id:
            retro = f.get("retro", "")
            import re
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                r_id = match.group(1).strip()
        if r_id:
            facturas_report_ids.add(str(r_id))
            
        if f.get("unidad") == eco_full and f.get("entregado") != "Sí" and f.get("estado") not in ["Cancelado_Cotizacion_Cara", "Rechazado", "Eliminado"]:
            return jsonify({"status": "error", "message": f"La unidad {unidad_req} ya se encuentra en taller o activa."})

    # 2. Check reportes.json (active unassigned tickets)
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        if str(r.get("unidad")) == str(unidad_req) and r.get("estado") != "Eliminado":
            if str(r.get("id")) not in facturas_report_ids:
                return jsonify({"status": "error", "message": f"La unidad {unidad_req} ya tiene un reporte activo en proceso de asignación."})

    # 3. Validar que exista al menos un Administrador Y un Supervisor para ese COPE
    cope_reporte = request.form.get("cope", "No especificado")
    usuarios_data = leer_json("usuarios.json")
    
    hay_admin = False
    hay_super = False
    
    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "administracion":
            perfil = u.get("datos_perfil", {})
            subrol = perfil.get("subrol", "")
            cope_admin = perfil.get("cope", "")
            copes_extra = perfil.get("copes_asignados", [])
            
            if cope_admin == cope_reporte or cope_reporte in copes_extra:
                if subrol == "Administrador":
                    hay_admin = True
                elif subrol == "Supervisor":
                    hay_super = True
                
    if not hay_admin or not hay_super:
        if not hay_admin and not hay_super:
            msg = f"No se puede crear el reporte: Faltan un Administrador y un Supervisor registrados para el COPE {cope_reporte}."
        elif not hay_admin:
            msg = f"No se puede crear el reporte: Falta un Administrador registrado para el COPE {cope_reporte}."
        else:
            msg = f"No se puede crear el reporte: Falta un Supervisor registrado para el COPE {cope_reporte}."
            
        return jsonify({"status": "error", "message": msg})

    # 4. Validar que el correo electrónico sea obligatorio y tenga formato válido
    import re as re_email
    email_req = (request.form.get("email") or "").strip()
    if not email_req or email_req.lower() == "no proporcionado":
        return jsonify({"status": "error", "message": "El correo electrónico es obligatorio para generar el reporte."})
    email_pattern = re_email.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    if not email_pattern.match(email_req):
        return jsonify({"status": "error", "message": "El correo electrónico ingresado no tiene un formato válido (ej. usuario@correo.com)."})

    nuevo_id = f"REP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    reporte = {
        "id": nuevo_id,
        "fecha": request.form.get("fecha"),
        "kilometraje": request.form.get("kilometraje"),
        "unidad": request.form.get("unidad"),
        "marca": request.form.get("marca"),
        "modelo": request.form.get("modelo"),
        "ciudad": request.form.get("ciudad", "No especificada"),
        "cope": request.form.get("cope", "No especificado"),
        "celular": request.form.get("celular"),
        "empleado": request.form.get("empleado"),
        "email": request.form.get("email"),
        "departamento": request.form.get("departamento"),
        "mantenimiento": request.form.get("mantenimiento"),
        "falla": request.form.get("falla"),
        "firma_chofer": request.form.get("firma_chofer"),
        "estado": "Pendiente de Revisión",
        "asignado_a": "",
        "timestamp": datetime.datetime.now().isoformat(),
    }

    data = leer_json("reportes.json")
    data.setdefault("reportes", []).append(reporte)
    escribir_json("reportes.json", data)

    usuarios_data = leer_json("usuarios.json")
    admins_data = []
    
    # Solo notificar a los Supervisores del mismo COPE
    for u in usuarios_data.get("usuarios", []):
            if u.get("rol") == "administracion":
                subrol = u["datos_perfil"].get("subrol", "")
                cope_admin = u["datos_perfil"].get("cope", "")
                copes_extra = u["datos_perfil"].get("copes_asignados", [])
                
                # Solo enviar a Supervisores de ese COPE
                if subrol == "Supervisor" and (cope_admin == reporte["cope"] or reporte["cope"] in copes_extra):
                    correo = u["datos_perfil"].get("correo")
                    if correo:
                        nombre_completo = f"{u['datos_perfil'].get('nombres', '')} {u['datos_perfil'].get('apellido_paterno', '')}".strip()
                        admins_data.append({"correo": correo, "nombre": nombre_completo, "puesto": subrol})

    if admins_data:
        enviar_correo_nuevo_ticket(
            lista_admins=admins_data,
            ticket=nuevo_id,
            unidad=reporte["unidad"],
            ciudad=reporte["ciudad"],
            falla=reporte["falla"],
            empleado=reporte["empleado"],
        )

    correo_empleado = reporte.get("email")
    if correo_empleado and correo_empleado.strip() not in ["", "No proporcionado"]:
        enviar_correo_confirmacion_reporte(correo_destino=correo_empleado, nombre_empleado=reporte["empleado"], ticket=nuevo_id, unidad=reporte["unidad"], falla=reporte["falla"])

    return jsonify({"status": "success", "message": "Reporte registrado exitosamente.", "ticket": nuevo_id})


@reportes_bp.route("/api/reportes/lista", methods=["GET"])
def lista_reportes():
    if "usuario" not in session:
        return jsonify({"reportes": []})
        
    data = leer_json("reportes.json")
    
    # --- FILTRO GEOGRÁFICO PARA SUPERVISORES ---
    if session['usuario']['rol'] == 'administracion':
        subrol = session['usuario']['datos_perfil'].get('subrol', '')
        if subrol == 'Supervisor':
            usuario_id = session['usuario']['usuario']
            usuarios_data = leer_json("usuarios.json")
            
            mi_cope = ""
            copes_asignados = []
            for u in usuarios_data.get("usuarios", []):
                if u.get("usuario") == usuario_id:
                    mi_cope = u.get("datos_perfil", {}).get("cope", "")
                    copes_asignados = u.get("datos_perfil", {}).get("copes_asignados", [])
                    break
                    
            copes_permitidos = [mi_cope] + copes_asignados
            # Solo dejamos los reportes que coincidan con el COPE (o COPEs extra) del Supervisor
            data['reportes'] = [r for r in data.get('reportes', []) if r.get('cope') in copes_permitidos]
            
    return jsonify(data)


@reportes_bp.route("/api/reportes/asignar", methods=["POST"])
def asignar_reporte():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})

    req_data = request.json
    reporte_id = req_data.get("id")
    proveedor = req_data.get("proveedor")
    compania = req_data.get("compania", "RUMN")

    correo_proveedor = ""
    nombre_proveedor = proveedor
    usuarios_data = leer_json("usuarios.json")
    for u in usuarios_data.get("usuarios", []):
        if u["rol"] == "proveedores" and u["datos_perfil"].get("nombre_proveedor") == proveedor:
            correo_proveedor = u["datos_perfil"].get("correo", "")
            break

    data = leer_json("reportes.json")
    for r in data.get("reportes", []):
        if str(r["id"]) == str(reporte_id):
            r["asignado_a"] = proveedor
            r["estado"] = f"Asignado a: {proveedor}"
            r["compania"] = compania
            
            escribir_json("reportes.json", data)
            nombre_supervisor_actor = None
            if "usuario" in session:
                dp_act = session["usuario"].get("datos_perfil", {})
                nombre_supervisor_actor = f"{dp_act.get('nombres', '')} {dp_act.get('apellido_paterno', '')}".strip() or session["usuario"].get("usuario")
            enviar_correo_nueva_orden(
                correo_proveedor,
                nombre_proveedor,
                reporte_id,
                r.get("unidad", ""),
                r.get("falla", ""),
                nombre_supervisor=nombre_supervisor_actor
            )
            return jsonify({"status": "success", "message": f"Reporte asignado exitosamente al taller {proveedor}."})

    return jsonify({"status": "error", "message": f"Reporte no encontrado. DEBUG ID req: {reporte_id}, Type: {type(reporte_id)}, req_data: {req_data}"})


@reportes_bp.route("/api/reportes/eliminar", methods=["POST"])
def eliminar_reporte():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})

    req_data = request.json
    reporte_id = req_data.get("id")
    motivo = req_data.get("motivo", "Motivo no especificado por la administración.") 

    data = leer_json("reportes.json")
    nuevos_reportes = []
    eliminado = False
    reporte_a_eliminar = None 

    for r in data.get("reportes", []):
        if r["id"] == reporte_id:
            eliminado = True
            reporte_a_eliminar = r 
        else:
            nuevos_reportes.append(r)

    if eliminado and reporte_a_eliminar:
        data["reportes"] = nuevos_reportes
        escribir_json("reportes.json", data)
        
        correo_chofer = reporte_a_eliminar.get('email')
        if correo_chofer and correo_chofer.strip() not in ["", "No proporcionado"]:
            nombre_admin_actor = None
            if "usuario" in session:
                dp_act = session["usuario"].get("datos_perfil", {})
                nombre_admin_actor = f"{dp_act.get('nombres', '')} {dp_act.get('apellido_paterno', '')}".strip() or session["usuario"].get("usuario")
            enviar_correo_ticket_rechazado(
                correo_chofer,
                reporte_a_eliminar.get('empleado', 'Operador'),
                reporte_a_eliminar.get('id'),
                reporte_a_eliminar.get('unidad'),
                motivo,
                nombre_admin=nombre_admin_actor
            )
        
        return jsonify({"status": "success", "message": "Reporte eliminado y usuario notificado."})


@reportes_bp.route("/api/unidades", methods=["GET"])
def obtener_unidades():
    from rutas_unidades_metricas import obtener_metricas_flota
    flota = obtener_metricas_flota()
    data = flota["unidades_data"]
    estados = flota["estados_por_unidad"]

    # Inject flags to know the exact operational status
    for num, info in data.items():
        est = estados.get(num, "En Circulación")
        info["estado_operativo"] = est
        info["activa_en_taller"] = (est == "En Taller")
        info["inhabilitada_caras"] = (est == "Inhabilitada")

    return jsonify(data)

@reportes_bp.route("/api/unidades/metricas", methods=["GET"])
def obtener_unidades_metricas():
    from rutas_unidades_metricas import obtener_metricas_flota
    return jsonify({
        "status": "success",
        **obtener_metricas_flota()
    })

def is_unidad_active(numero_unidad):
    if not numero_unidad or len(str(numero_unidad)) < 4:
        return False
        
    eco_4 = str(numero_unidad)[-4:]
    eco_full = f"8090-{eco_4}"
    
    facturas_data = leer_json("facturas.json")
    facturas_report_ids = set()
    for f in facturas_data.get("facturas", []):
        r_id = f.get("id_reporte") or f.get("numero_reporte")
        if not r_id:
            retro = f.get("retro", "")
            import re
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                r_id = match.group(1).strip()
        if r_id:
            facturas_report_ids.add(str(r_id))
            
        if f.get("unidad") == eco_full and f.get("entregado") != "Sí" and f.get("estado") not in ["Cancelado_Cotizacion_Cara", "Rechazado", "Eliminado"]:
            return True

    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        if str(r.get("unidad")) == eco_4 and r.get("estado") != "Eliminado":
            if str(r.get("id")) not in facturas_report_ids:
                return True
                
    return False

@reportes_bp.route("/api/unidades/guardar", methods=["POST"])
def guardar_unidad():
    import json
    import os
    try:
        numero = request.form.get('numero', '').strip()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        modo = request.form.get('modo', 'agregar')
        old_numero = request.form.get('old_numero', '').strip()
        
        if not numero:
            return jsonify({'status': 'error', 'message': 'El número económico es requerido.'})
            
        # Validar si la unidad esta activa
        if modo == 'editar' and is_unidad_active(old_numero or numero):
            return jsonify({'status': 'error', 'message': 'No puedes modificar esta unidad porque actualmente tiene un ticket activo en el taller o en asignación.'})
            
        archivo = "unidades.json"
        data = {}
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        if modo == 'agregar' and numero in data:
            return jsonify({'status': 'error', 'message': 'Esta unidad ya existe.'})
            
        if modo == 'editar' and old_numero and old_numero != numero:
            if numero in data:
                return jsonify({'status': 'error', 'message': 'El nuevo número de unidad ya está registrado.'})
            if old_numero in data:
                del data[old_numero]
                
        data[numero] = {
            "Marca": marca,
            "Modelo": modelo
        }
        
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@reportes_bp.route("/api/unidades/eliminar", methods=["POST"])
def eliminar_unidad():
    import json
    import os
    try:
        numero = request.form.get('numero', '').strip()
        archivo = "unidades.json"
        
        if not os.path.exists(archivo):
            return jsonify({'status': 'error', 'message': 'Archivo no encontrado.'})
            
        if is_unidad_active(numero):
            return jsonify({'status': 'error', 'message': 'No puedes eliminar esta unidad porque actualmente tiene un ticket activo en el taller o en asignación.'})
            
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if numero in data:
            del data[numero]
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Unidad no encontrada.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@reportes_bp.route("/api/reportes/eliminar_silencioso", methods=["POST"])
def eliminar_reporte_silencioso():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})

    reporte_id = request.json.get("id")
    data = leer_json("reportes.json")
    nuevos_reportes = []
    eliminado = False
    
    for r in data.get("reportes", []):
        if r["id"] == reporte_id:
            eliminado = True
        else:
            nuevos_reportes.append(r)

    if eliminado:
        data["reportes"] = nuevos_reportes
        escribir_json("reportes.json", data)
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error", "message": "Reporte no encontrado"})

@reportes_bp.route("/api/unidades/toggle_estado", methods=["POST"])
def toggle_estado_unidad():
    numero = request.form.get("numero")
    
    if not numero:
        return jsonify({"status": "error", "message": "Falta el numero de la unidad"})
        
    if is_unidad_active(numero):
        return jsonify({"status": "error", "message": "No puedes desactivar/modificar esta unidad porque actualmente tiene un ticket activo en el taller o en asignación."})
        
    try:
        data = leer_json("unidades.json")
        if not data:
            data = {}
            
        if numero in data:
            current = data[numero].get("Estado", "Activa")
            data[numero]["Estado"] = "Inactiva" if current == "Activa" else "Activa"
            escribir_json("unidades.json", data)
            return jsonify({"status": "success", "message": f"Estado cambiado a {data[numero]['Estado']}"})
        else:
            return jsonify({"status": "error", "message": "Unidad no encontrada"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@reportes_bp.route("/api/unidades/toggle_juridicos", methods=["POST"])
def toggle_juridicos_unidad():
    numero = request.form.get("numero")
    
    if not numero:
        return jsonify({"status": "error", "message": "Falta el numero de la unidad"})
        
    if is_unidad_active(numero):
        return jsonify({"status": "error", "message": "No puedes mandar a Jurídicos esta unidad porque actualmente tiene un ticket activo en el taller o en asignación."})
        
    try:
        data = leer_json("unidades.json")
        if not data:
            data = {}
            
        if numero in data:
            current = data[numero].get("Juridicos", False)
            data[numero]["Juridicos"] = not current
            escribir_json("unidades.json", data)
            return jsonify({"status": "success", "message": f"Estado Juridicos cambiado a {data[numero]['Juridicos']}"})
        else:
            return jsonify({"status": "error", "message": "Unidad no encontrada"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def obtener_fecha_entrega(factura):
    fecha_str = factura.get("fecha_entrega") or factura.get("fecha")
    if not fecha_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(fecha_str.split("T")[0] if "T" in fecha_str else fecha_str, fmt)
        except ValueError:
            pass
    try:
        part = fecha_str.split(" ")[0].split("T")[0]
        return datetime.datetime.strptime(part, "%Y-%m-%d")
    except Exception:
        return None


def formatear_duracion_segundos(segundos_totales):
    segundos_totales = int(max(0, segundos_totales))
    dias = segundos_totales // 86400
    resto = segundos_totales % 86400
    horas = resto // 3600
    resto = resto % 3600
    minutos = resto // 60
    segundos = resto % 60
    
    partes = []
    if dias > 0:
        partes.append(f"{dias} día{'s' if dias != 1 else ''}")
    if horas > 0:
        partes.append(f"{horas} hr{'s' if horas != 1 else ''}")
    if minutos > 0:
        partes.append(f"{minutos} min")
    if segundos > 0 or not partes:
        partes.append(f"{segundos} seg")
    return ", ".join(partes)


def formatear_duracion_corta(segundos_totales):
    segundos_totales = int(max(0, segundos_totales))
    dias = segundos_totales // 86400
    resto = segundos_totales % 86400
    horas = resto // 3600
    resto = resto % 3600
    minutos = resto // 60
    segundos = resto % 60
    
    partes = []
    if dias > 0: partes.append(f"{dias}d")
    if horas > 0: partes.append(f"{horas}h")
    if minutos > 0: partes.append(f"{minutos}m")
    if segundos > 0 or not partes: partes.append(f"{segundos}s")
    return " ".join(partes)


def verificar_vigencia_garantia(factura_correspondiente):
    nombre_taller = factura_correspondiente.get("proveedor", "Taller")
    usuarios_data = leer_json("usuarios.json")
    
    dias_gar = 30
    horas_gar = 0
    mins_gar = 0
    segs_gar = 0
    
    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "proveedores":
            dp = u.get("datos_perfil", {})
            p_nom = str(dp.get("nombre_proveedor", "")).strip().upper()
            u_nom = str(u.get("usuario", "")).strip().upper()
            if p_nom == str(nombre_taller).strip().upper() or u_nom == str(nombre_taller).strip().upper():
                try:
                    dias_gar = int(dp.get("dias_garantia", 30))
                except:
                    dias_gar = 30
                try:
                    horas_gar = int(dp.get("horas_garantia", 0))
                except:
                    horas_gar = 0
                try:
                    mins_gar = int(dp.get("minutos_garantia", 0))
                except:
                    mins_gar = 0
                try:
                    segs_gar = int(dp.get("segundos_garantia", 0))
                except:
                    segs_gar = 0
                break

    total_segundos_garantia = dias_gar * 86400 + horas_gar * 3600 + mins_gar * 60 + segs_gar
    if total_segundos_garantia <= 0:
        total_segundos_garantia = 30 * 86400

    dt_entrega = obtener_fecha_entrega(factura_correspondiente)
    if not dt_entrega:
        txt_def = formatear_duracion_segundos(total_segundos_garantia)
        return True, 0, total_segundos_garantia, total_segundos_garantia, "Fecha no registrada", nombre_taller, "0 seg", txt_def, txt_def

    ahora = datetime.datetime.now()
    segundos_transcurridos = (ahora - dt_entrega).total_seconds()
    if segundos_transcurridos < 0:
        segundos_transcurridos = 0

    vigente = segundos_transcurridos <= total_segundos_garantia
    segundos_restantes = max(0, total_segundos_garantia - segundos_transcurridos)
    fecha_entrega_formateada = dt_entrega.strftime("%Y-%m-%d %H:%M:%S")

    txt_limite = formatear_duracion_segundos(total_segundos_garantia)
    txt_transcurrido = formatear_duracion_segundos(segundos_transcurridos)
    txt_restante = formatear_duracion_segundos(segundos_restantes)

    return vigente, segundos_transcurridos, total_segundos_garantia, segundos_restantes, fecha_entrega_formateada, nombre_taller, txt_transcurrido, txt_limite, txt_restante


@reportes_bp.route("/api/garantia/buscar_ticket/<path:ticket_query>", methods=["GET"])
def buscar_ticket_garantia(ticket_query):
    query = str(ticket_query).strip()
    if not query:
        return jsonify({"status": "error", "message": "Por favor ingrese un número de ticket válido."})
    
    # 1. Buscar en reportes.json
    reportes_data = leer_json("reportes.json")
    reporte_encontrado = None
    
    clean_q = query.upper().replace("REP-", "").replace("REP", "").strip()
    
    for r in reportes_data.get("reportes", []):
        r_id = str(r.get("id", "")).strip()
        r_clean = r_id.upper().replace("REP-", "").replace("REP", "").strip()
        
        # Coincidencia exacta o numérica limpia
        if r_id.upper() == query.upper() or (clean_q and clean_q == r_clean):
            reporte_encontrado = r
            break
            
    # 2. Si no se encontró directo en reportes, buscar en facturas.json por id de factura o [TICKET:REP-xxx]
    if not reporte_encontrado:
        facturas_data = leer_json("facturas.json")
        for f in facturas_data.get("facturas", []):
            f_id = str(f.get("id", "")).strip()
            f_clean = f_id.upper().replace("REP-", "").replace("REP", "").strip()
            
            match_factura = (f_id.upper() == query.upper() or (clean_q and clean_q == f_clean))
            
            retro = f.get("retro", "")
            import re
            m = re.search(r"\[TICKET:(.*?)\]", retro)
            ref_rep_id = m.group(1).strip() if m else ""
            ref_clean = ref_rep_id.upper().replace("REP-", "").replace("REP", "").strip()
            
            match_retro = (ref_rep_id and (ref_rep_id.upper() == query.upper() or (clean_q and clean_q == ref_clean)))
            
            if match_factura or match_retro:
                target_id = ref_rep_id if ref_rep_id else f_id
                for r in reportes_data.get("reportes", []):
                    if str(r.get("id", "")).strip().upper() == target_id.upper():
                        reporte_encontrado = r
                        break
                
                if not reporte_encontrado:
                    u_eco = str(f.get("unidad", "")).replace("8090-", "").strip()
                    reporte_encontrado = {
                        "id": ref_rep_id or f.get("id"),
                        "fecha": f.get("fecha", ""),
                        "unidad": u_eco,
                        "marca": f.get("marca", ""),
                        "modelo": f.get("modelo", ""),
                        "ciudad": f.get("ciudad", ""),
                        "cope": f.get("cope", ""),
                        "empleado": f.get("responsable", ""),
                        "celular": f.get("telefono", ""),
                        "email": f.get("email", ""),
                        "kilometraje": f.get("kilometraje", ""),
                        "mantenimiento": f.get("mantenimiento", "Correctivo"),
                        "falla": f.get("retro", "") or f.get("diagnostico", "") or f.get("titulo", ""),
                        "asignado_a": f.get("proveedor", "")
                    }
                break

    # 3. Buscar en tickets_archivados.json por si acaso
    if not reporte_encontrado:
        arch_data = leer_json("tickets_archivados.json")
        for a in arch_data.get("tickets", []):
            a_id = str(a.get("id", "")).strip()
            a_clean = a_id.upper().replace("REP-", "").replace("REP", "").strip()
            if a_id.upper() == query.upper() or (clean_q and clean_q == a_clean):
                reporte_encontrado = a
                break

    if not reporte_encontrado:
        return jsonify({
            "status": "not_found",
            "message": f"No se encontró ningún reporte o ticket con el número '{query}'. Verifique el identificador e intente de nuevo."
        })

    # 4. REGLA ESTRICTA: Solo se puede mandar a retrabajo una unidad cuando el chofer ya haya verificado su número de confirmación (salida de taller)
    facturas_data = leer_json("facturas.json")
    todas_facturas = facturas_data.get("facturas", [])
    if os.path.exists("tickets_archivados.json"):
        todas_facturas += leer_json("tickets_archivados.json").get("facturas", [])

    factura_correspondiente = None
    rep_id_target = str(reporte_encontrado.get("id", query)).strip().upper()
    rep_id_clean = rep_id_target.replace("REP-", "").replace("REP", "").strip()

    import re
    for f in todas_facturas:
        f_id = str(f.get("id", "")).strip().upper()
        f_id_clean = f_id.replace("REP-", "").replace("REP", "").strip()
        f_rep = str(f.get("id_reporte", "") or f.get("numero_reporte", "")).strip().upper()
        retro = str(f.get("retro", ""))
        m = re.search(r"\[TICKET:(.*?)\]", retro)
        m_ticket = m.group(1).strip().upper() if m else ""

        if f_id == rep_id_target or f_rep == rep_id_target or m_ticket == rep_id_target or (f_id_clean and f_id_clean == rep_id_clean):
            factura_correspondiente = f
            break

    if not factura_correspondiente:
        return jsonify({
            "status": "no_elegible",
            "message": "Este ticket no puede ser enviado a retrabajo porque aún no ha sido atendido ni procesado en taller."
        })

    entregado_val = str(factura_correspondiente.get("entregado", "")).strip().lower()
    if not (entregado_val in ["sí", "si", "s"] or entregado_val.startswith("s")):
        return jsonify({
            "status": "no_elegible",
            "message": "Solo se puede mandar a retrabajo una unidad cuando el chofer ya haya verificado su número de confirmación para cuando el taller en teoría la dejó arreglada y lista."
        })

    # Validación de vigencia de tiempo de garantía del taller
    vigente, segs_trans, segs_tot, segs_rest, f_entrega, n_taller, txt_trans, txt_lim, txt_rest = verificar_vigencia_garantia(factura_correspondiente)
    if not vigente:
        return jsonify({
            "status": "garantia_expirada",
            "message": f"El tiempo de garantía ya pasó para este ticket. El taller '{n_taller}' ofrece un límite de {txt_lim} de garantía y han transcurrido {txt_trans} desde la entrega ({f_entrega}). Ya no es posible aplicar garantía para este servicio.",
            "limite_tiempo": txt_lim,
            "tiempo_transcurrido": txt_trans,
            "tiempo_restante": "0 seg",
            "segundos_transcurridos": int(segs_trans),
            "total_segundos_limite": int(segs_tot),
            "fecha_entrega": f_entrega,
            "taller": n_taller
        })

    # Verificar si ya tiene retrabajo pendiente en proceso
    retrabajos_data = leer_json("retrabajos.json")
    for ret in retrabajos_data.get("retrabajos", []):
        if str(ret.get("ticket_original", "")).strip().upper() == rep_id_target and ret.get("estado") == "Pendiente":
            return jsonify({
                "status": "ya_en_retrabajo",
                "message": "Este ticket ya cuenta con una solicitud de garantía/retrabajo pendiente en revisión con el supervisor."
            })

    eco = str(reporte_encontrado.get("unidad", "")).replace("8090-", "").strip()
    
    # Fallback para marca y modelo desde unidades.json si vienen vacíos o N/A
    unidades_data = leer_json("unidades.json")
    u_info = unidades_data.get(f"8090{eco}", {}) or unidades_data.get(eco, {})
    marca_val = reporte_encontrado.get("marca") or u_info.get("Marca") or "N/A"
    modelo_val = reporte_encontrado.get("modelo") or u_info.get("Modelo") or "N/A"
    
    ts = str(reporte_encontrado.get("timestamp", ""))
    hora_val = ""
    if "T" in ts:
        try:
            hora_val = ts.split("T")[1].split(".")[0]
        except Exception:
            hora_val = ""
            
    datos_reporte = {
        "id": reporte_encontrado.get("id", query),
        "fecha": reporte_encontrado.get("fecha", "No especificada"),
        "hora": hora_val,
        "timestamp": reporte_encontrado.get("timestamp", ""),
        "unidad": eco,
        "marca": marca_val,
        "modelo": modelo_val,
        "kilometraje": reporte_encontrado.get("kilometraje", "No registrado"),
        "empleado": reporte_encontrado.get("empleado") or reporte_encontrado.get("responsable") or "No registrado",
        "celular": reporte_encontrado.get("celular") or reporte_encontrado.get("telefono") or "No registrado",
        "email": reporte_encontrado.get("email", "No registrado"),
        "departamento": reporte_encontrado.get("departamento", "No especificado"),
        "ciudad": reporte_encontrado.get("ciudad") or factura_correspondiente.get("ciudad", "No especificada"),
        "cope": reporte_encontrado.get("cope") or factura_correspondiente.get("cope", "No especificado"),
        "compania": reporte_encontrado.get("compania") or factura_correspondiente.get("compania", "Telnor"),
        "mantenimiento": reporte_encontrado.get("mantenimiento", "Correctivo"),
        "falla": reporte_encontrado.get("falla") or reporte_encontrado.get("retro") or "Falla mecánica reportada",
        "firma_chofer": reporte_encontrado.get("firma_chofer", ""),
        "estado": reporte_encontrado.get("estado", "Pendiente"),
        "asignado_a": factura_correspondiente.get("proveedor") or reporte_encontrado.get("asignado_a", ""),
        "garantia_limite": txt_lim,
        "garantia_transcurrido": txt_trans,
        "garantia_restante": txt_rest
    }

    return jsonify({
        "status": "success",
        "encontrado": True,
        "reporte": datos_reporte
    })


@reportes_bp.route("/api/garantia/aplicar", methods=["POST"])
def aplicar_garantia():
    req = request.get_json() or {}
    ticket_id = str(req.get("ticket_id", "")).strip()
    motivo = str(req.get("motivo", "")).strip()
    import re
    motivo = re.sub(r'^["\'«»“”„]+|["\'«»“”„]+$', '', motivo).strip()

    if not ticket_id:
        return jsonify({"status": "error", "message": "Número de ticket no proporcionado."}), 400
    if not motivo:
        return jsonify({"status": "error", "message": "Por favor escribe el motivo del retrabajo detallando la falla no resuelta o reincidencia."}), 400

    reportes_data = leer_json("reportes.json")
    reporte_encontrado = None
    clean_q = ticket_id.upper().replace("REP-", "").replace("REP", "").strip()

    for r in reportes_data.get("reportes", []):
        r_id = str(r.get("id", "")).strip()
        r_clean = r_id.upper().replace("REP-", "").replace("REP", "").strip()
        if r_id.upper() == ticket_id.upper() or (clean_q and clean_q == r_clean):
            reporte_encontrado = r
            break

    facturas_data = leer_json("facturas.json")
    todas_facturas = facturas_data.get("facturas", [])
    if os.path.exists("tickets_archivados.json"):
        todas_facturas += leer_json("tickets_archivados.json").get("facturas", [])

    factura_correspondiente = None
    import re
    target_id_str = (reporte_encontrado.get("id") if reporte_encontrado else ticket_id).strip().upper()
    target_clean = target_id_str.replace("REP-", "").replace("REP", "").strip()

    for f in todas_facturas:
        f_id = str(f.get("id", "")).strip().upper()
        f_id_clean = f_id.replace("REP-", "").replace("REP", "").strip()
        f_rep = str(f.get("id_reporte", "") or f.get("numero_reporte", "")).strip().upper()
        retro = str(f.get("retro", ""))
        m = re.search(r"\[TICKET:(.*?)\]", retro)
        m_ticket = m.group(1).strip().upper() if m else ""

        if f_id == target_id_str or f_rep == target_id_str or m_ticket == target_id_str or (f_id_clean and f_id_clean == target_clean):
            factura_correspondiente = f
            break

    if not reporte_encontrado and factura_correspondiente:
        u_eco = str(factura_correspondiente.get("unidad", "")).replace("8090-", "").strip()
        reporte_encontrado = {
            "id": ticket_id,
            "fecha": factura_correspondiente.get("fecha", ""),
            "unidad": u_eco,
            "marca": factura_correspondiente.get("marca", ""),
            "modelo": factura_correspondiente.get("modelo", ""),
            "ciudad": factura_correspondiente.get("ciudad", ""),
            "cope": factura_correspondiente.get("cope", ""),
            "empleado": factura_correspondiente.get("responsable", ""),
            "celular": factura_correspondiente.get("telefono", ""),
            "email": factura_correspondiente.get("email", ""),
            "kilometraje": factura_correspondiente.get("kilometraje", ""),
            "mantenimiento": factura_correspondiente.get("mantenimiento", "Correctivo"),
            "falla": factura_correspondiente.get("retro", "") or factura_correspondiente.get("diagnostico", ""),
            "asignado_a": factura_correspondiente.get("proveedor", "")
        }

    if not reporte_encontrado or not factura_correspondiente:
        return jsonify({"status": "error", "message": "No se encontraron los registros de servicio correspondientes para este ticket."}), 404

    # Validación estricta del número de confirmación
    entregado_val = str(factura_correspondiente.get("entregado", "")).strip().lower()
    if not (entregado_val in ["sí", "si", "s"] or entregado_val.startswith("s")):
        return jsonify({
            "status": "error",
            "message": "Solo se puede mandar a retrabajo una unidad cuando el chofer ya haya verificado su número de confirmación para cuando el taller en teoría la dejó arreglada y lista."
        }), 400

    # Validación de vigencia de tiempo de garantía del taller
    vigente_ap, segs_trans_ap, segs_tot_ap, segs_rest_ap, f_entrega_ap, n_taller_ap, txt_trans_ap, txt_lim_ap, txt_rest_ap = verificar_vigencia_garantia(factura_correspondiente)
    if not vigente_ap:
        return jsonify({
            "status": "error",
            "message": f"El tiempo de garantía ya pasó para este ticket. El taller '{n_taller_ap}' tiene un límite de {txt_lim_ap} de garantía y han transcurrido {txt_trans_ap} desde la entrega ({f_entrega_ap})."
        }), 400

    eco = str(reporte_encontrado.get("unidad", "")).replace("8090-", "").strip()
    unidades_data = leer_json("unidades.json")
    u_info = unidades_data.get(f"8090{eco}", {}) or unidades_data.get(eco, {})
    marca_val = reporte_encontrado.get("marca") or u_info.get("Marca") or "N/A"
    modelo_val = reporte_encontrado.get("modelo") or u_info.get("Modelo") or "N/A"

    cope_val = reporte_encontrado.get("cope") or factura_correspondiente.get("cope") or "No especificado"
    ciudad_val = reporte_encontrado.get("ciudad") or factura_correspondiente.get("ciudad") or "No especificada"

    # 1. SECCIÓN 1: REPORTE DE INCIDENCIA (ORIGEN)
    seccion_1 = {
        "ticket": reporte_encontrado.get("id", ticket_id),
        "fecha": reporte_encontrado.get("fecha", ""),
        "hora": reporte_encontrado.get("hora", "") or (reporte_encontrado.get("timestamp", "").split("T")[1].split(".")[0] if "T" in str(reporte_encontrado.get("timestamp", "")) else ""),
        "timestamp": reporte_encontrado.get("timestamp", ""),
        "unidad": eco,
        "marca": marca_val,
        "modelo": modelo_val,
        "kilometraje": reporte_encontrado.get("kilometraje", "No registrado"),
        "compania": reporte_encontrado.get("compania") or factura_correspondiente.get("compania") or "Telnor",
        "mantenimiento": reporte_encontrado.get("mantenimiento", "Correctivo"),
        "ciudad": ciudad_val,
        "cope": cope_val,
        "empleado": reporte_encontrado.get("empleado") or reporte_encontrado.get("responsable") or "No registrado",
        "celular": reporte_encontrado.get("celular") or reporte_encontrado.get("telefono") or "No registrado",
        "email": reporte_encontrado.get("email", "No registrado"),
        "departamento": reporte_encontrado.get("departamento", "No especificado"),
        "falla_original": reporte_encontrado.get("falla") or reporte_encontrado.get("retro") or "Falla mecánica",
        "firma_chofer": reporte_encontrado.get("firma_chofer", "")
    }

    # 2. SECCIÓN 2: DIAGNÓSTICO Y COTIZACIÓN (TALLER)
    cots_raw = factura_correspondiente.get("cotizaciones", [])
    cotizaciones_sec2 = []
    for c in cots_raw:
        cotizaciones_sec2.append({
            "id_cotizacion": c.get("id_cotizacion"),
            "titulo": c.get("titulo", "Sin Título"),
            "mantenimiento": c.get("mantenimiento", "Correctivo"),
            "precio": c.get("precio", 0.0),
            "retro": c.get("retro", ""),
            "diagnostico": c.get("diagnostico", ""),
            "trabajo_realizar": c.get("trabajo_realizar", ""),
            "pdf_cotizacion": c.get("pdf_cotizacion"),
            "fotos_evidencia": c.get("fotos_evidencia", [])
        })

    seccion_2 = {
        "proveedor": factura_correspondiente.get("proveedor", "Taller No Asignado"),
        "responsable": factura_correspondiente.get("responsable", "No registrado"),
        "fecha_ingreso": factura_correspondiente.get("fecha", ""),
        "precio_total": factura_correspondiente.get("precio", 0.0),
        "titulo": factura_correspondiente.get("titulo", ""),
        "retro": factura_correspondiente.get("retro", ""),
        "diagnostico": factura_correspondiente.get("diagnostico", ""),
        "trabajo_realizar": factura_correspondiente.get("trabajo_realizar", ""),
        "cotizaciones": cotizaciones_sec2 if cotizaciones_sec2 else [{
            "titulo": factura_correspondiente.get("titulo", "Global"),
            "mantenimiento": factura_correspondiente.get("mantenimiento", "Correctivo"),
            "precio": factura_correspondiente.get("precio", 0.0),
            "retro": factura_correspondiente.get("retro", ""),
            "diagnostico": factura_correspondiente.get("diagnostico", ""),
            "trabajo_realizar": factura_correspondiente.get("trabajo_realizar", ""),
            "pdf_cotizacion": (factura_correspondiente.get("fotos_cotizacion") or [None])[0],
            "fotos_evidencia": factura_correspondiente.get("fotos_evidencia", [])
        }],
        "fotos_evidencia": factura_correspondiente.get("fotos_evidencia", [])
    }

    # 3. IDENTIFICAR AL SUPERVISOR ASIGNADO A ESE COPE / EDIFICIO
    sup_usuario = ""
    sup_nombre = "Supervisor Asignado"
    sup_correo = ""

    usuarios_data = leer_json("usuarios.json")
    cope_target_norm = str(cope_val).strip().upper()

    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "administracion":
            dp = u.get("datos_perfil", {})
            if dp.get("subrol") == "Supervisor":
                cope_prin = str(dp.get("cope", "")).strip().upper()
                copes_asig = [str(c).strip().upper() for c in dp.get("copes_asignados", [])]
                if cope_target_norm == cope_prin or cope_target_norm in copes_asig:
                    sup_usuario = u.get("usuario", "")
                    nomb = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
                    if nomb: sup_nombre = nomb
                    sup_correo = dp.get("correo", "")
                    break

    if not sup_usuario:
        for u in usuarios_data.get("usuarios", []):
            if u.get("rol") == "administracion" and u.get("datos_perfil", {}).get("subrol") == "Supervisor":
                sup_usuario = u.get("usuario", "")
                dp = u.get("datos_perfil", {})
                sup_nombre = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
                sup_correo = dp.get("correo", "")
                break

    # 4. CREAR EL REGISTRO DE RETRABAJO (Mantiene el mismo número de ticket original)
    ticket_original_val = reporte_encontrado.get("id", ticket_id)

    # Determinar fecha de salida del taller de la cual sale el retrabajo
    fecha_salida_val = ""
    if factura_correspondiente.get("fecha_cierre"):
        fecha_salida_val = str(factura_correspondiente["fecha_cierre"]).split(" ")[0]
    elif factura_correspondiente.get("fecha_salida"):
        fecha_salida_val = str(factura_correspondiente["fecha_salida"]).split(" ")[0]
    elif factura_correspondiente.get("fecha"):
        fecha_salida_val = str(factura_correspondiente["fecha"]).split(" ")[0]

    nuevo_retrabajo = {
        "id": ticket_original_val,
        "ticket": ticket_original_val,
        "ticket_original": ticket_original_val,
        "factura_id": factura_correspondiente.get("id"),
        "unidad": eco,
        "cope": cope_val,
        "ciudad": ciudad_val,
        "fecha_solicitud": datetime.datetime.now().strftime("%Y-%m-%d"),
        "hora_solicitud": datetime.datetime.now().strftime("%H:%M:%S"),
        "fecha_salida": fecha_salida_val,
        "fecha_salida_taller": fecha_salida_val,
        "timestamp": datetime.datetime.now().isoformat(),
        "motivo_chofer": motivo,
        "supervisor_asignado": sup_nombre,
        "supervisor_usuario": sup_usuario,
        "supervisor_correo": sup_correo,
        "estado": "Pendiente",
        "seccion_1": seccion_1,
        "seccion_2": seccion_2
    }

    retrabajos_data = leer_json("retrabajos.json")
    if "retrabajos" not in retrabajos_data:
        retrabajos_data["retrabajos"] = []
    retrabajos_data["retrabajos"].append(nuevo_retrabajo)
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar factura en facturas.json
    for f in facturas_data.get("facturas", []):
        if str(f.get("id")) == str(factura_correspondiente.get("id")):
            f["retrabajo"] = "Pendiente"
            f["estado_retrabajo"] = "Pendiente"
            if "estado_previo" not in f or not f["estado_previo"]:
                f["estado_previo"] = f.get("estado")
            f["estado"] = "En Asignacion/Retrabajo"
            f["ultimo_motivo_retrabajo"] = motivo
            # NOTA: NO se incrementa num_retrabajo aquí porque apenas se va a reasignar o cancelar
            break
    escribir_json("facturas.json", facturas_data)

    # Actualizar en reportes.json
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        if str(r.get("id")) == str(ticket_original_val):
            if "estado_previo" not in r or not r["estado_previo"]:
                r["estado_previo"] = r.get("estado")
            r["estado"] = "En Asignacion/Retrabajo"
            break
    escribir_json("reportes.json", reportes_data)

    return jsonify({
        "status": "success",
        "message": f"Garantía aplicada con éxito para el ticket {ticket_original_val} y se canalizó al supervisor ({sup_nombre}) para el COPE {cope_val}.",
        "ticket": ticket_original_val
    })


@reportes_bp.route("/api/garantia/supervisor/lista", methods=["GET"])
def obtener_retrabajos_supervisor():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    usuario_sesion = session["usuario"]
    dp = usuario_sesion.get("datos_perfil", {})
    subrol = dp.get("subrol", "")
    mi_cope = str(dp.get("cope", "")).strip().upper()
    copes_extra = [str(c).strip().upper() for c in dp.get("copes_asignados", [])]
    copes_permitidos = set([mi_cope] + copes_extra)

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    facturas_data_cache = None
    for ret in todos:
        if not ret.get("fecha_salida_taller") and not ret.get("fecha_salida"):
            if facturas_data_cache is None:
                facturas_data_cache = leer_json("facturas.json").get("facturas", [])
            f_id = str(ret.get("factura_id", "")).strip().upper()
            t_orig = str(ret.get("ticket_original", "") or ret.get("id", "")).strip().upper()
            for f in facturas_data_cache:
                f_cur_id = str(f.get("id", "")).strip().upper()
                f_retro = str(f.get("retro", "")).upper()
                f_rep = str(f.get("id_reporte", "")).strip().upper()
                if (f_id and f_cur_id == f_id) or (t_orig and (t_orig in f_retro or f_rep == t_orig)):
                    f_sal = (str(f.get("fecha_cierre", "")).split(" ")[0] or str(f.get("fecha_salida", "")).split(" ")[0])
                    if f_sal:
                        ret["fecha_salida"] = f_sal
                        ret["fecha_salida_taller"] = f_sal
                    break

    filtrados = []
    for ret in todos:
        ret_cope = str(ret.get("cope", "")).strip().upper()
        if subrol in ["Jefatura", "Administrador"]:
            filtrados.append(ret)
        elif ret_cope in copes_permitidos or not ret_cope:
            filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })


@reportes_bp.route("/api/garantia/retrabajo/<ticket_id>", methods=["GET"])
def obtener_detalle_retrabajo(ticket_id):
    retrabajos_data = leer_json("retrabajos.json")
    t_clean = str(ticket_id).strip().upper()
    for ret in retrabajos_data.get("retrabajos", []):
        r_id = str(ret.get("id", "")).strip().upper()
        r_orig = str(ret.get("ticket_original", "")).strip().upper()
        r_tick = str(ret.get("ticket", "")).strip().upper()
        if t_clean in [r_id, r_orig, r_tick] or (t_clean and t_clean.replace("REP-", "") in [r_id.replace("REP-", ""), r_orig.replace("REP-", "")]):
            return jsonify({
                "status": "success",
                "retrabajo": ret
            })
    return jsonify({"status": "error", "message": "Garantía no encontrada para este ticket"}), 404


@reportes_bp.route("/api/garantia/reasignar", methods=["POST"])
def reasignar_retrabajo():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json() or {}
    ticket = str(data.get("ticket", "")).strip().upper()
    if not ticket:
        return jsonify({"status": "error", "message": "Ticket no especificado"}), 400

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])
    
    encontrado = None
    for ret in todos:
        r_id = str(ret.get("id", "")).strip().upper()
        r_orig = str(ret.get("ticket_original", "")).strip().upper()
        r_tick = str(ret.get("ticket", "")).strip().upper()
        if ticket in [r_id, r_orig, r_tick] or (ticket.replace("REP-", "") in [r_id.replace("REP-", ""), r_orig.replace("REP-", "")]):
            encontrado = ret
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Reporte de retrabajo no encontrado"}), 404

    dp = session["usuario"].get("datos_perfil", {})
    nombres = dp.get("nombres", "")
    apellidos = dp.get("apellido_paterno", "")
    sup_nombre = f"{nombres} {apellidos}".strip() or session["usuario"].get("nombre", "Supervisor")

    encontrado["estado"] = "Reasignado"
    encontrado["fecha_reasignacion"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encontrado["supervisor_reasigno"] = sup_nombre
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar en facturas.json si corresponde
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["retrabajo"] = "Sí"
            f["estado_retrabajo"] = "Reasignado"
            if "estado_previo" not in f or not f["estado_previo"]:
                f["estado_previo"] = f.get("estado")
            f["estado"] = "Retrabajo"
            # Se empieza a contar cuando el supervisor lo vuelve a reasignar al taller
            f["num_retrabajo"] = int(f.get("num_retrabajo", 0)) + 1
            break
    escribir_json("facturas.json", facturas_data)

    # Actualizar en reportes.json
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            if "estado_previo" not in r or not r["estado_previo"]:
                r["estado_previo"] = r.get("estado")
            r["estado"] = "Retrabajo"
            break
    escribir_json("reportes.json", reportes_data)

    s2 = encontrado.get("seccion_2", {})
    nombre_taller = s2.get("proveedor") or encontrado.get("proveedor", "Taller")
    unidad = encontrado.get("unidad", "S/N")
    motivo_chofer = encontrado.get("motivo_chofer", "Falla persistente no reparada de manera correcta")
    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket

    # Buscar correo del taller en usuarios.json
    usuarios_data = leer_json("usuarios.json")
    correo_taller = None
    target_taller = str(nombre_taller or "").strip().upper()
    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "proveedores":
            perf = u.get("datos_perfil", {})
            nom_prov = str(perf.get("nombre_proveedor") or u.get("nombre_proveedor") or "").strip().upper()
            user_prov = str(u.get("usuario") or "").strip().upper()
            if nom_prov == target_taller or user_prov == target_taller or (nom_prov and nom_prov in target_taller) or (target_taller and target_taller in nom_prov):
                correo_taller = perf.get("correo") or u.get("correo")
                break

    if not correo_taller:
        correo_taller = "armandoramireztelnor2026@gmail.com"

    try:
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

    return jsonify({
        "status": "success",
        "message": f"Retrabajo para el ticket {ticket_display} reasignado exitosamente al taller {nombre_taller}. Se envió notificación por correo."
    })


@reportes_bp.route("/api/garantia/cancelar_reasignacion", methods=["POST"])
def cancelar_reasignacion_retrabajo():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json() or {}
    ticket = str(data.get("ticket", "")).strip().upper()
    motivo_cancelacion = str(data.get("motivo", "")).strip()

    if not ticket:
        return jsonify({"status": "error", "message": "Ticket no especificado"}), 400
    if not motivo_cancelacion:
        return jsonify({"status": "error", "message": "Debes especificar el motivo de cancelación"}), 400

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])
    
    encontrado = None
    for ret in todos:
        r_id = str(ret.get("id", "")).strip().upper()
        r_orig = str(ret.get("ticket_original", "")).strip().upper()
        r_tick = str(ret.get("ticket", "")).strip().upper()
        if ticket in [r_id, r_orig, r_tick] or (ticket.replace("REP-", "") in [r_id.replace("REP-", ""), r_orig.replace("REP-", "")]):
            encontrado = ret
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Reporte de retrabajo no encontrado"}), 404

    s1 = encontrado.get("seccion_1", {})
    correo_chofer = s1.get("email")
    nombre_chofer = s1.get("empleado", "Chofer / Empleado")
    unidad = encontrado.get("unidad", "S/N")
    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket

    dp = session["usuario"].get("datos_perfil", {})
    nombres = dp.get("nombres", "")
    apellidos = dp.get("apellido_paterno", "")
    sup_nombre = f"{nombres} {apellidos}".strip() or session["usuario"].get("nombre", "Supervisor")

    if not correo_chofer:
        correo_chofer = "armandoramireztelnor2026@gmail.com"

    try:
        enviar_correo_cancelacion_retrabajo_chofer(
            correo_chofer=correo_chofer,
            nombre_chofer=nombre_chofer,
            ticket=ticket_display,
            unidad=unidad,
            motivo_cancelacion=motivo_cancelacion,
            nombre_supervisor=sup_nombre
        )
    except Exception as e:
        print(f"Error al enviar correo de cancelación de retrabajo al chofer: {e}")

    # Eliminar reporte de retrabajo de retrabajos.json (requisito explícito del usuario)
    id_enc = str(encontrado.get("id", "")).strip().upper()
    orig_enc = str(encontrado.get("ticket_original", "")).strip().upper()
    retrabajos_data["retrabajos"] = [
        r for r in todos 
        if str(r.get("id", "")).strip().upper() != id_enc
        and str(r.get("ticket_original", "")).strip().upper() != orig_enc
    ]
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar en facturas.json si corresponde
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["retrabajo"] = "Cancelado"
            f["estado_retrabajo"] = "Cancelado"
            f["motivo_cancelacion_retrabajo"] = motivo_cancelacion
            f["estado"] = f.get("estado_previo") or "Archivado"
            if not f.get("num_retrabajo"):
                f["num_retrabajo"] = 0
            break
    escribir_json("facturas.json", facturas_data)

    # Restaurar en reportes.json si corresponde
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            r["estado"] = r.get("estado_previo") or "Finalizado"
            break
    escribir_json("reportes.json", reportes_data)

    return jsonify({
        "status": "success",
        "message": f"La reasignación del ticket {ticket_display} ha sido cancelada. El reporte de retrabajo fue eliminado y se notificó al chofer."
    })


@reportes_bp.route("/api/garantia/proveedor/lista", methods=["GET"])
def obtener_retrabajos_proveedor():
    if "usuario" not in session or session["usuario"].get("rol") != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    dp = session["usuario"].get("datos_perfil", {})
    mi_proveedor = str(dp.get("nombre_proveedor", "")).strip().upper()
    mi_usuario = str(session["usuario"].get("usuario", "")).strip().upper()

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    filtrados = []
    for ret in todos:
        s2 = ret.get("seccion_2", {})
        prov_ret = str(s2.get("proveedor") or ret.get("proveedor") or ret.get("taller") or "").strip().upper()
        estado = str(ret.get("estado", "")).strip()
        
        coincide = False
        if mi_proveedor and (prov_ret == mi_proveedor or prov_ret in mi_proveedor or mi_proveedor in prov_ret):
            coincide = True
        elif mi_usuario and (prov_ret == mi_usuario or mi_usuario in prov_ret):
            coincide = True

        if coincide and estado in ["Reasignado", "Reasignado_Taller"]:
            filtrados.append(ret)

    return jsonify({
        "status": "success",
        "total": len(filtrados),
        "retrabajos": filtrados
    })


@reportes_bp.route("/api/garantia/taller/finalizar", methods=["POST"])
def finalizar_retrabajo_taller():
    if "usuario" not in session or session["usuario"].get("rol") != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json() or {}
    ticket = str(data.get("ticket", "")).strip().upper()
    if not ticket:
        return jsonify({"status": "error", "message": "Ticket no especificado"}), 400

    retrabajos_data = leer_json("retrabajos.json")
    todos = retrabajos_data.get("retrabajos", [])

    encontrado = None
    for ret in todos:
        r_id = str(ret.get("id", "")).strip().upper()
        r_orig = str(ret.get("ticket_original", "")).strip().upper()
        r_tick = str(ret.get("ticket", "")).strip().upper()
        if ticket in [r_id, r_orig, r_tick] or (ticket.replace("REP-", "") in [r_id.replace("REP-", ""), r_orig.replace("REP-", "")]):
            encontrado = ret
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Reporte de retrabajo no encontrado"}), 404

    dp = session["usuario"].get("datos_perfil", {})
    taller_nombre = dp.get("nombre_proveedor", "Taller")

    # Actualizar estado en retrabajos.json
    encontrado["estado"] = "Finalizado"
    encontrado["fecha_finalizacion_taller"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_json("retrabajos.json", retrabajos_data)

    # Actualizar estado en facturas.json y restaurar estado previo
    facturas_data = leer_json("facturas.json")
    f_id = str(encontrado.get("factura_id", "")).strip().upper()
    for f in facturas_data.get("facturas", []):
        if str(f.get("id", "")).strip().upper() == f_id or ticket in str(f.get("retro", "")).upper() or str(f.get("id_reporte", "")).upper() == ticket:
            f["estado_retrabajo"] = "Finalizado"
            f["estado"] = f.get("estado_previo") or "Archivado"
            break
    escribir_json("facturas.json", facturas_data)

    # Actualizar estado en reportes.json
    reportes_data = leer_json("reportes.json")
    for r in reportes_data.get("reportes", []):
        r_id_clean = str(r.get("id", "")).strip().upper()
        if r_id_clean == ticket or r_id_clean == str(encontrado.get("ticket_original", "")).strip().upper():
            r["estado"] = r.get("estado_previo") or "Finalizado"
            break
    escribir_json("reportes.json", reportes_data)

    ticket_display = encontrado.get("ticket_original") or encontrado.get("ticket") or ticket
    return jsonify({
        "status": "success",
        "message": f"El retrabajo para el ticket {ticket_display} ha sido marcado como FINALIZADO exitosamente por el taller {taller_nombre}."
    })







@reportes_bp.route("/api/proveedor/actualizar_garantia", methods=["POST"])
def actualizar_garantia_proveedor():
    if "usuario" not in session or session["usuario"].get("rol") not in ["proveedores", "proveedor"]:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json() or {}
    try:
        dias = int(data.get("dias_garantia", 0))
        horas = int(data.get("horas_garantia", 0))
        minutos = int(data.get("minutos_garantia", 0))
        segundos = int(data.get("segundos_garantia", 0))
        
        total_segundos = dias * 86400 + horas * 3600 + minutos * 60 + segundos
        if total_segundos <= 0:
            return jsonify({"status": "error", "message": "El tiempo de garantía debe ser mayor a 0 segundos."}), 400
        if total_segundos > 365 * 86400:
            return jsonify({"status": "error", "message": "El tiempo de garantía no puede exceder 365 días."}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Valores de tiempo inválidos."}), 400

    mi_usuario = session["usuario"].get("usuario")
    mi_nombre_prov = session["usuario"].get("datos_perfil", {}).get("nombre_proveedor", "")
    usuarios_data = leer_json("usuarios.json")
    actualizado = False

    for u in usuarios_data.get("usuarios", []):
        if u.get("usuario") == mi_usuario or (mi_nombre_prov and u.get("datos_perfil", {}).get("nombre_proveedor") == mi_nombre_prov):
            if "datos_perfil" not in u:
                u["datos_perfil"] = {}
            u["datos_perfil"]["dias_garantia"] = dias
            u["datos_perfil"]["horas_garantia"] = horas
            u["datos_perfil"]["minutos_garantia"] = minutos
            u["datos_perfil"]["segundos_garantia"] = segundos
            u["datos_perfil"]["total_segundos_garantia"] = total_segundos
            u["datos_perfil"]["fecha_actualizacion_garantia"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "usuario" in session and "datos_perfil" in session["usuario"]:
                session["usuario"]["datos_perfil"]["dias_garantia"] = dias
                session["usuario"]["datos_perfil"]["horas_garantia"] = horas
                session["usuario"]["datos_perfil"]["minutos_garantia"] = minutos
                session["usuario"]["datos_perfil"]["segundos_garantia"] = segundos
                session["usuario"]["datos_perfil"]["total_segundos_garantia"] = total_segundos
            actualizado = True
            break

    if actualizado:
        escribir_json("usuarios.json", usuarios_data)
        txt_tiempo = formatear_duracion_segundos(total_segundos)
        return jsonify({
            "status": "success",
            "message": f"Tiempo de garantía actualizado a {txt_tiempo} exitosamente. Jefatura ha sido notificada de este periodo.",
            "tiempo_formateado": txt_tiempo
        })
    return jsonify({"status": "error", "message": "Usuario de taller no encontrado"}), 404


@reportes_bp.route("/api/garantia/talleres_tiempo", methods=["GET"])
def obtener_talleres_tiempo_garantia():
    if "usuario" not in session or session["usuario"].get("rol") not in ["administracion"]:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    usuarios_data = leer_json("usuarios.json")
    talleres = []

    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "proveedores":
            dp = u.get("datos_perfil", {})
            try:
                dias_gar = int(dp.get("dias_garantia", 30))
            except:
                dias_gar = 30
            try:
                horas_gar = int(dp.get("horas_garantia", 0))
            except:
                horas_gar = 0
            try:
                mins_gar = int(dp.get("minutos_garantia", 0))
            except:
                mins_gar = 0
            try:
                segs_gar = int(dp.get("segundos_garantia", 0))
            except:
                segs_gar = 0
            
            tot_segs = dias_gar * 86400 + horas_gar * 3600 + mins_gar * 60 + segs_gar
            if tot_segs <= 0:
                tot_segs = 30 * 86400
                dias_gar = 30

            foto = dp.get("foto_ruta", "")
            if foto and not foto.startswith("/") and not foto.startswith("http"):
                foto = f"/static/logos_proveedores/{foto}"

            talleres.append({
                "usuario": u.get("usuario"),
                "nombre_proveedor": dp.get("nombre_proveedor") or u.get("usuario"),
                "encargado": dp.get("encargado", "N/A"),
                "telefono": dp.get("telefono", "N/A"),
                "correo": dp.get("correo", "N/A"),
                "ciudad": dp.get("ciudad", "N/A"),
                "cope": dp.get("cope", "N/A"),
                "dias_garantia": dias_gar,
                "horas_garantia": horas_gar,
                "minutos_garantia": mins_gar,
                "segundos_garantia": segs_gar,
                "total_segundos": tot_segs,
                "tiempo_formateado": formatear_duracion_segundos(tot_segs),
                "tiempo_corta": formatear_duracion_corta(tot_segs),
                "garantia_configurada": bool(dp.get("dias_garantia") or dp.get("horas_garantia") or dp.get("minutos_garantia") or dp.get("segundos_garantia")),
                "fecha_actualizacion": dp.get("fecha_actualizacion_garantia", "Predefinido (30 días)"),
                "foto_ruta": foto
            })

    return jsonify({"status": "success", "talleres": talleres})


@reportes_bp.route("/api/garantia/taller/actualizar_dias", methods=["POST"])
def actualizar_dias_garantia_jefatura():
    if "usuario" not in session or session["usuario"].get("rol") not in ["administracion"]:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json() or {}
    usuario_taller = str(data.get("usuario", "")).strip()
    try:
        dias = int(data.get("dias_garantia", 0))
        horas = int(data.get("horas_garantia", 0))
        minutos = int(data.get("minutos_garantia", 0))
        segundos = int(data.get("segundos_garantia", 0))
        
        total_segundos = dias * 86400 + horas * 3600 + minutos * 60 + segundos
        if total_segundos <= 0:
            return jsonify({"status": "error", "message": "El tiempo de garantía debe ser mayor a 0 segundos."}), 400
        if total_segundos > 365 * 86400:
            return jsonify({"status": "error", "message": "El tiempo de garantía no puede exceder 365 días."}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Valores de tiempo inválidos."}), 400

    usuarios_data = leer_json("usuarios.json")
    encontrado = False

    for u in usuarios_data.get("usuarios", []):
        if u.get("usuario") == usuario_taller or u.get("datos_perfil", {}).get("nombre_proveedor") == usuario_taller:
            if "datos_perfil" not in u:
                u["datos_perfil"] = {}
            u["datos_perfil"]["dias_garantia"] = dias
            u["datos_perfil"]["horas_garantia"] = horas
            u["datos_perfil"]["minutos_garantia"] = minutos
            u["datos_perfil"]["segundos_garantia"] = segundos
            u["datos_perfil"]["total_segundos_garantia"] = total_segundos
            u["datos_perfil"]["fecha_actualizacion_garantia"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (Ajustado por Jefatura)"
            encontrado = True
            break

    if encontrado:
        escribir_json("usuarios.json", usuarios_data)
        txt_tiempo = formatear_duracion_segundos(total_segundos)
        return jsonify({
            "status": "success",
            "message": f"Tiempo de garantía para el taller actualizado a {txt_tiempo}.",
            "tiempo_formateado": txt_tiempo
        })
    return jsonify({"status": "error", "message": "Taller no encontrado."}), 404
