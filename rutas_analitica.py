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

@analitica_bp.route('/api/analitica/tops', methods=['GET'])
def analitica_tops():
    from collections import Counter
    import datetime
    
    reportes = leer_json('reportes.json').get('reportes', [])
    facturas = leer_json('facturas.json').get('facturas', [])
    
    # 1. Top 5 unidades con mas tiempo en taller
    # (estado no archivado y entregado != 'Sí' y no cancelado)
    unidades_tiempo = []
    now = datetime.datetime.now()
    for f in facturas:
        if f.get('estado') not in ['Archivado', 'Cancelado_Cotizacion_Cara', 'Rechazado', 'Eliminado'] and f.get('entregado') != 'Sí':
            if f.get('timestamp_aprobacion'):
                try:
                    dt = datetime.datetime.strptime(f['timestamp_aprobacion'], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    dt = now
            elif f.get('timestamp'):
                try:
                    dt = datetime.datetime.strptime(f['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    dt = now
            else:
                dt = now
                
            days = (now - dt).days
            if days < 0: days = 0
            
            # Find unity eco
            unidad_eco = "N/A"
            for r in reportes:
                ticket_id = f.get('id_reporte', f.get('numero_reporte', ''))
                if str(r.get('id')) == str(ticket_id):
                    unidad_eco = r.get('unidad', 'N/A')
                    break
            
            unidades_tiempo.append({
                "unidad": unidad_eco,
                "dias": days,
                "taller": f.get('proveedor', 'N/A')
            })
            
    unidades_tiempo.sort(key=lambda x: x['dias'], reverse=True)
    top_tiempo_taller = unidades_tiempo[:5]
    
    # 2. Top 5 Choferes con más reportes
    choferes_count = Counter()
    for r in reportes:
        e = r.get('empleado')
        if e and e != 'N/A':
            choferes_count[e] += 1
    top_choferes = [{"nombre": k, "cantidad": v} for k, v in choferes_count.most_common(5)]
    
    # 3. Top 5 Unidades con más averías (reportes)
    unidades_count = Counter()
    for r in reportes:
        u = r.get('unidad')
        if u and u != 'N/A':
            unidades_count[u] += 1
    top_unidades_averias = [{"unidad": k, "cantidad": v} for k, v in unidades_count.most_common(5)]
    
    # 4. Top 5 COPEs con más reportes
    copes_count = Counter()
    for r in reportes:
        c = r.get('cope')
        if c and c != 'N/A':
            copes_count[c] += 1
    top_copes = [{"cope": k, "cantidad": v} for k, v in copes_count.most_common(5)]
    
    # 5. Top 5 Talleres que más facturan (Suma de precios)
    talleres_dinero = {}
    for f in facturas:
        p = f.get('proveedor')
        if p and p != 'N/A':
            precio = float(f.get('precio_estimado', f.get('precio', 0)))
            talleres_dinero[p] = talleres_dinero.get(p, 0) + precio
            
    sorted_dinero = sorted(talleres_dinero.items(), key=lambda x: x[1], reverse=True)
    top_talleres_dinero = [{"nombre": k, "total": round(v, 2)} for k, v in sorted_dinero[:5]]

    return jsonify({
        "status": "success",
        "top_tiempo_taller": top_tiempo_taller,
        "top_choferes": top_choferes,
        "top_unidades_averias": top_unidades_averias,
        "top_copes": top_copes,
        "top_talleres_dinero": top_talleres_dinero
    })
