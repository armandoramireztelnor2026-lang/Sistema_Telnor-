# -*- coding: utf-8 -*-
import sys

with open('rutas_chat.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_imp = "from datetime import datetime"
new_imp = "from datetime import datetime, timedelta"
if old_imp in code:
    code = code.replace(old_imp, new_imp, 1)

# 2. Add presence setup right after CHAT_FILE and USUARIOS_FILE
old_files = """CHAT_FILE = 'chat_mensajes.json'
USUARIOS_FILE = 'usuarios.json'"""

new_files = """CHAT_FILE = 'chat_mensajes.json'
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
"""

if old_files in code:
    code = code.replace(old_files, new_files, 1)
else:
    code = code.replace(old_files.replace('\n', '\r\n'), new_files.replace('\n', '\r\n'), 1)

# 3. Update chat_contactos to register activity and include presencia
old_contactos_append = """        contactos.append({
            "usuario": u_id,
            "nombre": obtener_nombre_chat(u),
            "rol": u_rol,
            "foto_ruta": foto_url,
            "cope": dp.get('cope') or dp.get('ciudad') or '',
            "ultimo_mensaje": ultimo_msg.get('mensaje') if ultimo_msg else '',
            "fecha_ultimo_mensaje": ultimo_msg.get('fecha') if ultimo_msg else '',
            "hora_corta": ultimo_msg.get('hora_corta', '') if ultimo_msg else '',
            "timestamp_ultimo": ultimo_msg.get('timestamp', 0) if ultimo_msg else 0,
            "no_leidos": no_leidos
        })"""

new_contactos_append = """        pres = obtener_estado_presencia(u_id)
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
        })"""

if old_contactos_append in code:
    code = code.replace(old_contactos_append, new_contactos_append, 1)
else:
    code = code.replace(old_contactos_append.replace('\n', '\r\n'), new_contactos_append.replace('\n', '\r\n'), 1)

# In chat_contactos register activity for mi_usuario
old_contactos_reg = "mi_usuario = session['usuario'].get('usuario')"
new_contactos_reg = """mi_usuario = session['usuario'].get('usuario')
    registrar_actividad(mi_usuario)"""
code = code.replace(old_contactos_reg, new_contactos_reg, 1)

# 4. In chat_conversacion include presencia in contacto
old_conv_return = """    return jsonify({
        "status": "success",
        "mi_usuario": mi_usuario,
        "contacto": {
            "usuario": contacto_id,
            "nombre": obtener_nombre_chat(contacto_obj),
            "rol": contacto_rol,
            "foto_ruta": foto_url,
            "cope": dp.get('cope') or dp.get('ciudad') or ''
        },
        "mensajes": conversacion
    })"""

new_conv_return = """    pres_contacto = obtener_estado_presencia(contacto_id)
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
    })"""

if old_conv_return in code:
    code = code.replace(old_conv_return, new_conv_return, 1)
else:
    code = code.replace(old_conv_return.replace('\n', '\r\n'), new_conv_return.replace('\n', '\r\n'), 1)

# In chat_conversacion register activity
old_conv_reg = "def chat_conversacion(contacto_id):"
new_conv_reg = """def chat_conversacion(contacto_id):
    if 'usuario' in session:
        registrar_actividad(session['usuario'].get('usuario'))"""
if old_conv_reg in code:
    code = code.replace(old_conv_reg, new_conv_reg, 1)

# 5. In chat_no_leidos register activity and return contacto_presencia
old_no_leidos_return = """    return jsonify({
        "status": "success",
        "total_no_leidos": total,
        "por_contacto": por_contacto
    })"""

new_no_leidos_return = """    registrar_actividad(mi_usuario)
    contacto_activo = request.args.get('contacto_activo')
    contacto_presencia = None
    if contacto_activo:
        contacto_presencia = obtener_estado_presencia(contacto_activo)

    return jsonify({
        "status": "success",
        "total_no_leidos": total,
        "por_contacto": por_contacto,
        "contacto_presencia": contacto_presencia
    })"""

if old_no_leidos_return in code:
    code = code.replace(old_no_leidos_return, new_no_leidos_return, 1)
else:
    code = code.replace(old_no_leidos_return.replace('\n', '\r\n'), new_no_leidos_return.replace('\n', '\r\n'), 1)

# 6. Add dedicated endpoint /api/chat/presencia/<usuario_id>
nuevas_rutas_pres = """
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
"""

code = code.rstrip() + "\n" + nuevas_rutas_pres

with open('rutas_chat.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_chat.py actualizado con funciones de presencia en tiempo real.")

