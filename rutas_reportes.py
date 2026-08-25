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
        if u["rol"] == "administracion":
            subrol = u["datos_perfil"].get("subrol", "Administración")
            ciudad_admin = u["datos_perfil"].get("ciudad", "")
            
            if subrol == "Jefatura" or ciudad_admin == reporte["ciudad"]:
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
            mi_ciudad = session['usuario']['datos_perfil'].get('ciudad', '')
            # Solo dejamos los reportes que coincidan con la ciudad del Supervisor
            data['reportes'] = [r for r in data.get('reportes', []) if r.get('ciudad') == mi_ciudad]
            
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

