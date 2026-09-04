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
    enviar_correo_factura_rechazada_corp,
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
        return "\n✅ Orden aprobada. El taller ha sido autorizado para iniciar la reparación."
    return ""


@facturas_bp.route("/api/facturas/nueva", methods=["POST"])
def nueva_factura():
    if "usuario" not in session or session["usuario"]["rol"] != "proveedores":
        return jsonify({"status": "error", "message": "No autorizado"})

    proveedor = session["usuario"]["datos_perfil"]["nombre_proveedor"]
    unidad_sola = request.form.get("unidad")
    unidad = f"8090-{unidad_sola}"
    responsable = request.form.get("responsable")
    telefono = request.form.get("telefono")
    fecha = request.form.get("fecha")

    # Leer arrays de cotizaciones
    precios = request.form.getlist("precio[]")
    pdfs_cotizacion = request.files.getlist("pdf_cotizacion[]")
    titulos = request.form.getlist("titulo[]")
    mantenimientos = request.form.getlist("mantenimiento[]")
    retros = request.form.getlist("retro[]")
    diagnosticos = request.form.getlist("diagnostico[]")
    trabajos = request.form.getlist("trabajo_realizar[]")

    import time
    timestamp_base = int(time.time() * 1000)
    factura_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    precio_total = 0.0
    necesita_corp = False
    cotizaciones_array = []

    # Si no hay arrays (formulario viejo), crear una sola cotización con datos globales
    if len(precios) == 0:
        precio_str = request.form.get("precio", "0")
        precio_limpio = "".join(c for c in precio_str if c.isdigit() or c == ".")
        precio_float = float(precio_limpio) if precio_limpio else 0.0
        precio_total = precio_float
        necesita_corp = precio_float >= 10001.0

        cot = {
            "id_cotizacion": "1",
            "titulo": request.form.get("titulo", "Sin título"),
            "mantenimiento": request.form.get("mantenimiento", "General"),
            "retro": request.form.get("retro", ""),
            "diagnostico": request.form.get("diagnostico", ""),
            "trabajo_realizar": request.form.get("trabajo_realizar", ""),
            "precio": precio_float,
            "fotos_evidencia": [],
        }

        # Archivos (viejo formato)
        for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
            archivos = request.files.getlist(tipo)
            saved = []
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    nombre_unico = f"{tipo}_{factura_id}_{filename}"
                    archivo.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                    saved.append(nombre_unico)
            if tipo == "fotos_cotizacion" and saved:
                cot["pdf_cotizacion"] = saved[0]
            elif tipo == "fotos_evidencia":
                cot["fotos_evidencia"] = saved

        cotizaciones_array.append(cot)
    else:
        # Nuevo formato multi-cotización
        for i in range(len(precios)):
            try:
                precio_val = float(precios[i].replace(",", "").replace("$", "").strip())
            except (ValueError, TypeError):
                precio_val = 0.0

            precio_total += precio_val
            if precio_val >= 10001.0:
                necesita_corp = True

            cot = {
                "id_cotizacion": str(i + 1),
                "precio": precio_val,
                "titulo": titulos[i] if i < len(titulos) else "Sin título",
                "mantenimiento": mantenimientos[i] if i < len(mantenimientos) else "General",
                "retro": retros[i] if i < len(retros) else "",
                "diagnostico": diagnosticos[i] if i < len(diagnosticos) else "",
                "trabajo_realizar": trabajos[i] if i < len(trabajos) else "",
                "fotos_evidencia": [],
            }

            if i < len(pdfs_cotizacion) and pdfs_cotizacion[i] and pdfs_cotizacion[i].filename != "":
                pdf = pdfs_cotizacion[i]
                filename = secure_filename(pdf.filename)
                nombre_unico = f"{timestamp_base}_{i}_{filename}"
                pdf.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                cot["pdf_cotizacion"] = nombre_unico

            archivos_ev = request.files.getlist(f"fotos_evidencia_{i}[]")
            for archivo in archivos_ev:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    nombre_unico = f"evidencia_{timestamp_base}_{i}_{filename}"
                    archivo.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                    cot["fotos_evidencia"].append(nombre_unico)

            cotizaciones_array.append(cot)

    # Detectar compañía desde ticket vinculado
    retro_global = cotizaciones_array[0].get("retro", "") if cotizaciones_array else ""
    compania_asignada = "RUMN"
    import re as re_mod
    match_ticket = re_mod.search(r"\[TICKET:(.*?)\]", retro_global)
    if match_ticket:
        ticket_id = match_ticket.group(1).strip()
        rep_data = leer_json("reportes.json")
        for r in rep_data.get("reportes", []):
            if str(r.get("id")) == str(ticket_id):
                compania_asignada = r.get("compania", "RUMN")
                break

    # Título global = primer título de cotización
    titulo_global = cotizaciones_array[0].get("titulo", "Sin título") if cotizaciones_array else "Sin título"
    if len(cotizaciones_array) > 1:
        titulo_global = f"{titulo_global} (+{len(cotizaciones_array)-1} más)"

    nueva = {
        "id": factura_id,
        "proveedor": proveedor,
        "unidad": unidad,
        "responsable": responsable,
        "telefono": telefono,
        "titulo": titulo_global,
        "retro": retro_global,
        "diagnostico": cotizaciones_array[0].get("diagnostico", "") if cotizaciones_array else "",
        "trabajo_realizar": cotizaciones_array[0].get("trabajo_realizar", "") if cotizaciones_array else "",
        "mantenimiento": cotizaciones_array[0].get("mantenimiento", "General") if cotizaciones_array else "General",
        "precio": precio_total,
        "fecha": fecha,
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
        "cotizaciones": cotizaciones_array,
    }

    data = leer_json("facturas.json")
    data.setdefault("facturas", []).append(nueva)
    escribir_json("facturas.json", data)

    usuarios_data = leer_json("usuarios.json")
    admins_data = []
    corps_data = []

    proveedor_ciudad = session["usuario"]["datos_perfil"].get("ciudad", "")

    for u in usuarios_data.get("usuarios", []):
        if u["rol"] == "administracion":
            subrol = u["datos_perfil"].get("subrol", "Administración")
            ciudad_admin = u["datos_perfil"].get("ciudad", "")
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

    titulo_correo = f"Cotización: {titulo_global}"
    if admins_data:
        enviar_correo_nueva_factura(admins_data, proveedor, unidad_sola, precio_total, titulo=titulo_correo, cotizaciones=cotizaciones_array)
    if necesita_corp and corps_data:
        enviar_correo_nueva_factura_corp(corps_data, proveedor, unidad_sola, precio_total, titulo=titulo_correo)

    correo_proveedor = session["usuario"]["datos_perfil"].get("correo")
    if correo_proveedor and correo_proveedor.strip():
        enviar_correo_confirmacion_factura(correo_proveedor, proveedor, unidad_sola, precio_total)

    return jsonify({"status": "success", "message": "Cotización enviada correctamente a revisión."})


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
            # --- FILTRO GEOGRÁFICO PARA SUPERVISORES ---
            subrol = session["usuario"]["datos_perfil"].get("subrol", "")
            if subrol == "Supervisor":
                mi_ciudad = session["usuario"]["datos_perfil"].get("ciudad", "")
                usuarios_data = leer_json("usuarios.json")
                
                # Primero, buscamos cómo se llaman todos los proveedores de la misma ciudad
                proveedores_locales = [u["datos_perfil"]["nombre_proveedor"] for u in usuarios_data.get("usuarios", []) if u["rol"] == "proveedores" and u["datos_perfil"].get("ciudad") == mi_ciudad]
                
                # Luego, solo le mostramos al Supervisor las facturas que vengan de esos proveedores locales
                facturas = [f for f in facturas if f.get("proveedor") in proveedores_locales]


    # INYECTAR DATOS DEL REPORTE INICIAL
    try:
        reportes_data = leer_json("reportes.json").get("reportes", [])
        reportes_dict = {str(r.get("id")): r for r in reportes_data}
        
        for f in facturas:
            retro = f.get("retro", "")
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                ticket_id = match.group(1).strip()
                if ticket_id in reportes_dict:
                    f["reporte_inicial"] = reportes_dict[ticket_id]
    except Exception as e:
        pass

    return jsonify({"facturas": facturas})


@facturas_bp.route("/api/facturas/confirmar_admin", methods=["POST"])
def confirmar_admin():
    factura_id = request.form.get("id")
    
    # Manejar posibles arrays de ordenes (nuevo formato)
    nums_orden = request.form.getlist("numero_orden[]")
    nums_cotizacion = request.form.getlist("numero_cotizacion[]")
    pdfs_orden = request.files.getlist("pdf_orden[]")
    
    # Compatibilidad formato viejo
    if not nums_orden:
        num = request.form.get("numero_orden")
        if num: nums_orden = [num]
        cot = request.form.get("numero_cotizacion")
        if cot: nums_cotizacion = [cot]
        pdf = request.files.get("pdf_cotizacion")
        if pdf: pdfs_orden = [pdf]

    data = leer_json("facturas.json")
    
    for f in data.get("facturas", []):
        if str(f["id"]) == str(factura_id):
            f["aprobado_admin"] = True
            f["estado_custom"] = ""
            
            # Guardamos los primeros datos en la raiz por compatibilidad vieja
            if nums_orden: f["numero_orden"] = nums_orden[0]
            if nums_cotizacion: f["numero_cotizacion_asignacion"] = nums_cotizacion[0]
            
            cots = f.get("cotizaciones", [])
            for i, cot in enumerate(cots):
                if i < len(nums_orden):
                    cot["numero_orden"] = nums_orden[i]
                if i < len(nums_cotizacion):
                    cot["numero_cotizacion_asignacion"] = nums_cotizacion[i]
                    
                if i < len(pdfs_orden) and pdfs_orden[i] and pdfs_orden[i].filename != '':
                    pdf = pdfs_orden[i]
                    carpeta_cotizaciones = os.path.join("static", "facturas_archivos")
                    if not os.path.exists(carpeta_cotizaciones): os.makedirs(carpeta_cotizaciones)
                    nombre_pdf = f"Cotizacion_Orden_{factura_id}_{i}_{secure_filename(pdf.filename)}"
                    pdf.save(os.path.join(carpeta_cotizaciones, nombre_pdf))
                    cot["pdf_cotizacion_asignacion"] = nombre_pdf
                    if i == 0: f["pdf_cotizacion_asignacion"] = nombre_pdf

            reportes_data = leer_json("reportes.json")
            for r in reportes_data.get("reportes", []):
                if str(r.get("id")) == str(f.get("reporte_id", "")):
                    if nums_cotizacion: r["numero_cotizacion_asignacion"] = nums_cotizacion[0]
                    if f.get("pdf_cotizacion_asignacion"): r["pdf_cotizacion_asignacion"] = f["pdf_cotizacion_asignacion"]
                    escribir_json("reportes.json", reportes_data)
                    break

            mensaje_extra = procesar_liberacion_si_aplica(f)
            escribir_json("facturas.json", data)
            return jsonify({"status": "success", "message": "Órdenes asignadas y validadas por Administración." + mensaje_extra})
            
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
            return jsonify({"status": "success", "message": "Autorización financiera aprobada." + mensaje_extra})
    return jsonify({"status": "error", "message": "Registro no encontrado."})



@facturas_bp.route("/api/facturas/cancelar_cotizacion", methods=["POST"])
def cancelar_cotizacion():
    factura_id = request.form.get("id")
    data = leer_json("facturas.json")
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            f["estado"] = "Cancelado_Cotizacion_Cara"
            escribir_json("facturas.json", data)
            try:
                unidad_num = f.get("unidad", "").replace("8090-", "")
                if unidad_num:
                    unidades = leer_json("unidades.json")
                    if unidades and unidad_num in unidades:
                        unidades[unidad_num]["Estado"] = "Inactiva"
                        escribir_json("unidades.json", unidades)
            except Exception as e:
                print("Error desactivando unidad:", str(e))
            return jsonify({"status": "success", "message": "Ticket cancelado por cotización cara. Se movió a la pestaña correspondiente en Archivo General."})
    return jsonify({"status": "error", "message": "Factura no encontrada."})

@facturas_bp.route("/api/facturas/rechazar", methods=["POST"])


def rechazar_factura():
    factura_id = request.json.get("id")
    motivo = request.json.get("motivo", "Motivo no especificado por la administración.")
    
    data = leer_json("facturas.json")
    nuevas_facturas = []
    eliminada = False
    factura_a_eliminar = None
    
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            eliminada = True
            factura_a_eliminar = f
            for cot in f.get("cotizaciones", []):
                if cot.get("pdf_cotizacion"):
                    ruta = os.path.join(CARPETA_FACTURAS, cot["pdf_cotizacion"])
                    if os.path.exists(ruta): os.remove(ruta)
                for foto in cot.get("fotos_evidencia", []):
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
            
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

@facturas_bp.route("/api/facturas/rechazar_corp", methods=["POST"])
def rechazar_corp():
    if "usuario" not in session or session["usuario"]["rol"] != "corporativos":
        return jsonify({"status": "error", "message": "No autorizado"})
        
    factura_id = request.json.get("id")
    motivo = request.json.get("motivo", "Motivo no especificado por Corporativo.")
    precios_recomendados = request.json.get("precios_recomendados", [])
    
    data = leer_json("facturas.json")
    nuevas_facturas = []
    eliminada = False
    factura_a_eliminar = None
    
    for f in data.get("facturas", []):
        if f["id"] == factura_id:
            eliminada = True
            factura_a_eliminar = f
            for cot in f.get("cotizaciones", []):
                if cot.get("pdf_cotizacion"):
                    ruta = os.path.join(CARPETA_FACTURAS, cot["pdf_cotizacion"])
                    if os.path.exists(ruta): os.remove(ruta)
                for foto in cot.get("fotos_evidencia", []):
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
            
            for tipo in ["fotos_cotizacion", "fotos_evidencia"]:
                for foto in f.get(tipo, []):
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
        else:
            nuevas_facturas.append(f)
            
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
            enviar_correo_factura_rechazada_corp(correo_prov, proveedor_nombre, unidad_texto, motivo, precios_recomendados)
            
        return jsonify({"status": "success", "message": "Gasto rechazado. El ticket fue eliminado y el proveedor fue notificado con tus recomendaciones."})
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
            return jsonify({"status": "success", "message": "¡Unidad marcada como lista! El PIN ha sido enviado al chofer."})
            
    return jsonify({"status": "error", "message": "Registro no encontrado."})

@facturas_bp.route('/api/facturas/subir_factura_final', methods=['POST'])
def subir_factura_final():
    if 'usuario' not in session or session['usuario']['rol'] != 'proveedores':
        return jsonify({"status": "error", "message": "No autorizado"})
        
    factura_id = request.form.get('id_factura')
    folios = request.form.getlist('folio[]')
    pdfs_factura = request.files.getlist('pdf_factura[]')
    
    # Compatibilidad vieja
    if not folios:
        fol = request.form.get('folio')
        if fol: folios = [fol]
        pdf = request.files.get('pdf_factura')
        if pdf: pdfs_factura = [pdf]
        
    if not pdfs_factura:
        return jsonify({"status": "error", "message": "Debe subir los archivos PDF."})
        
    folios_limpios = [str(fol).strip().upper() for fol in folios if str(fol).strip()]
    if len(folios_limpios) != len(set(folios_limpios)):
        return jsonify({"status": "error", "message": "No puedes ingresar folios repetidos para distintas cotizaciones en el mismo ticket."})
        
    data = leer_json('facturas.json')
    
    todos_los_folios = set()
    for f_db in data.get('facturas', []):
        # Excluir el ticket actual de la validación global por si se están resubiendo
        if str(f_db.get('id')) == str(factura_id):
            continue
        if f_db.get('factura_folio'):
            todos_los_folios.add(str(f_db['factura_folio']).strip().upper())
        for c_db in f_db.get('cotizaciones', []):
            if c_db.get('factura_folio'):
                todos_los_folios.add(str(c_db['factura_folio']).strip().upper())
                
    for fol in folios_limpios:
        if fol in todos_los_folios:
            return jsonify({"status": "error", "message": f"El folio fiscal '{fol}' ya se encuentra registrado en otro ticket del sistema."})

    for f in data.get('facturas', []):
        if str(f['id']) == str(factura_id):
            
            cots = f.get("cotizaciones", [])
            for i, cot in enumerate(cots):
                if i < len(folios):
                    cot["factura_folio"] = folios[i]
                if i < len(pdfs_factura) and pdfs_factura[i] and pdfs_factura[i].filename != '':
                    pdf = pdfs_factura[i]
                    filename = secure_filename(pdf.filename)
                    nombre_unico = f"FACTURA_FINAL_{factura_id}_{i}_{filename}"
                    pdf.save(os.path.join(CARPETA_FACTURAS, nombre_unico))
                    cot["factura_pdf"] = nombre_unico
                    if i == 0: 
                        f['factura_folio'] = folios[i]
                        f['factura_pdf'] = nombre_unico

            f['validacion_fiscal'] = 'Pendiente'
            escribir_json('facturas.json', data)
            
            # Notificar
            enviar_correo_factura_fiscal_subida("armandoramireztelnor2026@gmail.com", f.get('proveedor', 'Proveedor'), f.get('unidad', 'S/N'), f.get('titulo', 'Sin Título'), folios[0] if folios else 'Varios')
            return jsonify({"status": "success", "message": "Facturas fiscales subidas correctamente. Se notificó a Administración."})
            
    return jsonify({"status": "error", "message": "No se encontró el registro."})
            
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
            f.pop('factura_folio', None)
            f.pop('factura_pdf', None)
            f.pop('pdf_fiscal', None)
            
            for cot in f.get('cotizaciones', []):
                if not folio_borrado or folio_borrado == 'Desconocido':
                    folio_borrado = cot.get('factura_folio', 'Desconocido')
                cot.pop('factura_folio', None)
                cot.pop('factura_pdf', None)
                cot.pop('pdf_fiscal', None)

            f['validacion_fiscal'] = 'Rechazada'
            
            # Opcional: Agregar comentario al ticket o mandar correo aquí, por ahora solo retro interna
            if not f.get('retro'): f['retro'] = ""
            f['retro'] += f"\n\n[ADMINISTRACIÓN - Factura Rechazada]: {motivo}"
            
            escribir_json('facturas.json', data)
            
            # Buscar correo del proveedor
            correo_proveedor = ""
            for u in usuarios:
                if u.get('usuario') == f.get('proveedor'):
                    correo_proveedor = u.get('datos_perfil', {}).get('correo', '')
                    break
            
            if correo_proveedor:
                enviar_correo_factura_fiscal_rechazada(correo_proveedor, f.get('proveedor'), f.get('unidad'), folio_borrado, motivo)
            
            return jsonify({"status": "success", "message": "Factura rechazada. Se notificará al proveedor para que la suba de nuevo."})
    return jsonify({"status": "error", "message": "Factura no encontrada."})

@facturas_bp.route('/api/facturas/doc50', methods=['POST'])
def doc50():
    if 'usuario' not in session or session['usuario']['rol'] != 'administracion':
        return jsonify({'status': 'error', 'message': 'No tienes permisos.'})

    factura_id = request.form.get('id_factura') # El form envía id_factura, no id
    if not factura_id: factura_id = request.form.get('id')

    nums_doc50 = request.form.getlist('numero_doc50[]')

    # Compatibilidad
    if not nums_doc50:
        num = request.form.get('numero_doc50')
        if num: nums_doc50 = [num]

    if not nums_doc50:
        return jsonify({'status': 'error', 'message': 'Faltan números de documento contable.'})

    data = leer_json('facturas.json')
    for f in data.get('facturas', []):
        if str(f['id']) == str(factura_id):
            
            cots = f.get("cotizaciones", [])
            for i, cot in enumerate(cots):
                if i < len(nums_doc50):
                    cot['numero_doc50'] = nums_doc50[i]
                    if i == 0:
                        f['numero_doc50'] = nums_doc50[i]

            f['estado'] = 'Archivado'
            escribir_json('facturas.json', data)
            return jsonify({'status': 'success', 'message': 'Documentos Contables subidos. El proceso ha concluido para todas las cotizaciones.'})

    return jsonify({'status': 'error', 'message': 'Factura no encontrada.'})


@facturas_bp.route("/api/facturas/editar_seccion_especifica", methods=["POST"])
def editar_seccion_especifica():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})
    
    id_factura = request.form.get("id_factura")
    seccion = request.form.get("seccion")
    identificador = request.form.get("identificador")
    pdf_file = request.files.get("pdf_file")
    
    if not all([id_factura, seccion, identificador, pdf_file]):
        return jsonify({"status": "error", "message": "Faltan datos requeridos."})
        
    data = leer_json("facturas.json")
    factura = next((f for f in data.get("facturas", []) if str(f["id"]) == str(id_factura)), None)
    
    if not factura:
        return jsonify({"status": "error", "message": "Factura no encontrada."})
        
    filename = f"{seccion}_{id_factura}_{secure_filename(pdf_file.filename)}"
    filepath = os.path.join(CARPETA_FACTURAS, filename)
    pdf_file.save(filepath)
    
    pdf_antiguo = None
    
    if seccion == "orden":
        pdf_antiguo = factura.get("pdf_cotizacion_asignacion")
        factura["numero_cotizacion_asignacion"] = identificador
        factura["numero_orden"] = identificador
        factura["pdf_cotizacion_asignacion"] = filename
        
        # Sincronizar con reportes.json
        reportes_data = leer_json("reportes.json")
        for r in reportes_data.get("reportes", []):
            if str(r.get("id")) == str(factura.get("id_reporte")):
                r["numero_cotizacion_asignacion"] = identificador
                r["pdf_cotizacion_asignacion"] = filename
                break
        escribir_json("reportes.json", reportes_data)
        
    elif seccion == "factura":
        pdf_antiguo = factura.get("factura_pdf") or factura.get("pdf_fiscal")
        factura["factura_folio"] = identificador
        factura["factura_pdf"] = filename
        factura["pdf_fiscal"] = filename
        
    elif seccion == "doc_contable":
        pdf_antiguo = factura.get("pdf_doc50")
        factura["numero_doc50"] = identificador
        factura["pdf_doc50"] = filename
        
    escribir_json("facturas.json", data)
    
    # Eliminar PDF antiguo si existe
    if pdf_antiguo:
        try:
            ruta_antigua = os.path.join(CARPETA_FACTURAS, pdf_antiguo)
            if os.path.exists(ruta_antigua):
                os.remove(ruta_antigua)
        except Exception as e:
            print(f"Error al borrar pdf antiguo {pdf_antiguo}: {e}")
            
    return jsonify({"status": "success"})


@facturas_bp.route("/api/facturas/eliminar_silencioso", methods=["POST"])
def eliminar_silencioso():
    if "usuario" not in session or session["usuario"]["rol"] != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"})

    factura_id = request.json.get("id")
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
                    import os
                    ruta = os.path.join(CARPETA_FACTURAS, foto)
                    if os.path.exists(ruta): os.remove(ruta)
        else: nuevas_facturas.append(f)
            
    if eliminada and factura_a_eliminar:
        data["facturas"] = nuevas_facturas
        escribir_json("facturas.json", data)
        
        # Eliminar tambin el reporte (ticket) original asociado para que no regrese a la bandeja de reportes
        reporte_id = factura_a_eliminar.get("numero_reporte", "")
        if not reporte_id:
            retro = factura_a_eliminar.get("retro", "")
            if "[TICKET:" in retro:
                import re
                match = re.search(r"\[TICKET:(.*?)\]", retro)
                if match:
                    reporte_id = match.group(1).strip()
                    
        if reporte_id:
            rep_data = leer_json("reportes.json")
            nuevos_reportes = [r for r in rep_data.get("reportes", []) if str(r.get("id")) != str(reporte_id)]
            rep_data["reportes"] = nuevos_reportes
            escribir_json("reportes.json", rep_data)

        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Factura no encontrada"})
