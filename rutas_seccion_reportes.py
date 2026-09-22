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

    reportes_data = leer_json('reportes.json')
    facturas_data = leer_json('facturas.json')
    
    todos_reportes = reportes_data.get("reportes", [])
    todas_facturas = facturas_data.get("facturas", [])
    
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
    
    # 1. Mapeo: proveedor -> ciudad
    prov_a_ciudad = {}
    for u in usuarios_list:
        if u.get('rol') == 'proveedores':
            nombre_prov = u.get('datos_perfil', {}).get('nombre_proveedor')
            ciudad_prov = u.get('datos_perfil', {}).get('ciudad')
            if nombre_prov and ciudad_prov:
                prov_a_ciudad[nombre_prov] = ciudad_prov

    # 2. Mapeo: ciudad -> nombre de supervisor, administrador y jefatura
    ciudad_a_sup = {}
    ciudad_a_admin = {}
    ciudad_a_jefatura = {}
    for u in usuarios_list:
        if u.get('rol') == 'administracion':
            subrol = u.get('datos_perfil', {}).get('subrol')
            ciudad = u.get('datos_perfil', {}).get('ciudad', '')
            nombres = u.get('datos_perfil', {}).get('nombres', '')
            apellido_pat = u.get('datos_perfil', {}).get('apellido_paterno', '')
            apellido_mat = u.get('datos_perfil', {}).get('apellido_materno', '')
            import re
            nombre_completo = re.sub(r'\s+', ' ', f"{nombres} {apellido_pat} {apellido_mat}").strip()
            
            ciudad_lower = ciudad.strip().lower()
            if ciudad_lower:
                if subrol == 'Supervisor':
                    ciudad_a_sup[ciudad_lower] = nombre_completo
                elif subrol == 'Administrador':
                    ciudad_a_admin[ciudad_lower] = nombre_completo
                elif subrol == 'Jefatura':
                    ciudad_a_jefatura[ciudad_lower] = nombre_completo

    # Precalcular ciudades de los reportes para busqueda rapida
    reporte_a_ciudad = {str(r.get("id")): r.get("ciudad", "") for r in todos_reportes}

    # 3. Asignar nombres al ticket
    for f in todos_combinados:
        ciudad_f = f.get('ciudad', '')
        
        # Si no tiene ciudad (como las facturas), extraerla del reporte original
        if not ciudad_f:
            r_id = f.get("id_reporte") or f.get("numero_reporte")
            if not r_id:
                retro = f.get("retro", "")
                import re
                match = re.search(r"\[TICKET:(.*?)\]", retro)
                if match:
                    r_id = match.group(1).strip()
            if r_id:
                ciudad_f = reporte_a_ciudad.get(str(r_id), "")
                
        # Fallback al proveedor por si acaso
        if not ciudad_f:
            prov = f.get('proveedor', '')
            ciudad_f = prov_a_ciudad.get(prov, '')

        ciudad_lower = ciudad_f.strip().lower()
        sup_nombre = ciudad_a_sup.get(ciudad_lower, "No asignado")
        admin_nombre = ciudad_a_admin.get(ciudad_lower, "No asignado")
        jefatura_nombre = ciudad_a_jefatura.get(ciudad_lower, "No asignado")
        
        f['supervisor_nombre'] = sup_nombre
        f['administrador_nombre'] = admin_nombre
        f['jefatura_nombre'] = jefatura_nombre
    
    return jsonify({
        "status": "success",
        "facturas": todos_combinados
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
