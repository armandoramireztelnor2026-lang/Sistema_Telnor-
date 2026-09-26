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

# COPEs disponibles: se leen dinámicamente del catálogo
def get_copes_disponibles():
    data = leer_json('ciudades_copes.json')
    copes = []
    for ciudad in data.get('ciudades', []):
        copes.extend(ciudad.get('copes', []))
    return sorted(set(copes))

# Mantener CIUDADES_DISPONIBLES para compatibilidad de otros campos del perfil
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
    return jsonify({"ciudades": CIUDADES_DISPONIBLES, "copes": get_copes_disponibles()})


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
            "copes_asignados": dp.get("copes_asignados", [])
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
        "ciudades_disponibles": CIUDADES_DISPONIBLES,
        "copes_disponibles": get_copes_disponibles()
    })


@panel_control_bp.route('/api/panel/asignar_cope', methods=['POST'])
def asignar_cope():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    usuario_id = request.json.get('usuario')
    cope = request.json.get('cope')
    if not usuario_id or not cope:
        return jsonify({"status": "error", "message": "Faltan datos."})
    if cope not in COPES_DISPONIBLES:
        return jsonify({"status": "error", "message": f"COPE '{cope}' no es válido."})

    usuarios_data = leer_json('usuarios.json')
    encontrado = False
    correo_destino = ""
    nombre_destino = ""

    for u in usuarios_data.get('usuarios', []):
        if u.get('usuario') == usuario_id and u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            subrol = dp.get('subrol', '')
            if subrol == 'Jefatura':
                return jsonify({"status": "error", "message": "No se pueden asignar COPEs a Jefatura desde aquí."})
            
            copes = dp.get('copes_asignados', [])
            if cope in copes:
                return jsonify({"status": "error", "message": f"El COPE '{cope}' ya está asignado."})
            if cope == dp.get('cope', ''):
                return jsonify({"status": "error", "message": f"'{cope}' ya es su COPE principal."})

            copes.append(cope)
            dp['copes_asignados'] = copes
            correo_destino = dp.get('correo', '')
            nombre_destino = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
            encontrado = True
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Usuario no encontrado."})

    escribir_json('usuarios.json', usuarios_data)

    if correo_destino:
        try:
            enviar_correo_ciudad_asignada(correo_destino, nombre_destino, cope, obtener_nombre_sesion())
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return jsonify({"status": "success", "message": f"COPE '{cope}' asignado a {nombre_destino} exitosamente."})


# Mantener endpoint antiguo por retrocompatibilidad
@panel_control_bp.route('/api/panel/asignar_ciudad', methods=['POST'])
def asignar_ciudad():
    # Redirigir internamente a asignar_cope renombrando el campo
    if request.json:
        request.json['cope'] = request.json.get('ciudad', '')
    return asignar_cope()


@panel_control_bp.route('/api/panel/quitar_cope', methods=['POST'])
def quitar_cope():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    usuario_id = request.json.get('usuario')
    cope = request.json.get('cope')
    if not usuario_id or not cope:
        return jsonify({"status": "error", "message": "Faltan datos."})

    usuarios_data = leer_json('usuarios.json')
    encontrado = False
    correo_destino = ""
    nombre_destino = ""

    for u in usuarios_data.get('usuarios', []):
        if u.get('usuario') == usuario_id and u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            copes = dp.get('copes_asignados', [])
            if cope not in copes:
                return jsonify({"status": "error", "message": f"El COPE '{cope}' no está asignado."})

            # === REGLA: NO QUITAR COPE SI HAY TICKETS ACTIVOS ===
            reportes_data = leer_json("reportes.json")
            for r in reportes_data.get("reportes", []):
                if r.get("cope") == cope and r.get("estado") not in ["Eliminado", "Finalizado"]:
                    return jsonify({"status": "error", "message": f"No se puede remover el COPE porque hay reportes activos en {cope} (Ej. {r.get('id')}). Deben finalizarse primero."})

            facturas_data = leer_json("facturas.json")
            reportes_dict = {str(r.get("id")): r for r in reportes_data.get("reportes", [])}
            import re as _re
            for f in facturas_data.get("facturas", []):
                retro = f.get("retro", "")
                m = _re.search(r"\[TICKET:(.*?)\]", retro)
                if m:
                    rep = reportes_dict.get(m.group(1).strip(), {})
                    if rep.get("cope") == cope and f.get("estado") not in ["Eliminado", "Finalizado", "Rechazado", "Cancelado_Cotizacion_Cara"]:
                        t_id = f.get("id_reporte") or f.get("numero_reporte") or f.get("id")
                        return jsonify({"status": "error", "message": f"No se puede remover el COPE porque hay tickets activos en {cope} (Ej. Factura {t_id}). Deben finalizarse primero."})

            copes.remove(cope)
            dp['copes_asignados'] = copes
            correo_destino = dp.get('correo', '')
            nombre_destino = f"{dp.get('nombres', '')} {dp.get('apellido_paterno', '')}".strip()
            encontrado = True
            break

    if not encontrado:
        return jsonify({"status": "error", "message": "Usuario no encontrado."})

    escribir_json('usuarios.json', usuarios_data)

    if correo_destino:
        try:
            enviar_correo_ciudad_removida(correo_destino, nombre_destino, cope, obtener_nombre_sesion())
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return jsonify({"status": "success", "message": f"COPE '{cope}' removido de {nombre_destino}."})


# Mantener endpoint antiguo por retrocompatibilidad
@panel_control_bp.route('/api/panel/quitar_ciudad', methods=['POST'])
def quitar_ciudad():
    if request.json:
        request.json['cope'] = request.json.get('ciudad', '')
    return quitar_cope()

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
