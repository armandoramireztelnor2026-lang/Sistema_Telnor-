import os
import json
from flask import Blueprint, jsonify, session

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, "r", encoding="utf-8") as f: return json.load(f)

seccion_reportes_bp = Blueprint('seccion_reportes_bp', __name__)

@seccion_reportes_bp.route('/api/seccion_reportes/lista', methods=['GET'])
def obtener_lista_seccion_reportes():
    """
    Retorna la lista de todas las facturas/tickets para la vista general de la Jefatura.
    Solo accesible para usuarios con subrol 'Jefatura'.
    """
    if "usuario" not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    usuario = session["usuario"]
    # Jefatura puede ver esto (el rol es administracion, subrol Jefatura)
    if usuario.get("rol") != "administracion" or usuario.get("datos_perfil", {}).get("subrol") != "Jefatura":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    facturas_data = leer_json('facturas.json')
    todas_facturas = facturas_data.get("facturas", [])
    
    # Podemos procesar la data si es necesario, o enviarla cruda
    return jsonify({
        "status": "success",
        "facturas": todas_facturas
    })
