# scratch/patch_rutas_chat.py
with open("rutas_chat.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Define obtener_foto_url and enhanced obtener_nombre_chat
old_func = '''def obtener_nombre_chat(usuario_obj):
    dp = usuario_obj.get('datos_perfil', {})
    if usuario_obj.get('rol') == 'proveedores':
        return dp.get('nombre_proveedor') or dp.get('encargado') or usuario_obj.get('usuario')
    nombres = (dp.get('nombres') or '').strip()
    apellido = (dp.get('apellido_paterno') or '').strip()
    if nombres or apellido:
        return f"{nombres} {apellido}".strip()
    return usuario_obj.get('usuario', 'Usuario')'''

new_func = '''def obtener_foto_url(usuario_obj):
    if not usuario_obj:
        return ''
    dp = usuario_obj.get('datos_perfil', {})
    foto = dp.get('foto_ruta', '')
    if not foto:
        return ''
    if foto.startswith('http://') or foto.startswith('https://') or foto.startswith('/'):
        return foto

    rol = usuario_obj.get('rol', '')
    carpetas_rol = {
        'proveedores': 'static/logos_proveedores',
        'administracion': 'static/foto_administracion',
        'corporativos': 'static/foto_corporativos'
    }

    # 1. Checar en la carpeta del rol correspondiente
    folder = carpetas_rol.get(rol)
    if folder and os.path.exists(os.path.join(folder, foto)):
        return f"/{folder}/{foto}"

    # 2. Buscar en todas las carpetas conocidas de fotos de perfil y logos
    for fld in ['static/foto_administracion', 'static/foto_corporativos', 'static/logos_proveedores', 'static/registros_confirmar']:
        if os.path.exists(os.path.join(fld, foto)):
            return f"/{fld}/{foto}"

    if folder:
        return f"/{folder}/{foto}"
    return f"/static/foto_administracion/{foto}"

def obtener_nombre_chat(usuario_obj):
    if not usuario_obj:
        return 'Usuario'
    dp = usuario_obj.get('datos_perfil', {})
    if usuario_obj.get('rol') == 'proveedores':
        return dp.get('nombre_proveedor') or dp.get('encargado') or usuario_obj.get('usuario')
    nombres = (dp.get('nombres') or '').strip()
    apellido_p = (dp.get('apellido_paterno') or '').strip()
    apellido_m = (dp.get('apellido_materno') or '').strip()
    if nombres or apellido_p or apellido_m:
        partes = [p for p in [nombres, apellido_p, apellido_m] if p]
        return " ".join(partes).strip()
    return usuario_obj.get('usuario', 'Usuario')'''

assert old_func in code, "old_func not found in rutas_chat.py"
code = code.replace(old_func, new_func, 1)
print("obtener_foto_url and obtener_nombre_chat replaced successfully")

# 2. Update chat_mi_perfil
old_mi_perfil = '''@chat_bp.route('/api/chat/mi_perfil', methods=['GET'])
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
    })'''

new_mi_perfil = '''@chat_bp.route('/api/chat/mi_perfil', methods=['GET'])
def chat_mi_perfil():
    if 'usuario' not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    uid = session['usuario'].get('usuario')
    usuarios_data = leer_json_chat(USUARIOS_FILE).get('usuarios', [])
    u_fresh = next((usr for usr in usuarios_data if usr.get('usuario') == uid), session['usuario'])
    
    rol_chat = obtener_rol_chat(u_fresh)
    foto_url = obtener_foto_url(u_fresh)
    nombre = obtener_nombre_chat(u_fresh)

    session['usuario'] = u_fresh
    session.modified = True

    return jsonify({
        "status": "success",
        "usuario": uid,
        "nombre": nombre,
        "rol": rol_chat,
        "foto_ruta": foto_url,
        "permitidos": MATRIZ_CHAT_PERMISOS.get(rol_chat, [])
    })'''

assert old_mi_perfil in code, "old_mi_perfil not found in rutas_chat.py"
code = code.replace(old_mi_perfil, new_mi_perfil, 1)
print("chat_mi_perfil replaced successfully")

# 3. Update chat_contactos foto_ruta resolution
old_contactos_foto = '''        dp = u.get('datos_perfil', {})
        foto = dp.get('foto_ruta', '')
        if foto:
            if u.get('rol') == 'proveedores':
                foto_url = f"/static/logos_proveedores/{foto}" if not foto.startswith('/') else foto
            else:
                foto_url = f"/static/fotos_perfil/{foto}" if not foto.startswith('/') else foto
        else:
            foto_url = ''
            
        pres = obtener_estado_presencia(u_id)'''

new_contactos_foto = '''        dp = u.get('datos_perfil', {})
        foto_url = obtener_foto_url(u)
        pres = obtener_estado_presencia(u_id)'''

assert old_contactos_foto in code, "old_contactos_foto not found in rutas_chat.py"
code = code.replace(old_contactos_foto, new_contactos_foto, 1)
print("chat_contactos foto replaced successfully")

# 4. Update chat_conversacion
old_conversacion_end = '''    conversacion.sort(key=lambda x: x.get('timestamp', 0))
    
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
    })'''

new_conversacion_end = '''    conversacion.sort(key=lambda x: x.get('timestamp', 0))
    
    # Mapeo de usuarios a datos actuales para enriquecer todos los mensajes en tiempo real
    usuarios_map = {}
    for usr in usuarios_data:
        usr_id = usr.get('usuario')
        if usr_id:
            usuarios_map[usr_id] = {
                "nombre": obtener_nombre_chat(usr),
                "rol": obtener_rol_chat(usr),
                "foto_ruta": obtener_foto_url(usr)
            }

    conversacion_enriquecida = []
    for m in conversacion:
        m_copy = dict(m)
        e_usr = m_copy.get('emisor_usuario')
        r_usr = m_copy.get('receptor_usuario')
        
        # Enriquecer con datos actualizados en tiempo real si el usuario editó nombre o foto
        if e_usr in usuarios_map:
            m_copy['emisor_nombre'] = usuarios_map[e_usr]['nombre']
            m_copy['emisor_rol'] = usuarios_map[e_usr]['rol']
            m_copy['emisor_foto'] = usuarios_map[e_usr]['foto_ruta']
        else:
            m_copy['emisor_foto'] = ''
            
        if r_usr in usuarios_map:
            m_copy['receptor_nombre'] = usuarios_map[r_usr]['nombre']
            m_copy['receptor_rol'] = usuarios_map[r_usr]['rol']
            m_copy['receptor_foto'] = usuarios_map[r_usr]['foto_ruta']
        else:
            m_copy['receptor_foto'] = ''

        if m_copy.get('respuesta_a') and isinstance(m_copy['respuesta_a'], dict):
            resp_emisor = m_copy['respuesta_a'].get('emisor_usuario')
            if resp_emisor and resp_emisor in usuarios_map:
                m_copy['respuesta_a']['emisor_nombre'] = usuarios_map[resp_emisor]['nombre']

        conversacion_enriquecida.append(m_copy)

    dp = contacto_obj.get('datos_perfil', {})
    pres_contacto = obtener_estado_presencia(contacto_id)
    return jsonify({
        "status": "success",
        "mi_usuario": mi_usuario,
        "contacto": {
            "usuario": contacto_id,
            "nombre": obtener_nombre_chat(contacto_obj),
            "rol": contacto_rol,
            "foto_ruta": obtener_foto_url(contacto_obj),
            "cope": dp.get('cope') or dp.get('ciudad') or '',
            "en_linea": pres_contacto.get("en_linea", False),
            "estado_presencia": pres_contacto.get("texto", "Desconectado")
        },
        "mensajes": conversacion_enriquecida
    })'''

assert old_conversacion_end in code, "old_conversacion_end not found in rutas_chat.py"
code = code.replace(old_conversacion_end, new_conversacion_end, 1)
print("chat_conversacion enriched successfully")

with open("rutas_chat.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Saved rutas_chat.py successfully!")

