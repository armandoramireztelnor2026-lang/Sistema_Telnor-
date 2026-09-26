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
            import re
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

    # Precalcular COPEs de los reportes para búsqueda rápida
    reporte_a_cope = {str(r.get("id")): r.get("cope", "") for r in todos_reportes}

    # 2. Asignar nombres al ticket
    import re as _re
    for f in todos_combinados:
        cope_f = f.get('cope', '')
        
        # Si no tiene COPE (como las facturas), extraerlo del reporte original
        if not cope_f:
            r_id = f.get("id_reporte") or f.get("numero_reporte")
            if not r_id:
                retro = f.get("retro", "")
                match = _re.search(r"\[TICKET:(.*?)\]", retro)
                if match:
                    r_id = match.group(1).strip()
            if r_id:
                cope_f = reporte_a_cope.get(str(r_id), "")

        sup_nombre = cope_a_sup.get(cope_f, "No asignado")
        admin_nombre = cope_a_admin.get(cope_f, "No asignado")
        
        f['supervisor_nombre'] = sup_nombre
        f['administrador_nombre'] = admin_nombre
        f['jefatura_nombre'] = nombre_jefatura
    
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
