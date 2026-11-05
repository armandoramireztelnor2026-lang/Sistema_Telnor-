def obtener_limite_cotizaciones_caras():
    try:
        import os, json
        conf_path = os.path.join(os.path.dirname(__file__), "configuracion_sistema.json")
        if os.path.exists(conf_path):
            with open(conf_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
                val = conf.get("limite_cotizaciones_caras")
                if val is not None:
                    return float(val)
    except Exception:
        pass
    return 10000.0

import os
import json
from flask import Blueprint, jsonify, session, request, send_file
import io
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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
    "Incosteable",
    "En Asignacion/Retrabajo",
    "Retrabajo"
]

def determinar_estado_ticket(f):
    estado_raw = f.get('estado', '')
    is_unassigned = f.get('is_unassigned', False)
    
    if estado_raw == 'Cancelado_Cotizacion_Cara':
        return "Incosteable"
    elif estado_raw == 'Rechazado_Con_Recomendaciones':
        return "Correcciones/Taller"
    elif estado_raw == 'En Asignacion/Retrabajo' or f.get('estado_retrabajo') == 'Pendiente':
        return "En Asignacion/Retrabajo"
    elif estado_raw == 'Retrabajo' or f.get('estado_retrabajo') in ('Reasignado', 'Por Liberar'):
        return "Retrabajo"
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
        is_cara = precio >= obtener_limite_cotizaciones_caras()
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
    nombre_corp_global = "Luisa Alejandra Gimenez"
    for u in usuarios_list:
        if u.get('rol') == 'corporativos':
            nombres = u.get('datos_perfil', {}).get('nombres', '')
            apellido_pat = u.get('datos_perfil', {}).get('apellido_paterno', '')
            apellido_mat = u.get('datos_perfil', {}).get('apellido_materno', '')
            nom_corp = re.sub(r'\s+', ' ', f"{nombres} {apellido_pat} {apellido_mat}").strip()
            if nom_corp:
                nombre_corp_global = nom_corp
        elif u.get('rol') == 'administracion':
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
            retrabajos_map[t_orig.replace("REP-", "")] = ret
        if f_id_ret:
            retrabajos_map[f_id_ret] = ret
            retrabajos_map[f_id_ret.replace("FAC-", "")] = ret

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
        f['corporativo_nombre'] = f.get('corporativo_aprobador') or f.get('corporativo_nombre') or (nombre_corp_global if f.get('aprobado_corp') is True else "")
        f['estado_calculado'] = determinar_estado_ticket(f)

        # Cruzar con retrabajos.json para obtener los datos de reingreso
        t_key = str(f.get("id", "")).strip().upper()
        r_key = str(r_id or "").strip().upper()
        ret_obj = (
            retrabajos_map.get(t_key) or 
            retrabajos_map.get(t_key.replace("REP-", "")) or 
            retrabajos_map.get(r_key) or 
            retrabajos_map.get(r_key.replace("REP-", ""))
        )
        if ret_obj:
            f['fecha_retrabajo'] = ret_obj.get("fecha_reasignacion") or ret_obj.get("fecha_ingreso") or f.get("fecha_retrabajo")
            if ret_obj.get("estado") == "Finalizado":
                f['fecha_finalizacion_retrabajo'] = ret_obj.get("fecha_finalizacion_taller") or f.get("fecha_finalizacion_retrabajo")
            elif ret_obj.get("estado") in ["Por Liberar", "por_liberar"]:
                f['fecha_finalizacion_retrabajo'] = ret_obj.get("fecha_finalizacion_taller") or f.get("fecha_finalizacion_retrabajo") or ""
            else:
                f['fecha_finalizacion_retrabajo'] = f.get("fecha_finalizacion_retrabajo") or ""
            f['estado_retrabajo'] = ret_obj.get("estado") or f.get("estado_retrabajo")
            if not f.get("num_retrabajo"):
                f["num_retrabajo"] = 1 if ret_obj.get("estado") != "Pendiente" else 0
            if not f.get("retrabajo"):
                f["retrabajo"] = "Pendiente" if ret_obj.get("estado") == "Pendiente" else "Sí"
            if ret_obj.get("unidad_entregada"):
                f["retrabajo_unidad_entregada"] = ret_obj.get("unidad_entregada")
            if ret_obj.get("reactivado_desde_caras") or ret_obj.get("es_cotizacion_cara"):
                f["reactivado_desde_caras"] = True

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

@seccion_reportes_bp.route('/api/seccion_reportes/exportar_excel', methods=['POST', 'GET'])
def exportar_seccion_reportes_excel():
    if "usuario" not in session or session["usuario"].get("rol") != "administracion":
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    payload = request.get_json(silent=True) or {}
    headers = payload.get("headers", [])
    rows = payload.get("rows", [])
    kpis = payload.get("kpis", {})

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sección de Reportes"
    ws.views.sheetView[0].showGridLines = True

    # PALETA DE COLORES DE ANALÍTICA Y SECCIÓN DE REPORTES
    fill_navy = PatternFill(start_color="112641", end_color="112641", fill_type="solid")
    fill_sub_header = PatternFill(start_color="1F395A", end_color="1F395A", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    # 4 Colores exactos de los encabezados de la tabla de Sección de Reportes
    fill_th_azul = PatternFill(start_color="1F395A", end_color="1F395A", fill_type="solid")      # Azul marino
    fill_th_verde = PatternFill(start_color="40916C", end_color="40916C", fill_type="solid")     # Verde analítica
    fill_th_amarillo = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid")  # Ámbar retrabajo
    fill_th_negro = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")     # Grafito/Negro administrativo

    fill_card_blue = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    fill_card_amber = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    fill_card_green = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")

    font_title = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    font_sub = Font(name="Segoe UI", size=10, italic=True, color="CBD5E1")
    font_section = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_th = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_normal = Font(name="Segoe UI", size=9, color="1E293B")
    font_bold = Font(name="Segoe UI", size=9, bold=True, color="1E293B")
    font_amber = Font(name="Segoe UI", size=9, bold=True, color="B45309")
    font_blue = Font(name="Segoe UI", size=9, bold=True, color="0284C7")
    font_green = Font(name="Segoe UI", size=9, bold=True, color="047857")
    font_total = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")

    border_thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    num_cols = max(len(headers), 1)
    last_col_letter = get_column_letter(num_cols)

    # 1. ENCABEZADO SUPERIOR
    ws.merge_cells(f"A1:{last_col_letter}1")
    ws["A1"] = "SISTEMA DE FACTURACION CENTRAL - SECCIÓN DE REPORTES ANALÍTICOS"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_navy
    ws["A1"].alignment = align_center
    ws.row_dimensions[1].height = 36

    ws.merge_cells(f"A2:{last_col_letter}2")
    ws["A2"] = f"Reporte Consolidado de Mantenimiento y Flota | Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Total Registros: {len(rows)} | Telnor / RUMN"
    ws["A2"].font = font_sub
    ws["A2"].fill = fill_navy
    ws["A2"].alignment = align_center
    ws.row_dimensions[2].height = 22

    # 2. RESUMEN DE KPIS (Filas 4 y 5)
    ws.merge_cells("A4:B4")
    ws["A4"] = "REGISTROS EXPORTADOS"
    ws["A4"].font = Font(name="Segoe UI", size=9, bold=True, color="0369A1")
    ws["A4"].fill = fill_card_blue
    ws["A4"].alignment = align_center
    for c in ["A4", "B4"]: ws[c].border = border_thin

    ws.merge_cells("A5:B5")
    ws["A5"] = f"{len(rows)} tickets"
    ws["A5"].font = Font(name="Segoe UI", size=12, bold=True, color="0284C7")
    ws["A5"].fill = fill_card_blue
    ws["A5"].alignment = align_center
    for c in ["A5", "B5"]: ws[c].border = border_thin

    ws.merge_cells("C4:D4")
    ws["C4"] = "PENDIENTES DOC 50"
    ws["C4"].font = Font(name="Segoe UI", size=9, bold=True, color="B45309")
    ws["C4"].fill = fill_card_amber
    ws["C4"].alignment = align_center
    for c in ["C4", "D4"]: ws[c].border = border_thin

    ws.merge_cells("C5:D5")
    ws["C5"] = str(kpis.get("pendientesDoc50", "--"))
    ws["C5"].font = Font(name="Segoe UI", size=12, bold=True, color="D97706")
    ws["C5"].fill = fill_card_amber
    ws["C5"].alignment = align_center
    for c in ["C5", "D5"]: ws[c].border = border_thin

    ws.merge_cells("E4:F4")
    ws["E4"] = "GASTO TOTAL EN REPORTES"
    ws["E4"].font = Font(name="Segoe UI", size=9, bold=True, color="047857")
    ws["E4"].fill = fill_card_green
    ws["E4"].alignment = align_center
    for c in ["E4", "F4"]: ws[c].border = border_thin

    total_gasto_val = 0.0
    try:
        total_gasto_val = float(str(kpis.get("totalGasto", "0")).replace("$", "").replace(",", "").strip() or 0)
    except Exception:
        total_gasto_val = 0.0

    ws.merge_cells("E5:F5")
    ws["E5"] = f"${total_gasto_val:,.2f} MXN"
    ws["E5"].font = Font(name="Segoe UI", size=12, bold=True, color="10B981")
    ws["E5"].fill = fill_card_green
    ws["E5"].alignment = align_center
    for c in ["E5", "F5"]: ws[c].border = border_thin

    ws.row_dimensions[4].height = 18
    ws.row_dimensions[5].height = 24

    # 3. BARRA SECCIÓN TABLA
    ws.merge_cells(f"A7:{last_col_letter}7")
    ws["A7"] = "📋 DETALLE COMPLETO DE EXPEDIENTES Y TICKETS (SECCIÓN DE REPORTES)"
    ws["A7"].font = font_section
    ws["A7"].fill = fill_sub_header
    ws["A7"].alignment = align_left
    ws.row_dimensions[7].height = 24

    # 4. ENCABEZADOS DE COLUMNAS CON SUS 4 COLORES DE LA WEB
    for col_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=8, column=col_idx, value=h_text)
        cell.font = font_th
        cell.alignment = align_center
        cell.border = border_thin

        # Asignar color por grupo semántico
        if col_idx <= 12:
            cell.fill = fill_th_azul
        elif col_idx <= 18:
            cell.fill = fill_th_verde
        elif col_idx <= 25:
            cell.fill = fill_th_amarillo
        else:
            cell.fill = fill_th_negro

    ws.row_dimensions[8].height = 28

    # 5. FILAS DE DATOS
    costo_col_idx = -1
    for i, h in enumerate(headers, 1):
        if "COSTO" in h.upper():
            costo_col_idx = i
            break

    row_num = 9
    costo_acumulado = 0.0

    for r_vals in rows:
        is_zebra = (row_num % 2 == 0)
        for col_idx, val in enumerate(r_vals, 1):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.border = border_thin
            if is_zebra:
                cell.fill = fill_zebra

            val_str = str(val if val is not None else "").strip()

            if col_idx == costo_col_idx:
                try:
                    num_val = float(val_str.replace("$", "").replace(",", "").strip())
                    cell.value = num_val
                    cell.number_format = "$#,##0.00"
                    cell.font = font_green
                    cell.alignment = align_right
                    costo_acumulado += num_val
                except Exception:
                    cell.value = val_str
                    cell.font = font_normal
                    cell.alignment = align_right
            elif col_idx == 1:
                cell.value = val_str
                cell.font = font_amber
                cell.alignment = align_center
            elif col_idx == 2:
                cell.value = val_str
                cell.font = font_blue
                cell.alignment = align_center
            elif col_idx in [3, 4, 5, 6, 7, 10, 11, 12, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32]:
                cell.value = val_str
                cell.font = font_normal
                cell.alignment = align_center
            else:
                cell.value = val_str
                cell.font = font_normal
                cell.alignment = align_left

        ws.row_dimensions[row_num].height = 22
        row_num += 1

    # 6. FILA DE TOTALES AL FINAL
    if row_num > 9 and costo_col_idx > 0:
        merge_end_letter = get_column_letter(costo_col_idx - 1)
        ws.merge_cells(f"A{row_num}:{merge_end_letter}{row_num}")
        ws[f"A{row_num}"] = "TOTAL GASTO REGISTRADO EN ESTOS REPORTES:"
        ws[f"A{row_num}"].font = font_total
        ws[f"A{row_num}"].fill = fill_navy
        ws[f"A{row_num}"].alignment = align_right

        for ci in range(1, costo_col_idx):
            ws[f"{get_column_letter(ci)}{row_num}"].border = border_thin
            ws[f"{get_column_letter(ci)}{row_num}"].fill = fill_navy

        c_sum = ws.cell(row=row_num, column=costo_col_idx)
        c_sum.value = f"=SUM({get_column_letter(costo_col_idx)}9:{get_column_letter(costo_col_idx)}{row_num-1})"
        c_sum.font = font_total
        c_sum.fill = fill_navy
        c_sum.alignment = align_right
        c_sum.number_format = "$#,##0.00"
        c_sum.border = border_thin

        for ci in range(costo_col_idx + 1, num_cols + 1):
            c_b = ws.cell(row=row_num, column=ci, value="")
            c_b.fill = fill_navy
            c_b.border = border_thin

        ws.row_dimensions[row_num].height = 26

    # Autoajuste de anchos de columnas
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(c.value or '')) for c in col)
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, 45), 14)

    # 7. HOJA 2: RESUMEN POR TALLER Y COPE
    ws2 = wb.create_sheet(title="Resumen por Taller y COPE")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:E1")
    ws2["A1"] = "SECCIÓN DE REPORTES - RESUMEN POR TALLER Y COPE"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_navy
    ws2["A1"].alignment = align_center
    ws2.row_dimensions[1].height = 36

    ws2.merge_cells("A2:E2")
    ws2["A2"] = f"Agrupación Estadística de los Registros Filtrados | Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws2["A2"].font = font_sub
    ws2["A2"].fill = fill_navy
    ws2["A2"].alignment = align_center
    ws2.row_dimensions[2].height = 22

    taller_idx = -1
    cope_idx = -1
    for i, h in enumerate(headers):
        hu = h.upper()
        if "PROVEEDOR" in hu or "TALLER" in hu: taller_idx = i
        if "COPE" in hu: cope_idx = i

    taller_map = {}
    cope_map = {}
    for r_vals in rows:
        t_val = r_vals[taller_idx].strip() if taller_idx >= 0 and taller_idx < len(r_vals) else "Sin especificar"
        cp_val = r_vals[cope_idx].strip() if cope_idx >= 0 and cope_idx < len(r_vals) else "No especificado"
        costo_v = 0.0
        if costo_col_idx > 0 and (costo_col_idx - 1) < len(r_vals):
            try:
                costo_v = float(str(r_vals[costo_col_idx - 1]).replace("$", "").replace(",", "").strip() or 0)
            except Exception:
                costo_v = 0.0

        if not t_val or t_val == "--": t_val = "Sin especificar"
        if not cp_val or cp_val == "--": cp_val = "No especificado"

        if t_val not in taller_map: taller_map[t_val] = {"count": 0, "monto": 0.0}
        taller_map[t_val]["count"] += 1
        taller_map[t_val]["monto"] += costo_v

        if cp_val not in cope_map: cope_map[cp_val] = {"count": 0, "monto": 0.0}
        cope_map[cp_val]["count"] += 1
        cope_map[cp_val]["monto"] += costo_v

    # Tabla Talleres
    ws2.merge_cells("A4:E4")
    ws2["A4"] = "🔧 GASTO Y TICKETS POR TALLER PROVEEDOR"
    ws2["A4"].font = font_section
    ws2["A4"].fill = fill_sub_header
    ws2["A4"].alignment = align_left
    ws2.row_dimensions[4].height = 24

    h_t = ["Taller Mecánico / Proveedor", "Tickets", "Gasto Total (s/IVA)", "% del Total", "Promedio por Ticket"]
    for c_i, h in enumerate(h_t, 1):
        cell = ws2.cell(row=5, column=c_i, value=h)
        cell.font = font_th
        cell.fill = fill_th_verde
        cell.alignment = align_center
        cell.border = border_thin
    ws2.row_dimensions[5].height = 26

    r_cur = 6
    tot_gastado = sum(v["monto"] for v in taller_map.values()) or 1.0

    for t_nom, t_data in sorted(taller_map.items(), key=lambda x: x[1]["monto"], reverse=True):
        m = t_data["monto"]
        c = t_data["count"]
        pct = (m / tot_gastado) * 100
        prom = m / c if c > 0 else 0

        c1 = ws2.cell(row=r_cur, column=1, value=t_nom)
        c1.alignment = align_left
        c2 = ws2.cell(row=r_cur, column=2, value=c)
        c2.alignment = align_center
        c3 = ws2.cell(row=r_cur, column=3, value=m)
        c3.alignment = align_right
        c3.number_format = "$#,##0.00"
        c4 = ws2.cell(row=r_cur, column=4, value=f"{pct:.2f} %")
        c4.alignment = align_center
        c5 = ws2.cell(row=r_cur, column=5, value=prom)
        c5.alignment = align_right
        c5.number_format = "$#,##0.00"

        for ci in range(1, 6):
            obj = ws2.cell(row=r_cur, column=ci)
            obj.font = font_normal
            obj.border = border_thin
            if r_cur % 2 == 0: obj.fill = fill_zebra
        ws2.row_dimensions[r_cur].height = 22
        r_cur += 1

    # Tabla COPEs
    r_cope_s = r_cur + 2
    ws2.merge_cells(f"A{r_cope_s}:E{r_cope_s}")
    ws2[f"A{r_cope_s}"] = "🏢 GASTO Y TICKETS POR CENTRO DE TRABAJO (COPE)"
    ws2[f"A{r_cope_s}"].font = font_section
    ws2[f"A{r_cope_s}"].fill = fill_sub_header
    ws2[f"A{r_cope_s}"].alignment = align_left
    ws2.row_dimensions[r_cope_s].height = 24

    for c_i, h in enumerate(["Centro de Trabajo (COPE)", "Tickets", "Gasto Total (s/IVA)", "% del Total", "Promedio por Ticket"], 1):
        cell = ws2.cell(row=r_cope_s+1, column=c_i, value=h)
        cell.font = font_th
        cell.fill = fill_th_verde
        cell.alignment = align_center
        cell.border = border_thin
    ws2.row_dimensions[r_cope_s+1].height = 26

    r_cur2 = r_cope_s + 2
    for cp_nom, cp_data in sorted(cope_map.items(), key=lambda x: x[1]["monto"], reverse=True):
        m = cp_data["monto"]
        c = cp_data["count"]
        pct = (m / tot_gastado) * 100
        prom = m / c if c > 0 else 0

        c1 = ws2.cell(row=r_cur2, column=1, value=cp_nom)
        c1.alignment = align_left
        c2 = ws2.cell(row=r_cur2, column=2, value=c)
        c2.alignment = align_center
        c3 = ws2.cell(row=r_cur2, column=3, value=m)
        c3.alignment = align_right
        c3.number_format = "$#,##0.00"
        c4 = ws2.cell(row=r_cur2, column=4, value=f"{pct:.2f} %")
        c4.alignment = align_center
        c5 = ws2.cell(row=r_cur2, column=5, value=prom)
        c5.alignment = align_right
        c5.number_format = "$#,##0.00"

        for ci in range(1, 6):
            obj = ws2.cell(row=r_cur2, column=ci)
            obj.font = font_normal
            obj.border = border_thin
            if r_cur2 % 2 == 0: obj.fill = fill_zebra
        ws2.row_dimensions[r_cur2].height = 22
        r_cur2 += 1

    for col in ws2.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(c.value or '')) for c in col)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 20)
    ws2.column_dimensions['A'].width = 32

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Reporte_Seccion_Reportes_{ts}.xlsx"

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )
