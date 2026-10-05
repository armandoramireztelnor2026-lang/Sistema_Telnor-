from flask import Blueprint, jsonify
import json
import os

analitica_bp = Blueprint("analitica_bp", __name__)

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)

@analitica_bp.route('/api/analitica/ultimos', methods=['GET'])
def analitica_ultimos():
    usuarios_data = leer_json('usuarios.json').get('usuarios', [])
    reportes = leer_json('reportes.json').get('reportes', [])
    facturas = leer_json('facturas.json').get('facturas', [])

    cope_map = {}
    for u in usuarios_data:
        if u.get('rol') == 'administracion':
            dp = u.get('datos_perfil', {})
            cope = dp.get('cope')
            subrol = dp.get('subrol')
            nombres = dp.get('nombres', '')
            apellidos = dp.get('apellido_paterno', '')
            name = f"{nombres} {apellidos}".strip()
            
            copes = [cope] if cope else []
            copes.extend(dp.get('copes_asignados', []))
            
            for c in copes:
                if c not in cope_map:
                    cope_map[c] = {'Administrador': 'N/A', 'Supervisor': 'N/A', 'Jefatura': 'N/A'}
                if subrol in cope_map[c]:
                    cope_map[c][subrol] = name

    def get_responsables(cope):
        return cope_map.get(cope, {'Administrador': 'N/A', 'Supervisor': 'N/A', 'Jefatura': 'N/A'})

    ultimo_llegado = None
    if reportes:
        r = reportes[-1]
        resp = get_responsables(r.get('cope', ''))
        ultimo_llegado = {
            "ticket": r.get('id', 'N/A'),
            "chofer": r.get('empleado', 'N/A'),
            "administrador": resp.get('Administrador', 'N/A'),
            "supervisor": resp.get('Supervisor', 'N/A'),
            "jefatura": resp.get('Jefatura', 'N/A')
        }

    def extract_factura_info(f):
        import re
        retro = f.get('retro', '')
        ticket_id = f.get('id_reporte', f.get('numero_reporte', 'N/A'))
        match = re.search(r"\[TICKET:(.*?)\]", retro)
        if match: ticket_id = match.group(1).strip()
        
        chofer = 'N/A'
        resp = {'Administrador': 'N/A', 'Supervisor': 'N/A', 'Jefatura': 'N/A'}
        for r in reportes:
            if str(r.get('id')) == str(ticket_id):
                chofer = r.get('empleado', 'N/A')
                resp = get_responsables(r.get('cope', ''))
                break
                
        return {
            "ticket": ticket_id,
            "chofer": chofer,
            "taller": f.get('proveedor', 'N/A'),
            "administrador": resp.get('Administrador', 'N/A'),
            "supervisor": resp.get('Supervisor', 'N/A'),
            "jefatura": resp.get('Jefatura', 'N/A')
        }

    ultimo_finalizado = None
    for f in reversed(facturas):
        if f.get('estado') == 'Archivado' or (f.get('liberado_admin') == True and f.get('factura_cargada')):
            ultimo_finalizado = extract_factura_info(f)
            break

    ultimo_asignado = None
    if facturas:
        ultimo_asignado = extract_factura_info(facturas[-1])

    ultimo_caro = None
    for f in reversed(facturas):
        p = float(f.get('precio_estimado', f.get('precio', 0)))
        if p >= 10001:
            ultimo_caro = extract_factura_info(f)
            break

    # Ultima Unidad Reparada
    ultima_reparada = None
    for f in reversed(facturas):
        if f.get('estado') == 'Reparado' or f.get('entregado') == 'Sí':
            ultima_reparada = extract_factura_info(f)
            break
            
    # Ultima Unidad Entregada
    ultima_entregada = None
    for f in reversed(facturas):
        if f.get('entregado') == 'Sí':
            ultima_entregada = extract_factura_info(f)
            break
            
    # Ultima Cotizacion Rechazada / Cancelada
    ultima_rechazada = None
    for f in reversed(facturas):
        if 'Rechazad' in f.get('estado', '') or 'Cancelado' in f.get('estado', ''):
            ultima_rechazada = extract_factura_info(f)
            break
            
    # Ultima Factura Fiscal Cargada
    ultima_fiscal = None
    for f in reversed(facturas):
        if f.get('factura_cargada') == True:
            ultima_fiscal = extract_factura_info(f)
            break

    return jsonify({
        "status": "success",
        "ultimo_llegado": ultimo_llegado,
        "ultimo_finalizado": ultimo_finalizado,
        "ultimo_asignado": ultimo_asignado,
        "ultimo_caro": ultimo_caro,
        "ultima_reparada": ultima_reparada,
        "ultima_entregada": ultima_entregada,
        "ultima_rechazada": ultima_rechazada,
        "ultima_fiscal": ultima_fiscal
    })
