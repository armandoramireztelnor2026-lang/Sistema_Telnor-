# -*- coding: utf-8 -*-
import os
import json
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session

chat_bp = Blueprint('chat_bp', __name__)

CHAT_FILE = 'chat_mensajes.json'
USUARIOS_FILE = 'usuarios.json'
PRESENCIA_FILE = 'chat_presencia.json'

# Cache en memoria de presencia: { usuario_id: { "timestamp": int, "fecha": str } }
_presencia_cache = None
_ultimo_guardado_presencia = 0

def _cargar_presencia():
    global _presencia_cache
    if _presencia_cache is None:
        _presencia_cache = leer_json_chat(PRESENCIA_FILE)
    return _presencia_cache

def registrar_actividad(usuario_id):
    global _ultimo_guardado_presencia
    if not usuario_id:
        return
    cache = _cargar_presencia()
    ahora = time.time()
    cache[usuario_id] = {
        "timestamp": int(ahora),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Persistir a disco maximo cada 10 segundos para optimizar I/O
    if ahora - _ultimo_guardado_presencia > 10:
        escribir_json_chat(PRESENCIA_FILE, cache)
        _ultimo_guardado_presencia = ahora

def obtener_estado_presencia(usuario_id):
    if not usuario_id:
        return {"en_linea": False, "texto": "Desconectado", "timestamp": None}
    cache = _cargar_presencia()
    info = cache.get(usuario_id)
    if not info:
        return {"en_linea": False, "texto": "Desconectado", "timestamp": None}
        
    ts = info.get("timestamp", 0)
    ahora = int(time.time())
    diff = max(0, ahora - ts)

    # Si se detectó actividad en los últimos 90 segundos: En línea
    if diff <= 90:
        return {"en_linea": True, "texto": "En línea", "timestamp": ts}
        
    minutos = diff // 60
    if minutos < 60:
        texto = "En línea hace 1 min" if minutos <= 1 else f"En línea hace {minutos} min"
        return {"en_linea": False, "texto": texto, "timestamp": ts}
        
    horas = diff // 3600
    d_ts = datetime.fromtimestamp(ts)
    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)
    hora_str = d_ts.strftime("%I:%M %p")
    
    if d_ts.date() == hoy:
        return {"en_linea": False, "texto": f"Últ. vez hoy a las {hora_str}", "timestamp": ts}
    elif d_ts.date() == ayer:
        return {"en_linea": False, "texto": f"Últ. vez ayer a las {hora_str}", "timestamp": ts}
    else:
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        mes = meses[d_ts.month - 1]
        return {"en_linea": False, "texto": f"Últ. vez el {d_ts.day} {mes} {d_ts.year} a las {hora_str}", "timestamp": ts}


def leer_json_chat(archivo):
    if not os.path.exists(archivo):
        return {}
    with open(archivo, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def escribir_json_chat(archivo, data):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def inicializar_chat():
    if not os.path.exists(CHAT_FILE):
        escribir_json_chat(CHAT_FILE, {"mensajes": []})

inicializar_chat()

def obtener_rol_chat(usuario_obj):
    if not usuario_obj:
        return None
    rol = usuario_obj.get('rol', '')
    if rol == 'proveedores':
        return 'Taller'
    if rol == 'corporativos':
        return 'Corporativos'
    if rol == 'administracion':
        subrol = usuario_obj.get('datos_perfil', {}).get('subrol', '')
        if subrol in ['Supervisor', 'Administrador', 'Jefatura']:
            return subrol
        return 'Administrador'
    return rol

def obtener_nombre_chat(usuario_obj):
    dp = usuario_obj.get('datos_perfil', {})
    if usuario_obj.get('rol') == 'proveedores':
        return dp.get('nombre_proveedor') or dp.get('encargado') or usuario_obj.get('usuario')
    nombres = (dp.get('nombres') or '').strip()
    apellido = (dp.get('apellido_paterno') or '').strip()
    if nombres or apellido:
        return f"{nombres} {apellido}".strip()
    return usuario_obj.get('usuario', 'Usuario')

# Matriz estricta de permisos de mensajeria solicitada por el usuario:
MATRIZ_CHAT_PERMISOS = {
    'Taller': ['Supervisor'],
    'Supervisor': ['Supervisor', 'Taller', 'Administrador', 'Jefatura', 'Corporativos'],
    'Corporativos': ['Supervisor'],
    'Jefatura': ['Taller', 'Supervisor', 'Administrador', 'Corporativos', 'Jefatura'],
    'Administrador': ['Supervisor', 'Jefatura']
}

@chat_bp.route('/api/chat/mi_perfil', methods=['GET'])
def chat_mi_perfil():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    u = session['usuario']
    rol_chat = obtener_rol_chat(u)
    return jsonify({
        "status": "success",
        "usuario": u.get('usuario'),
        "nombre": obtener_nombre_chat(u),
        "rol": rol_chat,
        "permitidos": MATRIZ_CHAT_PERMISOS.get(rol_chat, [])
    })

@chat_bp.route('/api/chat/contactos', methods=['GET'])
def chat_contactos():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    mi_usuario = session['usuario'].get('usuario')
    registrar_actividad(mi_usuario)
    mi_rol = obtener_rol_chat(session['usuario'])
    roles_permitidos = MATRIZ_CHAT_PERMISOS.get(mi_rol, [])
    
    usuarios_data = leer_json_chat(USUARIOS_FILE).get('usuarios', [])
    mensajes_data = leer_json_chat(CHAT_FILE).get('mensajes', [])
    
    contactos = []
    for u in usuarios_data:
        u_id = u.get('usuario')
        if u_id == mi_usuario:
            continue
        u_rol = obtener_rol_chat(u)
        if u_rol not in roles_permitidos:
            continue
        
        # Buscar ultimo mensaje entre mi_usuario y este contacto
        msgs_con_este = [
            m for m in mensajes_data
            if (m.get('emisor_usuario') == mi_usuario and m.get('receptor_usuario') == u_id)
            or (m.get('emisor_usuario') == u_id and m.get('receptor_usuario') == mi_usuario)
        ]
        msgs_con_este.sort(key=lambda x: x.get('timestamp', 0))
        ultimo_msg = msgs_con_este[-1] if msgs_con_este else None
        
        # Conteo de no leidos enviados por este contacto hacia mi
        no_leidos = sum(
            1 for m in msgs_con_este
            if m.get('emisor_usuario') == u_id and m.get('receptor_usuario') == mi_usuario and not m.get('leido', False)
        )
        
        dp = u.get('datos_perfil', {})
        foto = dp.get('foto_ruta', '')
        if foto:
            if u.get('rol') == 'proveedores':
                foto_url = f"/static/logos_proveedores/{foto}" if not foto.startswith('/') else foto
            else:
                foto_url = f"/static/fotos_perfil/{foto}" if not foto.startswith('/') else foto
        else:
            foto_url = ''
            
        pres = obtener_estado_presencia(u_id)
        contactos.append({
            "usuario": u_id,
            "nombre": obtener_nombre_chat(u),
            "rol": u_rol,
            "foto_ruta": foto_url,
            "cope": dp.get('cope') or dp.get('ciudad') or '',
            "ultimo_mensaje": ultimo_msg.get('mensaje') if ultimo_msg else '',
            "fecha_ultimo_mensaje": ultimo_msg.get('fecha') if ultimo_msg else '',
            "hora_corta": ultimo_msg.get('hora_corta', '') if ultimo_msg else '',
            "timestamp_ultimo": ultimo_msg.get('timestamp', 0) if ultimo_msg else 0,
            "no_leidos": no_leidos,
            "en_linea": pres.get("en_linea", False),
            "estado_presencia": pres.get("texto", "Desconectado"),
            "ultimo_acceso": pres.get("timestamp")
        })
        
    # Ordenar contactos: primero los que tienen mensajes no leidos, luego por fecha de ultimo mensaje
    contactos.sort(key=lambda x: (x['no_leidos'] > 0, x['timestamp_ultimo']), reverse=True)
    
    return jsonify({
        "status": "success",
        "mi_rol": mi_rol,
        "mi_usuario": mi_usuario,
        "contactos": contactos
    })

@chat_bp.route('/api/chat/conversacion/<path:contacto_id>', methods=['GET'])
def chat_conversacion(contacto_id):
    if 'usuario' in session:
        registrar_actividad(session['usuario'].get('usuario'))
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    mi_usuario = session['usuario'].get('usuario')
    mi_rol = obtener_rol_chat(session['usuario'])
    
    usuarios_data = leer_json_chat(USUARIOS_FILE).get('usuarios', [])
    contacto_obj = next((u for u in usuarios_data if u.get('usuario') == contacto_id), None)
    if not contacto_obj:
        return jsonify({"status": "error", "message": "Contacto no encontrado"}), 404
        
    contacto_rol = obtener_rol_chat(contacto_obj)
    
    # Validar si este usuario tiene permiso para ver/escribir segun la matriz
    roles_permitidos = MATRIZ_CHAT_PERMISOS.get(mi_rol, [])
    if contacto_rol not in roles_permitidos:
        return jsonify({"status": "error", "message": f"Tu rol '{mi_rol}' no tiene permisos para chatear con '{contacto_rol}'"}), 403

    chat_db = leer_json_chat(CHAT_FILE)
    mensajes = chat_db.get('mensajes', [])
    
    hubo_cambios = False
    conversacion = []
    for m in mensajes:
        es_de_este_chat = (
            (m.get('emisor_usuario') == mi_usuario and m.get('receptor_usuario') == contacto_id) or
            (m.get('emisor_usuario') == contacto_id and m.get('receptor_usuario') == mi_usuario)
        )
        if es_de_este_chat:
            # Marcar como leido si era para mi y estaba no leido
            if m.get('receptor_usuario') == mi_usuario and not m.get('leido', False):
                m['leido'] = True
                ahora_leido = datetime.now()
                m['fecha_leido'] = ahora_leido.strftime("%Y-%m-%d %H:%M:%S")
                m['fecha_leido_completa'] = ahora_leido.strftime("%I:%M:%S %p • %d/%m/%Y")
                hubo_cambios = True
            conversacion.append(m)
            
    if hubo_cambios:
        escribir_json_chat(CHAT_FILE, chat_db)
        
    conversacion.sort(key=lambda x: x.get('timestamp', 0))
    
    dp = contacto_obj.get('datos_perfil', {})
    foto = dp.get('foto_ruta', '')
    if foto:
        if contacto_obj.get('rol') == 'proveedores':
            foto_url = f"/static/logos_proveedores/{foto}" if not foto.startswith('/') else foto
        else:
            foto_url = f"/static/fotos_perfil/{foto}" if not foto.startswith('/') else foto
    else:
        foto_url = ''
        
    pres_contacto = obtener_estado_presencia(contacto_id)
    return jsonify({
        "status": "success",
        "mi_usuario": mi_usuario,
        "contacto": {
            "usuario": contacto_id,
            "nombre": obtener_nombre_chat(contacto_obj),
            "rol": contacto_rol,
            "foto_ruta": foto_url,
            "cope": dp.get('cope') or dp.get('ciudad') or '',
            "en_linea": pres_contacto.get("en_linea", False),
            "estado_presencia": pres_contacto.get("texto", "Desconectado")
        },
        "mensajes": conversacion
    })

@chat_bp.route('/api/chat/enviar', methods=['POST'])
def chat_enviar():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
        
    data = request.json or {}
    receptor_id = (data.get('receptor_usuario') or '').strip()
    texto = (data.get('mensaje') or '').strip()
    
    if not receptor_id:
        return jsonify({"status": "error", "message": "Falta el destinatario"}), 400
    if not texto:
        return jsonify({"status": "error", "message": "El mensaje no puede estar vacío"}), 400
        
    mi_usuario = session['usuario'].get('usuario')
    mi_nombre = obtener_nombre_chat(session['usuario'])
    mi_rol = obtener_rol_chat(session['usuario'])
    
    usuarios_data = leer_json_chat(USUARIOS_FILE).get('usuarios', [])
    receptor_obj = next((u for u in usuarios_data if u.get('usuario') == receptor_id), None)
    if not receptor_obj:
        return jsonify({"status": "error", "message": "Destinatario no existe"}), 404
        
    receptor_rol = obtener_rol_chat(receptor_obj)
    receptor_nombre = obtener_nombre_chat(receptor_obj)
    
    # Validacion estricta de la matriz de permisos
    roles_permitidos = MATRIZ_CHAT_PERMISOS.get(mi_rol, [])
    if receptor_rol not in roles_permitidos:
        return jsonify({
            "status": "error",
            "message": f"El rol {mi_rol} no tiene autorización para enviar mensajes a {receptor_rol}."
        }), 403

    respuesta_a = data.get('respuesta_a')
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
    }
    
    chat_db = leer_json_chat(CHAT_FILE)
    if 'mensajes' not in chat_db:
        chat_db['mensajes'] = []
    chat_db['mensajes'].append(nuevo_mensaje)
    escribir_json_chat(CHAT_FILE, chat_db)
    
    return jsonify({
        "status": "success",
        "mensaje": nuevo_mensaje
    })

@chat_bp.route('/api/chat/no_leidos', methods=['GET'])
def chat_no_leidos():
    if 'usuario' not in session:
        return jsonify({"status": "success", "total_no_leidos": 0, "por_contacto": {}})
        
    mi_usuario = session['usuario'].get('usuario')
    mensajes = leer_json_chat(CHAT_FILE).get('mensajes', [])
    
    por_contacto = {}
    total = 0
    for m in mensajes:
        if m.get('receptor_usuario') == mi_usuario and not m.get('leido', False):
            emisor = m.get('emisor_usuario')
            por_contacto[emisor] = por_contacto.get(emisor, 0) + 1
            total += 1
            
    registrar_actividad(mi_usuario)
    contacto_activo = request.args.get('contacto_activo')
    contacto_presencia = None
    if contacto_activo:
        contacto_presencia = obtener_estado_presencia(contacto_activo)

    return jsonify({
        "status": "success",
        "total_no_leidos": total,
        "por_contacto": por_contacto,
        "contacto_presencia": contacto_presencia
    })

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
        
    pres_emisor = obtener_estado_presencia(encontrado.get('emisor_usuario'))
    pres_receptor = obtener_estado_presencia(encontrado.get('receptor_usuario'))
    return jsonify({
        "status": "success",
        "detalles": encontrado,
        "emisor_presencia": pres_emisor,
        "receptor_presencia": pres_receptor
    })

@chat_bp.route('/api/chat/presencia/<usuario_id>', methods=['GET'])
def chat_presencia_usuario(usuario_id):
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    registrar_actividad(session['usuario'].get('usuario'))
    pres = obtener_estado_presencia(usuario_id)
    return jsonify({
        "status": "success",
        "usuario": usuario_id,
        "en_linea": pres.get("en_linea", False),
        "estado_presencia": pres.get("texto", "Desconectado")
    })
