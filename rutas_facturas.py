# =========================================================
# ARCHIVO: rutas_facturas.py
# =========================================================
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
import datetime
import re

from notificaciones import (
    generar_codigo_liberacion,
    enviar_correo_liberacion,
    enviar_correo_nueva_factura,
    enviar_correo_nueva_factura_corp,
    enviar_correo_confirmacion_factura,
    enviar_correo_factura_rechazada,
    enviar_correo_factura_fiscal_subida,
    enviar_correo_factura_fiscal_rechazada,
)

facturas_bp = Blueprint("facturas_bp", __name__)
CARPETA_FACTURAS = "static/facturas_archivos"

def leer_json(archivo):
    if not os.path.exists(archivo): return {"facturas": []}
    with open(archivo, "r", encoding="utf-8") as f: return json.load(f)

def escribir_json(archivo, data):
    with open(archivo, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def procesar_liberacion_si_aplica(f):
    if f.get("aprobado_admin") and f.get("aprobado_corp"):
        return "\nâœ… Orden aprobada. El taller ha sido autorizado para iniciar la reparaciÃ³n."
    return ""


@facturas_bp.route("/api/facturas/nueva", methods=["POST"])
def nueva_factura():
    if "usuario" not in session or session["usuario"]["rol"] != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"})

    proveedor = session["usuario"]["datos_perfil"]["nombre_proveedor"]
    unidad_sola = request.form.get("unidad")
    unidad = f"8090-{unidad_sola}"

    precio_str = request.form.get("precio", "0")
    precio_limpio = "".join(c for c in precio_str if c.isdigit() or c == ".")
    precio_float = float(precio_limpio)
    necesita_corp = precio_float >= 10001.0
    
    retro = request.form.get("retro", "")
    compania_asignada = "RUMN"
    import re
    match = re.search(r"\[TICKET:(.*?)\]", retro)
    if match:
        ticket_id = match.group(1).strip()
        rep_data = leer_json("reportes.json")
        for r in rep_data.get("reportes", []):
            if str(r.get("id")) == str(ticket_id):
                compania_asignada = r.get("compania", "RUMN")
                break

    nueva_factura = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "proveedor": proveedor,
        "unidad": unidad,
        "responsable": request.form.get("responsable"),
        "telefono": request.form.get("telefono"),
        "titulo": request.form.get("titulo"),
        "retro": retro,
        "diagnostico": request.form.get("diagnostico", ""),
        "trabajo_realizar": request.form.get("trabajo_realizar", ""),
        "mantenimiento": request.form.get("mantenimiento"),
        "precio": precio_float,
        "fecha": request.form.get("fecha"),
        "numero_orden": "",
        "compania": compania_asignada,
        "aprobado_admin": False,
        "aprobado_corp": not necesita_corp,
        "timestamp": datetime.datetime.now().isoformat(),
        "estado_custom": "",
        "fotos_cotizacion": [],
        "fotos_evidencia": [],
        "codigo_liberacion": "",
        "entregado": "No",
    }

    for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
        archivos = request.files.getlist(tipo)
        for archivo in archivos:
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                nombre_unico = f"{tipo}_{nueva_factura['id']}_{filename}"
                archivo.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                nueva_factura[tipo].append(nombre_unico)

    data = leer_json("facturas.json")
    data.setdefault("facturas", []).append(nueva_factura)
    escribir_json("facturas.json", data)

    usuarios_data = leer_json("usuarios.json")
    admins_data = []
    corps_data = []
    
    proveedor_ciudad = session["usuario"]["datos_perfil"].get("ciudad", "")

    for u in usuarios_data.get("usuarios", []):
        if u["rol"] == "administracion":
            subrol = u["datos_perfil"].get("subrol", "AdministraciÃ³n")
            ciudad_admin = u["datos_perfil"].get("ciudad", "")
            
            # Solo notificar a la Jefatura general o al Supervisor local
            if subrol == "Jefatura" or ciudad_admin == proveedor_ciudad:
                correo = u["datos_perfil"].get("correo")
                if correo:
                    nombre = f"{u['datos_perfil'].get('nombres', '')} {u['datos_perfil'].get('apellido_paterno', '')}".strip()
                    admins_data.append({"correo": correo, "nombre": nombre, "puesto": subrol})

        elif u["rol"] == "corporativos":
            correo = u["datos_perfil"].get("correo")
            if correo:
                nombre = f"{u['datos_perfil'].get('nombres', '')} {u['datos_perfil'].get('apellido_paterno', '')}".strip()
                corps_data.append({"correo": correo, "nombre": nombre})

    if admins_data: enviar_correo_nueva_factura(admins_data, proveedor, unidad_sola, precio_float)
    if necesita_corp and corps_data: enviar_correo_nueva_factura_corp(corps_data, proveedor, unidad_sola, precio_float)

    correo_proveedor = session["usuario"]["datos_perfil"].get("correo")
    if correo_proveedor and correo_proveedor.strip():
        enviar_correo_confirmacion_factura(correo_proveedor, proveedor, unidad_sola, precio_float)

    return jsonify({"status": "success", "message": "CotizaciÃ³n enviada correctamente a revisiÃ³n."})


@facturas_bp.route("/api/facturas/lista", methods=["GET"])
def listar_facturas():
    data = leer_json("facturas.json")
    facturas = data.get("facturas", [])
    facturas.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    if "usuario" in session:
        rol = session["usuario"]["rol"]
        if rol == "proveedores":
            proveedor_actual = session["usuario"]["datos_perfil"]["nombre_proveedor"]
            facturas = [f for f in facturas if f.get("proveedor") == proveedor_actual]
            
        elif rol == "corporativos":
            facturas = [f for f in facturas if float(f.get("precio", 0)) >= 10001.0]
            
        elif rol == "administracion":
            # --- FILTRO GEOGRÃFICO PARA SUPERVISORES ---
            subrol = session["usuario"]["datos_perfil"].get("subrol", "")
            if subrol == "Supervisor":
                mi_ciudad = session["usuario"]["datos_perfil"].get("ciudad", "")
                usuarios_data = leer_json("usuarios.json")
                
                # Primero, buscamos cÃ³mo se llaman todos los proveedores de la misma ciudad
                proveedores_locales = [u["datos_perfil"]["nombre_proveedor"] for u in usuarios_data.get("usuarios", []) if u["rol"] == "proveedores" and u["datos_perfil"].get("ciudad") == mi_ciudad]
                
                # Luego, solo le mostramos al Supervisor las facturas que vengan de esos proveedores locales
                facturas = [f for f in facturas if f.get("proveedor") in proveedores_locales]
                
    return jsonify({"facturas": facturas})


@facturas_bp.route("/api/facturas/confirmar_admin", methods=["POST"])
def confirmar_admin():
    factura_id = request.form.get("id")
    num_orden = request.form.get("numero_orden")
    numero_cotizacion = request.form.get("numero_cotizacion", "")
    
    pdf_cotizacion = request.files.get("pdf_cotizacion")
    nombre_pdf = ""
    if pdf_cotizacion and pdf_cotizacion.filename != '':
        carpeta_cotizaciones = os.path.join("static", "facturas_archivos")
        if not os.path.exists(carpeta_cotizaciones):
            os.makedirs(carpeta_cotizaciones)
        
        nombre_pdf = f"Cotizacion_{factura_id}_{secure_filename(pdf_cotizacion.filename)}"
        pdf_cotizacion.save(os.path.join(carpeta_cotizaciones, nombre_pdf))

    data = leer_json("facturas.json")
    
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            f["aprobado_admin"] = True
            f["numero_orden"] = num_orden
            f["numero_cotizacion_asignacion"] = numero_cotizacion
            if nombre_pdf:
                f["pdf_cotizacion_asignacion"] = nombre_pdf
            
            # TambiÃ©n lo copiamos al reporte original para que los PDFs que se imprimen desde el taller
            # puedan visualizar este dato si consultan el reporte original.
            reportes_data = leer_json("reportes.json")
            for r in reportes_data.get("reportes", []):
                if str(r.get("id")) == str(f.get("reporte_id")):
                    r["numero_cotizacion_asignacion"] = numero_cotizacion
                    if nombre_pdf:
                        r["pdf_cotizacion_asignacion"] = nombre_pdf
                    escribir_json("reportes.json", reportes_data)
                    break

            f["estado_custom"] = ""
            mensaje_extra = procesar_liberacion_si_aplica(f)
            escribir_json("facturas.json", data)
            return jsonify({"status": "success", "message": "Orden asignada y validada por AdministraciÃ³n." + mensaje_extra})
    return jsonify({"status": "error", "message": "Registro no encontrado."})


@facturas_bp.route("/api/facturas/confirmar_corp", methods=["POST"])
def confirmar_corp():
    factura_id = request.json.get("id")
    data = leer_json("facturas.json")
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            f["aprobado_corp"] = True
            f["estado_custom"] = ""
            mensaje_extra = procesar_liberacion_si_aplica(f)
            escribir_json("facturas.json", data)
            return jsonify({"status": "success", "message": "AutorizaciÃ³n financiera aprobada." + mensaje_extra})
    return jsonify({"status": "error", "message": "Registro no encontrado."})


@facturas_bp.route("/api/facturas/rechazar", methods=["POST"])
def rechazar_factura():
    factura_id = request.json.get("id")
    motivo = request.json.get("motivo", "Motivo no especificado por la administraciÃ³n.")
    
    data = leer_json("facturas.json")
    nuevas_facturas = []
    eliminada = False
    factura_a_eliminar = None
    
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            eliminada = True
            factura_a_eliminar = f
            for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
                for foto in f.get(tipo, []):
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
        else: nuevas_facturas.append(f)
            
    if eliminada and factura_a_eliminar:
        data["facturas"] = nuevas_facturas
        escribir_json("facturas.json", data)
        
        proveedor_nombre = factura_a_eliminar.get('proveedor', '')
        unidad_texto = str(factura_a_eliminar.get('unidad', '')).replace('8090-', '')
        usuarios_data = leer_json('usuarios.json')
        correo_prov = ""
        
        for u in usuarios_data.get('usuarios', []):
            if u['rol'] == 'proveedores' and u['datos_perfil'].get('nombre_proveedor') == proveedor_nombre:
                correo_prov = u['datos_perfil'].get('correo', '')
                break
                
        if correo_prov:
            enviar_correo_factura_rechazada(correo_prov, proveedor_nombre, unidad_texto, motivo)
            
        return jsonify({"status": "success", "message": "Registro eliminado y proveedor notificado."})
    return jsonify({"status": "error", "message": "Registro no encontrado."})


@facturas_bp.route("/api/facturas/editar", methods=["POST"])
def editar_factura():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})
    factura_id = request.form.get("id_factura")
    data = leer_json("facturas.json")
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            unidad_cruda = request.form.get("unidad")
            f["unidad"] = (unidad_cruda if unidad_cruda.startswith("8090-") else f"8090-{unidad_cruda}")
            f["responsable"] = request.form.get("responsable")
            f["telefono"] = request.form.get("telefono")
            f["fecha"] = request.form.get("fecha")
            f["titulo"] = request.form.get("titulo")
            f["retro"] = request.form.get("retro")
            f["diagnostico"] = request.form.get("diagnostico", "")
            f["trabajo_realizar"] = request.form.get("trabajo_realizar", "")
            f["mantenimiento"] = request.form.get("mantenimiento")
            f["numero_orden"] = request.form.get("numero_orden")
            precio_str = request.form.get("precio", "0")
            precio_limpio = "".join(c for c in precio_str if c.isdigit() or c == ".")
            precio_float = float(precio_limpio)
            f["precio"] = precio_float
            necesita_corp = precio_float >= 10001.0
            f["aprobado_admin"] = True
            if necesita_corp:
                f["aprobado_corp"] = False
                f["estado_custom"] = "Actualizada por sistema (Pend. Corp)"
            else:
                f["aprobado_corp"] = True
                f["estado_custom"] = "Actualizada por sistema"
            
            coti_guardadas = json.loads(request.form.get("cotizaciones_guardadas", "[]"))
            evi_guardadas = json.loads(request.form.get("evidencias_guardadas", "[]"))
            for foto in f.get("fotos_cotizacion", []):
                if foto not in coti_guardadas:
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
            for foto in f.get("fotos_evidencia", []):
                if foto not in evi_guardadas:
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
            f["fotos_cotizacion"] = coti_guardadas
            f["fotos_evidencia"] = evi_guardadas
            for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
                archivos = request.files.getlist(tipo + "_nuevas")
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        nombre_unico = f"{tipo}_{f['id']}_{datetime.datetime.now().strftime('%H%M%S')}_{filename}"
                        archivo.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                        f[tipo].append(nombre_unico)
            escribir_json("facturas.json", data)
            return jsonify({"status": "success", "message": "Datos actualizados correctamente."})
    return jsonify({"status": "error", "message": "Registro no encontrado."})


@facturas_bp.route('/api/facturas/marcar_lista', methods=['POST'])
def marcar_lista():
    if 'usuario' not in session or session['usuario']['rol'] != 'proveedores':
        return jsonify({"status": "error", "message": "No autorizado"})
    
    factura_id = request.json.get('id')
    data = leer_json('facturas.json')
    
    for f in data.get('facturas', []):
        if f['id'] == factura_id:
            if f.get('codigo_liberacion'):
                return jsonify({"status": "error", "message": "La unidad ya estaba marcada como lista."})
            
            codigo = generar_codigo_liberacion()
            f['codigo_liberacion'] = codigo
            f['entregado'] = "No"
            
            correo_chofer = ""
            nombre_chofer = "Operador no registrado"
            telefono_chofer = "No proporcionado"
            ticket_id = ""
            retro = f.get('retro', '')
            match = re.search(r'\[TICKET:(.*?)\]', retro)
            
            if match:
                ticket_id = match.group(1)
                reportes_data = leer_json('reportes.json')
                for r in reportes_data.get('reportes', []):
                    if str(r.get('id')) == ticket_id:
                        correo_chofer = r.get('email', '')
                        nombre_chofer = r.get('empleado', 'Operador no registrado')
                        telefono_chofer = r.get('celular', 'No proporcionado')
                        break
                        
            unidad_limpia = str(f.get('unidad', '')).replace('8090-', '')
            exito, msg_correo = enviar_correo_liberacion(correo_chofer, ticket_id or "N/A", unidad_limpia, codigo, nombre_chofer, telefono_chofer)
            
            escribir_json('facturas.json', data)
            return jsonify({"status": "success", "message": "Â¡Unidad marcada como lista! El PIN ha sido enviado al chofer."})
            
    return jsonify({"status": "error", "message": "Registro no encontrado."})

@facturas_bp.route('/api/facturas/subir_factura_final', methods=['POST'])
def subir_factura_final():
    if 'usuario' not in session or session['usuario']['rol'] != 'proveedores':
        return jsonify({"status": "error", "message": "No autorizado"})
        
    factura_id = request.form.get('id_factura')
    folio = request.form.get('folio')
    archivo_pdf = request.files.get('pdf_factura')
    
    if not archivo_pdf or not archivo_pdf.filename.endswith('.pdf'):
        return jsonify({"status": "error", "message": "Debe subir un archivo en formato PDF vÃ¡lido."})
        
    data = leer_json('facturas.json')
    for f in data.get('facturas', []):
        if f['id'] == factura_id:
            filename = secure_filename(archivo_pdf.filename)
            nombre_unico = f"FACTURA_FINAL_{f['id']}_{filename}"
            archivo_pdf.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
            
            f['factura_folio'] = folio
            f['factura_pdf'] = nombre_unico
            f['validacion_fiscal'] = 'Pendiente'
            escribir_json('facturas.json', data)
            
            # Enviar notificaciÃ³n a administraciÃ³n
            enviar_correo_factura_fiscal_subida("armandoramireztelnor2026@gmail.com", f.get('proveedor', 'Proveedor'), f.get('unidad', 'S/N'), f.get('titulo', 'Sin TÃ­tulo'), folio)
            
            return jsonify({"status": "success", "message": "Factura fiscal subida y adjuntada correctamente al expediente. Se ha notificado a AdministraciÃ³n."})
            
    return jsonify({"status": "error", "message": "Registro no encontrado."})

@facturas_bp.route('/api/facturas/validar_fiscal', methods=['POST'])
def validar_fiscal():
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion':
        return jsonify({"status": "error", "message": "No tienes permisos para validar facturas."})
    
    factura_id = request.json.get('id')
    data = leer_json('facturas.json')
    for f in data.get('facturas', []):
        if str(f['id']) == str(factura_id):
            f['validacion_fiscal'] = 'Aprobada'
            escribir_json('facturas.json', data)
            return jsonify({"status": "success", "message": "Factura validada correctamente. Ahora puede ser editada si es necesario."})
    return jsonify({"status": "error", "message": "Factura no encontrada."})

@facturas_bp.route('/api/facturas/rechazar_fiscal', methods=['POST'])
def rechazar_fiscal():
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion':
        return jsonify({"status": "error", "message": "No tienes permisos para rechazar facturas."})
    
    factura_id = request.json.get('id')
    motivo = request.json.get('motivo', 'Sin motivo especificado')
    data = leer_json('facturas.json')
    usuarios = leer_json('usuarios.json').get('usuarios', [])
    
    for f in data.get('facturas', []):
        if str(f['id']) == str(factura_id):
            folio_borrado = f.get('factura_folio', 'Desconocido')
            # Limpiamos el folio y PDF para que el proveedor vuelva a subir
            f.pop('factura_folio', None)
            f.pop('factura_pdf', None)
            f.pop('pdf_fiscal', None)
            f['validacion_fiscal'] = 'Rechazada'
            
            # Opcional: Agregar comentario al ticket o mandar correo aquÃ­, por ahora solo retro interna
            if not f.get('retro'): f['retro'] = ""
            f['retro'] += f"\n\n[ADMINISTRACIÃ“N - Factura Rechazada]: {motivo}"
            
            escribir_json('facturas.json', data)
            
            # Buscar correo del proveedor
            correo_proveedor = ""
            for u in usuarios:
                if u.get('usuario') == f.get('proveedor'):
                    correo_proveedor = u.get('datos_perfil', {}).get('correo', '')
                    break
            
            if correo_proveedor:
                enviar_correo_factura_fiscal_rechazada(correo_proveedor, f.get('proveedor'), f.get('unidad'), folio_borrado, motivo)
            
            return jsonify({"status": "success", "message": "Factura rechazada. Se notificarÃ¡ al proveedor para que la suba de nuevo."})
    return jsonify({"status": "error", "message": "Factura no encontrada."})

@facturas_bp.route('/api/facturas/doc50', methods=['POST'])
def doc50():
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion':
        return jsonify({'status': 'error', 'message': 'No tienes permisos.'})

    factura_id = request.form.get('id')
    numero_doc50 = request.form.get('numero_doc50')
    file = request.files.get('pdf')

    if not file or file.filename == '':
        return jsonify({'status': 'error', 'message': 'No se seleccionÃ³ archivo.'})

    filename = secure_filename(f'doc50_{factura_id}_{file.filename}')
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    data = leer_json('facturas.json')
    for f in data.get('facturas', []):
        if str(f['id']) == str(factura_id):
            f['numero_doc50'] = numero_doc50
            f['pdf_doc50'] = filename
            escribir_json('facturas.json', data)
            return jsonify({'status': 'success', 'message': 'Documento Contable subido y guardado correctamente. El proceso ha concluido.'})

    return jsonify({'status': 'error', 'message': 'Factura no encontrada.'})
