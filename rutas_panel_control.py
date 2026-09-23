# =========================================================
# ARCHIVO: rutas_panel_control.py
# PROPÓSITO: API para Panel de Control de Jefatura
# =========================================================
from flask import Blueprint, request, jsonify, session
import json
import os

from notificaciones import (
    enviar_correo_ciudad_asignada,
    enviar_correo_ciudad_removida,
    enviar_correo_cambio_subrol
)

panel_control_bp = Blueprint("panel_control_bp", __name__)

# Catálogo fijo de ciudades disponibles en Telnor
CIUDADES_DISPONIBLES = [
    "Tijuana", "Mexicali", "Ensenada", "Tecate", "Rosarito", "San Quintin", "San Felipe"
]

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)

def escribir_json(archivo, data):
    with open(archivo, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def obtener_nombre_sesion():
    u = session.get('usuario', {})
    dp = u.get('datos_perfil', {})
    return f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip() or "Sistema"

def es_jefatura():
    u = session.get('usuario', {})
    return u.get('datos_perfil', {}).get('subrol') == 'Jefatura'


@panel_control_bp.route('/api/panel/ciudades_disponibles', methods=['GET'])
def ciudades_disponibles():
    return jsonify({"ciudades": CIUDADES_DISPONIBLES})


@panel_control_bp.route('/api/panel/personal', methods=['GET'])
def listar_personal():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura."}), 403

    usuarios_data = leer_json('usuarios.json')
    jefatura = []
    supervisores = []
    administradores = []

    for u in usuarios_data.get('usuarios', []):
        if u.get('rol') != 'administracion':
            continue
        dp = u.get('datos_perfil', {})
        perfil = {
            "usuario": u.get("usuario"),
            "nombres": dp.get("nombres", ""),
            "apellido_paterno": dp.get("apellido_paterno", ""),
            "apellido_materno": dp.get("apellido_materno", ""),
            "subrol": dp.get("subrol", ""),
            "ciudad": dp.get("ciudad", ""),
            "cope": dp.get("cope", ""),
            "area": dp.get("area", ""),
            "correo": dp.get("correo", ""),
            "num_empleado": dp.get("num_empleado", ""),
            "foto_ruta": dp.get("foto_ruta", ""),
            "ciudades_asignadas": dp.get("ciudades_asignadas", [])
        }
        subrol = dp.get("subrol", "")
        if subrol == "Jefatura":
            jefatura.append(perfil)
        elif subrol == "Supervisor":
            supervisores.append(perfil)
        elif subrol == "Administrador":
            administradores.append(perfil)

    return jsonify({
        "status": "success",
        "jefatura": jefatura,
        "supervisores": supervisores,
        "administradores": administradores,
        "ciudades_disponibles": CIUDADES_DISPONIBLES
    })


@panel_control_bp.route('/api/panel/asignar_ciudad', methods=['POST'])
def asignar_ciudad():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    usuario_id = request.json.get('usuario')
    ciudad = request.json.get('ciudad')
    if not usuario_id or not ciudad:
        return jsonify({"status": "error", "message": "Faltan datos."})
    if ciudad not in CIUDADES_DISPONIBLES:
        return jsonify({"status": "error", "message": f"Ciudad '{ciudad}' no es válida."})

    usuarios_data = leer_json('usuarios.json')
    encontrado = False
    correo_destino = ""
    nombre_destino = ""

    for u in usuarios_data.get('usuarios', []):
        if u.get('usuario') == usuario_id and u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            subrol = dp.get('subrol', '')
            if subrol == 'Jefatura':
                return jsonify({"status": "error", "message": "No se pueden asignar ciudades a Jefatura desde aquí."})
            
            ciudades = dp.get('ciudades_asignadas', [])
            if ciudad in ciudades:
                return jsonify({"status": "error", "message": f"La ciudad '{ciudad}' ya está asignada."})
            if ciudad == dp.get('ciudad', ''):
                return jsonify({"status": "error", "message": f"'{ciudad}' ya es su ciudad principal."})

            ciudades.append(ciudad)
            dp['ciudades_asignadas'] = ciudades
            correo_destino = dp.get('correo', '')
            nombre_destino = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
            encontrado = True
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Usuario no encontrado."})

    escribir_json('usuarios.json', usuarios_data)

    if correo_destino:
        try:
            enviar_correo_ciudad_asignada(correo_destino, nombre_destino, ciudad, obtener_nombre_sesion())
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return jsonify({"status": "success", "message": f"Ciudad '{ciudad}' asignada a {nombre_destino} exitosamente."})


@panel_control_bp.route('/api/panel/quitar_ciudad', methods=['POST'])
def quitar_ciudad():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    usuario_id = request.json.get('usuario')
    ciudad = request.json.get('ciudad')
    if not usuario_id or not ciudad:
        return jsonify({"status": "error", "message": "Faltan datos."})

    usuarios_data = leer_json('usuarios.json')
    encontrado = False
    correo_destino = ""
    nombre_destino = ""

    for u in usuarios_data.get('usuarios', []):
        if u.get('usuario') == usuario_id and u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            ciudades = dp.get('ciudades_asignadas', [])
            if ciudad not in ciudades:
                return jsonify({"status": "error", "message": f"La ciudad '{ciudad}' no está asignada."})

            # === REGLA: NO QUITAR CIUDAD SI HAY TICKETS ACTIVOS ===
            reportes_data = leer_json("reportes.json")
            for r in reportes_data.get("reportes", []):
                if r.get("ciudad") == ciudad and r.get("estado") not in ["Eliminado", "Finalizado"]:
                    return jsonify({"status": "error", "message": f"No se puede remover la ciudad porque hay reportes activos en {ciudad} (Ej. {r.get('id')}). Deben finalizarse primero."})

            facturas_data = leer_json("facturas.json")
            proveedores_ciudad = [usr["datos_perfil"]["nombre_proveedor"] for usr in usuarios_data.get("usuarios", []) if usr.get("rol") == "proveedores" and usr.get("datos_perfil", {}).get("ciudad") == ciudad]

            for f in facturas_data.get("facturas", []):
                if f.get("proveedor") in proveedores_ciudad and f.get("estado") not in ["Eliminado", "Finalizado", "Rechazado", "Cancelado_Cotizacion_Cara"]:
                    t_id = f.get("id_reporte") or f.get("numero_reporte") or f.get("id")
                    return jsonify({"status": "error", "message": f"No se puede remover la ciudad porque hay tickets activos en {ciudad} (Ej. Factura {t_id}). Deben finalizarse primero."})


            ciudades.remove(ciudad)
            dp['ciudades_asignadas'] = ciudades
            correo_destino = dp.get('correo', '')
            nombre_destino = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
            encontrado = True
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Usuario no encontrado."})

    escribir_json('usuarios.json', usuarios_data)

    if correo_destino:
        try:
            enviar_correo_ciudad_removida(correo_destino, nombre_destino, ciudad, obtener_nombre_sesion())
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return jsonify({"status": "success", "message": f"Ciudad '{ciudad}' removida de {nombre_destino}."})


@panel_control_bp.route('/api/panel/cambiar_subrol', methods=['POST'])
def cambiar_subrol():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    usuario_id = request.json.get('usuario')
    if not usuario_id:
        return jsonify({"status": "error", "message": "Falta el usuario."})

    usuarios_data = leer_json('usuarios.json')
    encontrado = False
    correo_destino = ""
    nombre_destino = ""
    nuevo_subrol = ""

    for u in usuarios_data.get('usuarios', []):
        if u.get('usuario') == usuario_id and u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            subrol_actual = dp.get('subrol')
            if subrol_actual == 'Jefatura':
                return jsonify({"status": "error", "message": "No se puede cambiar el rol a otro usuario de Jefatura."})

            nuevo_subrol = 'Supervisor' if subrol_actual == 'Administrador' else 'Administrador'
            dp['subrol'] = nuevo_subrol
            correo_destino = dp.get('correo', '')
            nombre_destino = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
            encontrado = True
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Usuario no encontrado."})

    escribir_json('usuarios.json', usuarios_data)

    if correo_destino:
        try:
            enviar_correo_cambio_subrol(correo_destino, nombre_destino, nuevo_subrol, obtener_nombre_sesion())
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return jsonify({"status": "success", "message": f"{nombre_destino} ha sido cambiado a {nuevo_subrol} exitosamente."})
