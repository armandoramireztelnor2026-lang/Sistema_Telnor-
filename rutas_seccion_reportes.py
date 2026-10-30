import os
import json
from flask import Blueprint, jsonify, session

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, "r", encoding="utf-8") as f: return json.load(f)

seccion_reportes_bp = Blueprint('seccion_reportes_bp', __name__)

ESTADOS_SISTEMA_TICKET = [
    "Pendiente / Asig. Taller",
    "Pendiente de Cotización",
    "Correcciones/Taller",
    "Esperando / Aprob. Cotizacion (Supervisor)",
    "Esperando / Aprob. Cotizacion (Admin)",
    "Esperando / Aprob. Cotizacion (Corp)",
    "En Reparación (Taller)",
    "Validación / Pin (Chofer)",
    "Esperando Facturación (Taller)",
    "Esperando Rev/Factura",
    "Esperando Num. Contable",
    "Finalizado / Histórico",
    "Incosteable"
]

def determinar_estado_ticket(f):
    estado_raw = f.get('estado', '')
    is_unassigned = f.get('is_unassigned', False)
    
    if estado_raw == 'Cancelado_Cotizacion_Cara':
        return "Incosteable"
    elif estado_raw == 'Rechazado_Con_Recomendaciones':
        return "Correcciones/Taller"
    elif estado_raw in ('Archivado', 'Archivado_Final'):
        return "Finalizado / Histórico"
    elif is_unassigned:
        if not f.get('asignado_a'):
            return "Pendiente / Asig. Taller"
        else:
            return "Pendiente de Cotización"
    else:
        cotizaciones = f.get('cotizaciones', [])
        tiene_cot = len(cotizaciones) > 0
        try:
            precio = float(f.get('precio', 0) or 0)
        except Exception:
            precio = 0
        is_cara = precio >= 10001
        ap_super = f.get('aprobado_admin') is True
        ap_admin = f.get('aprobado_admin_10k') is True
        ap_corp = f.get('aprobado_corp') is True
        
        if is_cara:
            confirmada_total = (ap_super and ap_admin and ap_corp)
        else:
            confirmada_total = (ap_super and ap_corp)
            
        if not tiene_cot or estado_raw in ('Rechazado', 'Rechazada_Por_Cotizacion_Normal_U_Otra'):
            return "Pendiente de Cotización"
        else:
            if confirmada_total:
                if not f.get('codigo_liberacion'):
                    return "En Reparación (Taller)"
                elif f.get('entregado') != 'Sí':
                    return "Validación / Pin (Chofer)"
                else:
                    factura_pdf = f.get('factura_pdf') or f.get('pdf_fiscal')
                    val_fiscal = f.get('validacion_fiscal')
                    if not factura_pdf or val_fiscal == 'Rechazada':
                        return "Esperando Facturación (Taller)"
                    elif val_fiscal != 'Aprobada':
                        return "Esperando Rev/Factura"
                    elif not f.get('numero_doc50'):
                        return "Esperando Num. Contable"
                    else:
                        return "Finalizado / Histórico"
            else:
                if is_cara:
                    if not ap_super:
                        return "Esperando / Aprob. Cotizacion (Supervisor)"
                    elif not ap_admin:
                        return "Esperando / Aprob. Cotizacion (Admin)"
                    elif not ap_corp:
                        return "Esperando / Aprob. Cotizacion (Corp)"
                    else:
                        return "En Reparación (Taller)"
                else:
                    return "Esperando / Aprob. Cotizacion (Supervisor)"

@seccion_reportes_bp.route('/api/seccion_reportes/lista', methods=['GET'])
def obtener_lista_seccion_reportes():
    """
    Retorna la lista de todas las facturas/tickets para la vista general de la Jefatura.
    Solo accesible para usuarios con subrol 'Jefatura' o rol 'administracion'.
    Soporta filtros opcionales por query params (estado, texto, proveedor, ciudad, fecha) con lógica AND.
    """
    if "usuario" not in session:
        return jsonify({"status": "error", "message": "No autenticado"}), 401
    
    usuario = session["usuario"]
    # Todos en administracion pueden ver esto
    if usuario.get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    from flask import request
    import unicodedata

    reportes_data = leer_json('reportes.json')
    facturas_data = leer_json('facturas.json')
    archivados_data = leer_json('tickets_archivados.json')
    
    todos_reportes = reportes_data.get("reportes", [])
    todas_facturas = facturas_data.get("facturas", []) + archivados_data.get("facturas", [])
    
    # Set of report IDs that have a corresponding factura
    facturas_ids = set()
    import re
    for f in todas_facturas:
        r_id = f.get("id_reporte") or f.get("numero_reporte")
        if not r_id:
            retro = f.get("retro", "")
            if "[TICKET:" in retro:
                match = re.search(r"\[TICKET:(.*?)\]", retro)
                if match:
                    r_id = match.group(1).strip()
        if r_id:
            facturas_ids.add(str(r_id))
            
    # Solo agregamos reportes que no tengan una factura ya creada
    reportes_no_asignados = [r for r in todos_reportes if str(r.get("id")) not in facturas_ids]
    
    # Marcamos de donde vienen por si acaso
    for r in reportes_no_asignados:
        r['origen'] = 'reportes'
        r['is_unassigned'] = True
    for f in todas_facturas:
        f['origen'] = 'facturas'
        f['is_unassigned'] = False
        
    todos_combinados = reportes_no_asignados + todas_facturas
    
    # Mapear nombre del supervisor a cada ticket
    usuarios_list = leer_json('usuarios.json').get('usuarios', [])
    
    # 1. Mapeo: COPE -> nombre de supervisor, administrador y jefatura
    cope_a_sup = {}
    cope_a_admin = {}
    nombre_jefatura = "No asignado"
    for u in usuarios_list:
        if u.get('rol') == 'administracion':
            subrol = u.get('datos_perfil', {}).get('subrol')
            cope_principal = u.get('datos_perfil', {}).get('cope', '')
            copes_extra = u.get('datos_perfil', {}).get('copes_asignados', [])
            nombres = u.get('datos_perfil', {}).get('nombres', '')
            apellido_pat = u.get('datos_perfil', {}).get('apellido_paterno', '')
            apellido_mat = u.get('datos_perfil', {}).get('apellido_materno', '')
            nombre_completo = re.sub(r'\s+', ' ', f"{nombres} {apellido_pat} {apellido_mat}").strip()
            
            todos_copes = [cope_principal] + copes_extra if cope_principal else copes_extra
            for cope in todos_copes:
                if cope:
                    if subrol == 'Supervisor':
                        cope_a_sup[cope] = nombre_completo
                    elif subrol == 'Administrador':
                        cope_a_admin[cope] = nombre_completo
            
            if subrol == 'Jefatura' and nombre_completo:
                nombre_jefatura = nombre_completo

    # Precalcular COPEs y reactivados de los reportes para búsqueda rápida
    reporte_a_cope = {str(r.get("id")): r.get("cope", "") for r in todos_reportes}
    reporte_a_reactivado = {str(r.get("id")): r.get("reactivado_desde_caras", False) for r in todos_reportes}

    # Precalcular datos de retrabajos para cruzar fechas de reingreso
    retrabajos_data = leer_json('retrabajos.json')
    retrabajos_map = {}
    for ret in retrabajos_data.get('retrabajos', []):
        t_orig = str(ret.get('ticket_original') or ret.get('ticket') or ret.get('id', '')).strip().upper()
        f_id_ret = str(ret.get('factura_id', '')).strip().upper()
        if t_orig:
            retrabajos_map[t_orig] = ret
        if f_id_ret:
            retrabajos_map[f_id_ret] = ret

    # 2. Asignar nombres al ticket y calcular estado
    for f in todos_combinados:
        cope_f = f.get('cope', '')
        
        # Extraer ID del reporte para cruzar información
        r_id = f.get("id_reporte") or f.get("numero_reporte")
        if not r_id:
            retro = f.get("retro", "")
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                r_id = match.group(1).strip()
        if not r_id:
            r_id = f.get("id")

        # Si no tiene COPE (como las facturas), extraerlo del reporte original
        if not cope_f and r_id:
            cope_f = reporte_a_cope.get(str(r_id), "")

        # Si el reporte original fue reactivado desde cotizaciones caras, preservar la bandera
        if not f.get('reactivado_desde_caras') and r_id:
            if reporte_a_reactivado.get(str(r_id)):
                f['reactivado_desde_caras'] = True

        sup_nombre = cope_a_sup.get(cope_f, "No asignado")
        admin_nombre = cope_a_admin.get(cope_f, "No asignado")
        
        f['supervisor_nombre'] = sup_nombre
        f['administrador_nombre'] = admin_nombre
        f['jefatura_nombre'] = nombre_jefatura
        f['estado_calculado'] = determinar_estado_ticket(f)

        # Cruzar con retrabajos.json para obtener los datos de reingreso
        t_key = str(f.get("id", "")).strip().upper()
        r_key = str(r_id or "").strip().upper()
        ret_obj = retrabajos_map.get(t_key) or retrabajos_map.get(r_key)
        if ret_obj:
            f['fecha_retrabajo'] = ret_obj.get("fecha_reasignacion") or ret_obj.get("fecha_ingreso") or f.get("fecha_retrabajo")
            if ret_obj.get("estado") == "Finalizado":
                f['fecha_finalizacion_retrabajo'] = ret_obj.get("fecha_finalizacion_taller") or f.get("fecha_finalizacion_retrabajo")
            else:
                f['fecha_finalizacion_retrabajo'] = f.get("fecha_finalizacion_retrabajo") or ""
            f['estado_retrabajo'] = ret_obj.get("estado") or f.get("estado_retrabajo")
            if not f.get("num_retrabajo"):
                f["num_retrabajo"] = 1
            if not f.get("retrabajo"):
                f["retrabajo"] = "Sí"

    # Recopilar lista completa de todos los estados posibles del sistema y base de datos
    estados_disponibles = list(ESTADOS_SISTEMA_TICKET)
    for f in todos_combinados:
        st = f.get('estado_calculado')
        if st and st not in estados_disponibles:
            estados_disponibles.append(st)

    # Filtros opcionales pasados por query params (lógica AND)
    estado_filtro = request.args.get('estado', '').strip()
    texto_filtro = request.args.get('texto', '').strip()
    proveedor_filtro = request.args.get('proveedor', '').strip()
    ciudad_filtro = request.args.get('ciudad', '').strip()
    fecha_filtro = request.args.get('fecha', '').strip()
    reactivadas_filtro = request.args.get('reactivadas', '').strip().lower()

    if reactivadas_filtro in ['1', 'true', 'si', 's']:
        todos_combinados = [f for f in todos_combinados if f.get('reactivado_desde_caras') is True]

    def norm(txt):
        if not txt:
            return ""
        return unicodedata.normalize('NFKD', str(txt)).encode('ASCII', 'ignore').decode('utf-8').strip().lower()

    if any([estado_filtro, texto_filtro, proveedor_filtro, ciudad_filtro, fecha_filtro]):
        texto_norm = norm(texto_filtro)
        estado_norm = norm(estado_filtro)
        prov_norm = norm(proveedor_filtro)
        ciudad_norm = norm(ciudad_filtro)

        resultado_filtrado = []
        for f in todos_combinados:
            match = True
            
            # 1. Filtro Estado (exacto o normalizado)
            if estado_filtro:
                st_norm = norm(f.get('estado_calculado', ''))
                if st_norm != estado_norm:
                    match = False
                    
            # 2. Filtro Texto (en ID, Eco, Retro, Proveedor, Chofer, Supervisor, etc.)
            if match and texto_norm:
                corpus = norm(f"{f.get('id', '')} {f.get('id_reporte', '')} {f.get('unidad', '')} {f.get('retro', '')} {f.get('supervisor_nombre', '')} {f.get('administrador_nombre', '')} {f.get('proveedor', '')}")
                if texto_norm not in corpus:
                    match = False
                    
            # 3. Filtro Proveedor
            if match and prov_norm:
                if prov_norm not in norm(f.get('proveedor', '')):
                    match = False
                    
            # 4. Filtro Ciudad / Base / COPE
            if match and ciudad_norm:
                ciudad_corpus = norm(f"{f.get('ciudad', '')} {f.get('cope', '')}")
                if ciudad_norm not in ciudad_corpus:
                    match = False
                    
            # 5. Filtro Fecha
            if match and fecha_filtro:
                f_fecha = str(f.get('fecha', '') or f.get('timestamp', ''))
                if not f_fecha.startswith(fecha_filtro) and fecha_filtro not in f_fecha:
                    match = False
                    
            if match:
                resultado_filtrado.append(f)
        todos_combinados = resultado_filtrado
    
    return jsonify({
        "status": "success",
        "facturas": todos_combinados,
        "estados_disponibles": estados_disponibles
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
