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
)

reportes_bp = Blueprint("reportes_bp", __name__)

def leer_json(archivo):
    if not os.path.exists(archivo): return {"reportes": []}
    with open(archivo, "r", encoding="utf-8") as f: return json.load(f)

def escribir_json(archivo, data):
    with open(archivo, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)


@reportes_bp.route("/api/reportes/nuevo", methods=["POST"])
def nuevo_reporte():
    unidad_req = request.form.get("unidad")
    eco_full = f"8090-{unidad_req}"
    
    # 0. Check if the unit is inactive
    unidades_data = leer_json("unidades.json")
    if unidad_req in unidades_data and unidades_data[unidad_req].get("Estado") == "Inactiva":
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

    # 3. Validar que exista al menos un Administrador Y un Supervisor para esa ciudad
    ciudad_reporte = request.form.get("ciudad", "No especificada")
    usuarios_data = leer_json("usuarios.json")
    
    hay_admin = False
    hay_super = False
    
    for u in usuarios_data.get("usuarios", []):
        if u.get("rol") == "administracion":
            perfil = u.get("datos_perfil", {})
            subrol = perfil.get("subrol", "")
            ciudad_admin = perfil.get("ciudad", "")
            ciudades_extra = perfil.get("ciudades_asignadas", [])
            
            if ciudad_admin == ciudad_reporte or ciudad_reporte in ciudades_extra:
                if subrol == "Administrador":
                    hay_admin = True
                elif subrol == "Supervisor":
                    hay_super = True
                
    if not hay_admin or not hay_super:
        if not hay_admin and not hay_super:
            msg = f"No se puede crear el reporte: Faltan un Administrador y un Supervisor registrados para la ciudad de {ciudad_reporte}."
        elif not hay_admin:
            msg = f"No se puede crear el reporte: Falta un Administrador registrado para la ciudad de {ciudad_reporte}."
        else:
            msg = f"No se puede crear el reporte: Falta un Supervisor registrado para la ciudad de {ciudad_reporte}."
            
        return jsonify({"status": "error", "message": msg})

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
    
    # Solo notificar a los Admins de la MISMA ciudad, o a la Jefatura
    for u in usuarios_data.get("usuarios", []):
            if u.get("rol") == "administracion":
                subrol = u["datos_perfil"].get("subrol", "")
                ciudad_admin = u["datos_perfil"].get("ciudad", "")
                
                # Solo enviar a Supervisores de esa ciudad
                if subrol == "Supervisor" and ciudad_admin == reporte["ciudad"]:
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
            
            mi_ciudad = ""
            ciudades_asignadas = []
            for u in usuarios_data.get("usuarios", []):
                if u.get("usuario") == usuario_id:
                    mi_ciudad = u.get("datos_perfil", {}).get("ciudad", "")
                    ciudades_asignadas = u.get("datos_perfil", {}).get("ciudades_asignadas", [])
                    break
                    
            ciudades_permitidas = [mi_ciudad] + ciudades_asignadas
            # Solo dejamos los reportes que coincidan con la ciudad (o ciudades extra) del Supervisor
            data['reportes'] = [r for r in data.get('reportes', []) if r.get('ciudad') in ciudades_permitidas]
            
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
            enviar_correo_nueva_orden(correo_proveedor, nombre_proveedor, reporte_id, r.get("unidad", ""), r.get("falla", ""))
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
            enviar_correo_ticket_rechazado(correo_chofer, reporte_a_eliminar.get('empleado', 'Operador'), reporte_a_eliminar.get('id'), reporte_a_eliminar.get('unidad'), motivo)
        
        return jsonify({"status": "success", "message": "Reporte eliminado y usuario notificado."})


@reportes_bp.route("/api/unidades", methods=["GET"])
def obtener_unidades():
    if not os.path.exists("unidades.json"):
        return jsonify({})
    with open("unidades.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Inject flag to know if the unit is actively in the workshop/assigned
    for num, info in data.items():
        info["activa_en_taller"] = is_unidad_active(num)
        
    return jsonify(data)

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
