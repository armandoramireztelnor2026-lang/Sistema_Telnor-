# =========================================================
# ARCHIVO: rutas_ciudades_copes.py
# PROPÓSITO: CRUD de ciudades y COPEs para panel Jefatura
# =========================================================
from flask import Blueprint, request, jsonify, session
import json
import os

ciudades_copes_bp = Blueprint("ciudades_copes_bp", __name__)

ARCHIVO = "ciudades_copes.json"

def leer_json(archivo):
    if not os.path.exists(archivo):
        return {}
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def escribir_json(archivo, data):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def es_jefatura():
    u = session.get("usuario", {})
    return u.get("datos_perfil", {}).get("subrol") == "Jefatura"


# ── GET: listar todas las ciudades y sus COPEs (requiere Jefatura) ──────────
@ciudades_copes_bp.route("/api/ciudades_copes", methods=["GET"])
def listar_ciudades_copes():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
    data = leer_json(ARCHIVO)
    return jsonify({"status": "success", "ciudades": data.get("ciudades", [])})


# ── GET: catálogo público para formulario de reporte (sin auth) ────────────
@ciudades_copes_bp.route("/api/catalogo_ciudades", methods=["GET"])
def catalogo_ciudades():
    """Devuelve el catálogo ciudad→COPEs para el dropdown del formulario del chofer."""
    data = leer_json(ARCHIVO)
    resultado = {}
    for ciudad in data.get("ciudades", []):
        resultado[ciudad["nombre"]] = ciudad.get("copes", [])
    return jsonify({"status": "success", "catalogo": resultado})


# ── POST: agregar una ciudad nueva ──────────────────────────────────────────
@ciudades_copes_bp.route("/api/ciudades_copes/agregar_ciudad", methods=["POST"])
def agregar_ciudad():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
    nombre = request.json.get("nombre", "").strip()
    if not nombre:
        return jsonify({"status": "error", "message": "El nombre de la ciudad no puede estar vacío."})
    data = leer_json(ARCHIVO)
    ciudades = data.get("ciudades", [])
    if any(c["nombre"].lower() == nombre.lower() for c in ciudades):
        return jsonify({"status": "error", "message": f"La ciudad '{nombre}' ya existe."})
    ciudades.append({"nombre": nombre, "copes": []})
    data["ciudades"] = ciudades
    escribir_json(ARCHIVO, data)
    return jsonify({"status": "success", "message": f"Ciudad '{nombre}' agregada exitosamente."})


# ── POST: eliminar una ciudad ───────────────────────────────────────────────
@ciudades_copes_bp.route("/api/ciudades_copes/eliminar_ciudad", methods=["POST"])
def eliminar_ciudad():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
    nombre = request.json.get("nombre", "").strip()
    data = leer_json(ARCHIVO)
    ciudades = data.get("ciudades", [])

    ciudad_obj = next((c for c in ciudades if c["nombre"] == nombre), None)
    if not ciudad_obj:
        return jsonify({"status": "error", "message": f"Ciudad '{nombre}' no encontrada."})

    # Verificar que no haya COPEs activos con tickets
    if ciudad_obj.get("copes"):
        reportes = leer_json("reportes.json")
        copes_ciudad = set(ciudad_obj["copes"])
        for r in reportes.get("reportes", []):
            if r.get("cope") in copes_ciudad and r.get("estado") not in ["Eliminado", "Finalizado"]:
                return jsonify({"status": "error", "message": f"No se puede eliminar '{nombre}': hay reportes activos en sus COPEs."})

    data["ciudades"] = [c for c in ciudades if c["nombre"] != nombre]
    escribir_json(ARCHIVO, data)
    return jsonify({"status": "success", "message": f"Ciudad '{nombre}' eliminada."})


# ── POST: agregar un COPE a una ciudad ─────────────────────────────────────
@ciudades_copes_bp.route("/api/ciudades_copes/agregar_cope", methods=["POST"])
def agregar_cope():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
    ciudad_nombre = request.json.get("ciudad", "").strip()
    cope = request.json.get("cope", "").strip().upper()
    if not ciudad_nombre or not cope:
        return jsonify({"status": "error", "message": "Faltan datos."})
    data = leer_json(ARCHIVO)
    for c in data.get("ciudades", []):
        if c["nombre"] == ciudad_nombre:
            if cope in [cp.upper() for cp in c["copes"]]:
                return jsonify({"status": "error", "message": f"El COPE '{cope}' ya existe en {ciudad_nombre}."})
            # Verificar que no esté en otra ciudad
            for otra in data["ciudades"]:
                if otra["nombre"] != ciudad_nombre and cope in [cp.upper() for cp in otra.get("copes", [])]:
                    return jsonify({"status": "error", "message": f"El COPE '{cope}' ya pertenece a la ciudad '{otra['nombre']}'."})
            c["copes"].append(cope)
            escribir_json(ARCHIVO, data)
            return jsonify({"status": "success", "message": f"COPE '{cope}' agregado a {ciudad_nombre}."})
    return jsonify({"status": "error", "message": f"Ciudad '{ciudad_nombre}' no encontrada."})


# ── POST: eliminar un COPE de una ciudad ───────────────────────────────────
@ciudades_copes_bp.route("/api/ciudades_copes/eliminar_cope", methods=["POST"])
def eliminar_cope():
    if not es_jefatura():
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
    ciudad_nombre = request.json.get("ciudad", "").strip()
    cope = request.json.get("cope", "").strip()
    if not ciudad_nombre or not cope:
        return jsonify({"status": "error", "message": "Faltan datos."})

    # Verificar que no haya tickets activos en ese COPE
    reportes = leer_json("reportes.json")
    for r in reportes.get("reportes", []):
        if r.get("cope") == cope and r.get("estado") not in ["Eliminado", "Finalizado"]:
            return jsonify({"status": "error", "message": f"No se puede eliminar '{cope}': hay reportes activos (Ej. {r.get('id')}). Deben finalizarse primero."})

    data = leer_json(ARCHIVO)
    for c in data.get("ciudades", []):
        if c["nombre"] == ciudad_nombre:
            if cope not in c["copes"]:
                return jsonify({"status": "error", "message": f"El COPE '{cope}' no existe en {ciudad_nombre}."})
            c["copes"].remove(cope)
            escribir_json(ARCHIVO, data)
            return jsonify({"status": "success", "message": f"COPE '{cope}' eliminado de {ciudad_nombre}."})
    return jsonify({"status": "error", "message": f"Ciudad '{ciudad_nombre}' no encontrada."})
