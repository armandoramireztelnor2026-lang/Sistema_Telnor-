# =========================================================
# ARCHIVO: app.py
# PROPÓSITO: Backend principal y Coordinador de Módulos
# =========================================================
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import json
import os
import shutil
import random
import string
import datetime
import webbrowser
from threading import Timer

from rutas_facturas import facturas_bp
from rutas_reportes import reportes_bp  
from rutas_seccion_reportes import seccion_reportes_bp

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura_2026"

app.register_blueprint(facturas_bp)
app.register_blueprint(reportes_bp)     
app.register_blueprint(seccion_reportes_bp)     

CARPETAS = {
    "temporal": "static/registros_confirmar",
    "proveedores": "static/logos_proveedores",
    "administracion": "static/foto_administracion",
    "corporativos": "static/foto_corporativos",
    "facturas": "static/facturas_archivos" 
}

USUARIOS_PRUEBA = [
    {
        "usuario": "admin_universal", 
        "password": "password123", 
        "rol": "administracion", 
        "datos_perfil": {
            "nombres": "Admin", 
            "apellido_paterno": "Universal", 
            "area": "Dirección General",
            "subrol": "Jefatura",
            "ciudad": "Mexicali",
            "foto_ruta": "imagen_universal.jpg"
        }
    }
]

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)

def escribir_json(archivo, data):
    with open(archivo, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def inicializar_sistema():
    if not os.path.exists('usuarios.json'): escribir_json('usuarios.json', {"usuarios": []})
    if not os.path.exists('pendientes.json'): escribir_json('pendientes.json', {"pendientes": []})
    if not os.path.exists('facturas.json'): escribir_json('facturas.json', {"facturas": []}) 
    if not os.path.exists('reportes.json'): escribir_json('reportes.json', {"reportes": []}) 
    for carpeta in CARPETAS.values():
        os.makedirs(carpeta, exist_ok=True)

inicializar_sistema()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/reportar')
def reportar(): return render_template('reporte.html') 

@app.route('/proveedores')
def proveedores(): 
    if 'usuario' not in session or session['usuario']['rol'] != 'proveedores': return redirect(url_for('index'))
    return render_template('proveedores.html', usuario=session['usuario'])

@app.route('/administracion')
def administracion(): 
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion': return redirect(url_for('index'))
    return render_template('administracion.html', usuario=session['usuario'])

@app.route('/corporativos')
def corporativos(): 
    if 'usuario' not in session or session['usuario']['rol'] != 'corporativos': return redirect(url_for('index'))
    return render_template('corporativos.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get('usuario')
    password = data.get('password')
    rol_seleccionado = data.get('rol')
    for u in USUARIOS_PRUEBA:
        if u['usuario'] == usuario and u['password'] == password and u['rol'] == rol_seleccionado: 
            session['usuario'] = u 
            return jsonify({"status": "success", "redirect": f"/{rol_seleccionado}"})
    usuarios_data = leer_json('usuarios.json')
    for u in usuarios_data.get('usuarios', []):
        if u['usuario'] == usuario and u['password'] == password and u['rol'] == rol_seleccionado: 
            session['usuario'] = u 
            return jsonify({"status": "success", "redirect": f"/{rol_seleccionado}"})
    return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos."})

@app.route('/registro', methods=['POST'])
def registro():
    rol = request.form.get('rol')
    foto = request.files.get('foto')
    nuevo_pendiente = {"rol": rol}
    nuevo_pendiente['cope'] = request.form.get('cope', 'No especificado')
    for key, value in request.form.items():
        if key != 'rol' and key != 'cope': 
            nuevo_pendiente[key] = value
    if foto and foto.filename:
        filename = secure_filename(foto.filename)
        nombre_unico = f"temp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        foto.save(os.path.join(CARPETAS["temporal"], nombre_unico))
        nuevo_pendiente['foto_ruta'] = nombre_unico
    pendientes_data = leer_json('pendientes.json')
    pendientes_data.setdefault('pendientes', []).append(nuevo_pendiente)
    escribir_json('pendientes.json', pendientes_data)
    return jsonify({"status": "success", "message": "Registro enviado para revisión."})


# --- RUTAS DE APROBACIÓN (PROTEGIDAS PARA JEFATURA) ---
@app.route('/api/pendientes', methods=['GET'])
def get_pendientes(): 
    # Si entra un Supervisor a esta ruta, le regresamos una lista vacía para que no vea nada.
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"pendientes": []})
    return jsonify(leer_json('pendientes.json'))

@app.route('/api/accesos', methods=['GET'])
def get_accesos(): return jsonify(leer_json('usuarios.json'))

@app.route('/api/aprobar', methods=['POST'])
def aprobar_usuario():
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura puede aprobar usuarios."})
        
    id_pendiente = request.json.get('identificador') 
    pendientes_data = leer_json('pendientes.json')
    usuarios_data = leer_json('usuarios.json')
    usuario_encontrado, nuevos_pendientes = None, []
    for p in pendientes_data.get('pendientes', []):
        if p.get('correo') == id_pendiente or p.get('num_empleado') == id_pendiente: usuario_encontrado = p
        else: nuevos_pendientes.append(p)
    if usuario_encontrado:
        rol = usuario_encontrado['rol']
        año_actual = datetime.datetime.now().year
        if rol == 'proveedores': usuario_generado = f"{usuario_encontrado['nombre_proveedor'].replace(' ', '')}-RUMN-{año_actual}-prov"
        elif rol == 'administracion': usuario_generado = f"{usuario_encontrado['nombres'].replace(' ', '')}_{usuario_encontrado['apellido_paterno']}-RUMN-{año_actual}-admin"
        else: usuario_generado = f"{usuario_encontrado['nombres'].replace(' ', '')}_{usuario_encontrado['apellido_paterno']}-RUMN-{año_actual}-corp"
        password_generado = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
        nombre_foto = usuario_encontrado.get('foto_ruta')
        if nombre_foto:
            ruta_origen = os.path.join(CARPETAS["temporal"], nombre_foto)
            if os.path.exists(ruta_origen): shutil.move(ruta_origen, os.path.join(CARPETAS[rol], nombre_foto))
        usuarios_data.setdefault('usuarios', []).append({"usuario": usuario_generado, "password": password_generado, "rol": rol, "datos_perfil": usuario_encontrado})
        pendientes_data['pendientes'] = nuevos_pendientes
        escribir_json('usuarios.json', usuarios_data)
        escribir_json('pendientes.json', pendientes_data)
        return jsonify({"status": "success", "message": "Usuario aprobado y credenciales generadas."})
    return jsonify({"status": "error", "message": "Solicitud no encontrada."})

@app.route('/api/rechazar', methods=['POST'])
def rechazar_usuario():
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura puede rechazar usuarios."})
        
    id_pendiente = request.json.get('identificador') 
    pendientes_data = leer_json('pendientes.json')
    usuario_encontrado, nuevos_pendientes = None, []
    for p in pendientes_data.get('pendientes', []):
        if p.get('correo') == id_pendiente or p.get('num_empleado') == id_pendiente: usuario_encontrado = p
        else: nuevos_pendientes.append(p)
    if usuario_encontrado:
        nombre_foto = usuario_encontrado.get('foto_ruta')
        if nombre_foto:
            ruta_foto = os.path.join(CARPETAS["temporal"], nombre_foto)
            if os.path.exists(ruta_foto): os.remove(ruta_foto)
        pendientes_data['pendientes'] = nuevos_pendientes
        escribir_json('pendientes.json', pendientes_data)
        return jsonify({"status": "success", "message": "Solicitud rechazada y eliminada del sistema."})
    return jsonify({"status": "error", "message": "Solicitud no encontrada."})


# --- RUTAS DE CRUD (PROTEGIDAS PARA JEFATURA) ---
@app.route('/api/renovar_password', methods=['POST'])
def renovar_password():
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura puede renovar contraseñas."})
        
    usuario_id = request.json.get('usuario')
    usuarios_data = leer_json('usuarios.json')
    for u in usuarios_data.get('usuarios', []):
        if u['usuario'] == usuario_id:
            nueva_pass = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            u['password'] = nueva_pass
            escribir_json('usuarios.json', usuarios_data)
            return jsonify({"status": "success", "message": f"Contraseña renovada correctamente.\nNueva clave: {nueva_pass}"})
    return jsonify({"status": "error", "message": "Usuario no encontrado."})

@app.route('/api/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura puede eliminar cuentas."})
        
    usuario_id = request.json.get('usuario')
    usuarios_data = leer_json('usuarios.json')
    nuevos_usuarios = []
    eliminado = False
    for u in usuarios_data.get('usuarios', []):
        if u['usuario'] == usuario_id:
            eliminado = True
            rol = u['rol']
            foto = u['datos_perfil'].get('foto_ruta')
            if foto:
                ruta_foto = os.path.join(CARPETAS[rol], foto)
                if os.path.exists(ruta_foto): os.remove(ruta_foto)
        else:
            nuevos_usuarios.append(u)
    if eliminado:
        usuarios_data['usuarios'] = nuevos_usuarios
        escribir_json('usuarios.json', usuarios_data)
        return jsonify({"status": "success", "message": "Usuario y archivos eliminados completamente."})
    return jsonify({"status": "error", "message": "Usuario no encontrado."})

@app.route('/api/editar_usuario', methods=['POST'])
def editar_usuario():
    if session.get('usuario', {}).get('datos_perfil', {}).get('subrol') == 'Supervisor':
        return jsonify({"status": "error", "message": "Acceso denegado. Solo Jefatura puede editar cuentas de usuario."})
        
    usuario_id = request.form.get('usuario_id')
    usuarios_data = leer_json('usuarios.json')
    for u in usuarios_data.get('usuarios', []):
        if u['usuario'] == usuario_id:
            rol = u['rol']
            foto_nueva = request.files.get('foto')
            u['datos_perfil']['cope'] = request.form.get('cope', 'No especificado')
            for key, value in request.form.items():
                if key not in ['usuario_id', 'rol', 'cope']: 
                    u['datos_perfil'][key] = value
            if foto_nueva and foto_nueva.filename:
                foto_vieja = u['datos_perfil'].get('foto_ruta')
                if foto_vieja:
                    ruta_vieja = os.path.join(CARPETAS[rol], foto_vieja)
                    if os.path.exists(ruta_vieja): os.remove(ruta_vieja)
                filename = secure_filename(foto_nueva.filename)
                nombre_unico = f"edit_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                foto_nueva.save(os.path.join(CARPETAS[rol], nombre_unico))
                u['datos_perfil']['foto_ruta'] = nombre_unico
            escribir_json('usuarios.json', usuarios_data)
            return jsonify({"status": "success", "message": "Perfil actualizado correctamente."})
    return jsonify({"status": "error", "message": "No se pudo actualizar."})


@app.route('/api/facturas/validar_codigo', methods=['POST'])
def validar_codigo():
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion':
        return jsonify({"status": "error", "message": "No tienes permisos para liberar vehículos."})
    req_data = request.json
    id_factura = req_data.get('id_factura')
    codigo_ingresado = req_data.get('codigo')
    data = leer_json('facturas.json')
    for f in data.get('facturas', []):
        if str(f['id']) == str(id_factura):
            codigo_real = f.get('codigo_liberacion')
            if not codigo_real:
                return jsonify({"status": "error", "message": "Esta factura aún no tiene un código de liberación activo."})
            if str(codigo_real) == str(codigo_ingresado):
                f['entregado'] = "Sí"
                escribir_json('facturas.json', data)
                return jsonify({"status": "success", "message": "Match perfecto."})
            else:
                return jsonify({"status": "error", "message": "El código es incorrecto. Pide al chofer que revise su correo nuevamente."})
    return jsonify({"status": "error", "message": "No se encontró la factura en el sistema."})

def abrir_navegador(): webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    Timer(1, abrir_navegador).start()
    app.run(debug=True, use_reloader=False)