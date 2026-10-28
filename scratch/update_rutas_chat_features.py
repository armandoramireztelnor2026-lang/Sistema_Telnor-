# -*- coding: utf-8 -*-
import sys

with open('rutas_chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update marking as read with timestamps
old_leido = """            if m.get('receptor_usuario') == mi_usuario and not m.get('leido', False):
                m['leido'] = True
                hubo_cambios = True"""

new_leido = """            if m.get('receptor_usuario') == mi_usuario and not m.get('leido', False):
                m['leido'] = True
                ahora_leido = datetime.now()
                m['fecha_leido'] = ahora_leido.strftime("%Y-%m-%d %H:%M:%S")
                m['fecha_leido_completa'] = ahora_leido.strftime("%I:%M:%S %p • %d/%m/%Y")
                hubo_cambios = True"""

if old_leido in content:
    content = content.replace(old_leido, new_leido)
    print("OK: Replaced old_leido")
else:
    print("WARN: old_leido not found directly, trying CRLF")
    content = content.replace(old_leido.replace('\n', '\r\n'), new_leido.replace('\n', '\r\n'))

# 2. Update nuevo_mensaje with respuesta_a and eliminado: False
old_nuevo_msg = """    ahora = datetime.now()
    nuevo_mensaje = {
        "id": f"msg_{int(time.time()*1000)}",
        "emisor_usuario": mi_usuario,
        "emisor_nombre": mi_nombre,
        "emisor_rol": mi_rol,
        "receptor_usuario": receptor_id,
        "receptor_nombre": receptor_nombre,
        "receptor_rol": receptor_rol,
        "mensaje": texto,
        "fecha": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "hora_corta": ahora.strftime("%I:%M %p"),
        "fecha_completa": ahora.strftime("%I:%M %p • %d/%m/%Y"),
        "timestamp": int(time.time()),
        "leido": False
    }"""

new_nuevo_msg = """    respuesta_a = data.get('respuesta_a')
    info_respuesta = None
    if isinstance(respuesta_a, dict) and respuesta_a.get('id'):
        info_respuesta = {
            "id": str(respuesta_a.get('id')),
            "emisor_nombre": str(respuesta_a.get('emisor_nombre') or 'Usuario'),
            "mensaje": str(respuesta_a.get('mensaje') or '')[:180]
        }

    ahora = datetime.now()
    nuevo_mensaje = {
        "id": f"msg_{int(time.time()*1000)}",
        "emisor_usuario": mi_usuario,
        "emisor_nombre": mi_nombre,
        "emisor_rol": mi_rol,
        "receptor_usuario": receptor_id,
        "receptor_nombre": receptor_nombre,
        "receptor_rol": receptor_rol,
        "mensaje": texto,
        "fecha": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "hora_corta": ahora.strftime("%I:%M %p"),
        "fecha_completa": ahora.strftime("%I:%M %p • %d/%m/%Y"),
        "timestamp": int(time.time()),
        "leido": False,
        "eliminado": False,
        "respuesta_a": info_respuesta
    }"""

if old_nuevo_msg in content:
    content = content.replace(old_nuevo_msg, new_nuevo_msg)
    print("OK: Replaced old_nuevo_msg")
else:
    print("WARN: old_nuevo_msg not found directly, trying CRLF")
    content = content.replace(old_nuevo_msg.replace('\n', '\r\n'), new_nuevo_msg.replace('\n', '\r\n'))

# 3. Add endpoints for eliminar and detalles
nuevas_rutas = """
@chat_bp.route('/api/chat/eliminar_mensaje', methods=['POST'])
def chat_eliminar_mensaje():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
        
    data = request.json or {}
    mensaje_id = data.get('mensaje_id')
    if not mensaje_id:
        return jsonify({"status": "error", "message": "Falta el ID del mensaje"}), 400
        
    mi_usuario = session['usuario'].get('usuario')
    mi_rol = obtener_rol_chat(session['usuario'])
    
    chat_db = leer_json_chat(CHAT_FILE)
    mensajes = chat_db.get('mensajes', [])
    
    encontrado = None
    for m in mensajes:
        if m.get('id') == mensaje_id:
            encontrado = m
            break
            
    if not encontrado:
        return jsonify({"status": "error", "message": "Mensaje no encontrado"}), 404
        
    # Solo el emisor o Jefatura/Supervisor tienen permiso para eliminar
    es_emisor = (encontrado.get('emisor_usuario') == mi_usuario)
    es_admin_jefatura = (mi_rol in ['Jefatura', 'Supervisor'])
    
    if not es_emisor and not es_admin_jefatura:
        return jsonify({"status": "error", "message": "No tienes permiso para eliminar este mensaje"}), 403
        
    ahora_elim = datetime.now()
    encontrado['eliminado'] = True
    encontrado['fecha_eliminado'] = ahora_elim.strftime("%Y-%m-%d %H:%M:%S")
    encontrado['fecha_eliminado_completa'] = ahora_elim.strftime("%I:%M:%S %p • %d/%m/%Y")
    encontrado['eliminado_por'] = mi_usuario
    encontrado['mensaje'] = "Este mensaje fue eliminado"
    
    escribir_json_chat(CHAT_FILE, chat_db)
    
    return jsonify({
        "status": "success",
        "message": "Mensaje eliminado correctamente",
        "mensaje_id": mensaje_id
    })

@chat_bp.route('/api/chat/mensaje_detalles/<mensaje_id>', methods=['GET'])
def chat_mensaje_detalles(mensaje_id):
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
        
    mi_usuario = session['usuario'].get('usuario')
    chat_db = leer_json_chat(CHAT_FILE)
    mensajes = chat_db.get('mensajes', [])
    
    encontrado = next((m for m in mensajes if m.get('id') == mensaje_id), None)
    if not encontrado:
        return jsonify({"status": "error", "message": "Mensaje no encontrado"}), 404
        
    # Verificar que el usuario tenga relación con el mensaje o sea de administración
    if (encontrado.get('emisor_usuario') != mi_usuario and 
        encontrado.get('receptor_usuario') != mi_usuario and 
        session['usuario'].get('rol') != 'administracion'):
        return jsonify({"status": "error", "message": "No autorizado para ver este mensaje"}), 403
        
    return jsonify({
        "status": "success",
        "detalles": encontrado
    })
"""

content = content.rstrip() + "\n" + nuevas_rutas

with open('rutas_chat.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("rutas_chat.py actualizado exitosamente.")

