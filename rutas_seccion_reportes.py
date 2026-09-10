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
    # Todos en administracion pueden ver esto
    if usuario.get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    facturas_data = leer_json('facturas.json')
    todas_facturas = facturas_data.get("facturas", [])
    
    # Podemos procesar la data si es necesario, o enviarla cruda
    return jsonify({
        "status": "success",
        "facturas": todas_facturas
    })

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

@seccion_reportes_bp.route('/api/seccion_reportes/comentario', methods=['POST'])
def guardar_comentario():
    if "usuario" not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    usuario = session["usuario"]
    if usuario.get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    from flask import request
    data = request.json
    ticket_id = data.get("id")
    is_unassigned = data.get("is_unassigned", False)
    
    import re
    comentario = data.get("comentario", "").strip()
    action = data.get("action", "save")
    
    nombre_completo = f"{usuario.get('datos_perfil', {}).get('nombres', '')} {usuario.get('datos_perfil', {}).get('apellido_paterno', '')}".strip()
    if not nombre_completo:
        nombre_completo = "Usuario"
        
    if action == "delete":
        comentario = ""
        eliminado_por = nombre_completo
    else:
        comentario = re.sub(r'\s*\(Actualizado por:.*?\)$', '', comentario).strip()
        eliminado_por = ""

    if not ticket_id:
        return jsonify({"status": "error", "message": "ID de ticket requerido"}), 400

    encontrado = False

    if is_unassigned:
        # Guardar en reportes.json
        reportes_data = leer_json('reportes.json')
        reportes_lista = reportes_data.get("reportes", [])
        for r in reportes_lista:
            if str(r.get("id")) == str(ticket_id):
                r["comentarios"] = comentario
                r["autor_comentario"] = nombre_completo
                r["eliminado_por"] = eliminado_por
                encontrado = True
                break
        if encontrado:
            guardar_json('reportes.json', reportes_data)
    else:
        # Guardar en facturas.json
        facturas_data = leer_json('facturas.json')
        facturas_lista = facturas_data.get("facturas", [])
        for f in facturas_lista:
            if str(f.get("id")) == str(ticket_id):
                f["comentarios"] = comentario
                f["autor_comentario"] = nombre_completo
                f["eliminado_por"] = eliminado_por
                encontrado = True
                break
        if encontrado:
            guardar_json('facturas.json', facturas_data)

    if not encontrado:
        return jsonify({"status": "error", "message": "Ticket no encontrado"}), 404

    return jsonify({
        "status": "success", 
        "message": "Comentario actualizado",
        "comentario_final": comentario,
        "autor_comentario": nombre_completo,
        "eliminado_por": eliminado_por
    })
