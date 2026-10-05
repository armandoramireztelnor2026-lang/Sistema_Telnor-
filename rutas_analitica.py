from flask import Blueprint, jsonify, request
import json
import os
import datetime
from collections import Counter
import re

analitica_bp = Blueprint("analitica_bp", __name__)

def leer_json(archivo):
    if not os.path.exists(archivo): return {}
    with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)

def filtrar_por_anio(reportes, facturas, year_str):
    if not year_str or year_str == 'Todos' or year_str == '':
        return reportes, facturas
        
    rep_filtrados = []
    ticket_years = {}
    
    for r in reportes:
        y = str(r.get('fecha', ''))[:4]
        if not y and r.get('timestamp'):
            y = str(r.get('timestamp', ''))[:4]
            
        ticket_id = str(r.get('id', ''))
        ticket_years[ticket_id] = y
        
        if y == year_str:
            rep_filtrados.append(r)
            
    fact_filtradas = []
    for f in facturas:
        ticket_id = str(f.get('id_reporte', f.get('numero_reporte', 'N/A')))
        match = re.search(r"\[TICKET:(.*?)\]", f.get('retro', ''))
        if match: ticket_id = match.group(1).strip()
        
        y = ticket_years.get(ticket_id)
        if not y and f.get('timestamp'):
            y = str(f.get('timestamp', ''))[:4]
            
        if y == year_str:
            fact_filtradas.append(f)
            
    return rep_filtrados, fact_filtradas

@analitica_bp.route('/api/analitica/ultimos', methods=['GET'])
def analitica_ultimos():
    year = request.args.get('year', 'Todos')
    usuarios_data = leer_json('usuarios.json').get('usuarios', [])
    reportes_raw = leer_json('reportes.json').get('reportes', [])
    facturas_raw = leer_json('facturas.json').get('facturas', [])
    
    reportes, facturas = filtrar_por_anio(reportes_raw, facturas_raw, year)

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
        retro = f.get('retro', '')
        ticket_id = f.get('id_reporte', f.get('numero_reporte', 'N/A'))
        match = re.search(r"\[TICKET:(.*?)\]", retro)
        if match: ticket_id = match.group(1).strip()
        
        chofer = 'N/A'
        resp = {'Administrador': 'N/A', 'Supervisor': 'N/A', 'Jefatura': 'N/A'}
        for r in reportes_raw:
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

    ultima_reparada = None
    for f in reversed(facturas):
        if f.get('estado') == 'Reparado' or f.get('entregado') == 'Sí':
            ultima_reparada = extract_factura_info(f)
            break
            
    ultima_entregada = None
    for f in reversed(facturas):
        if f.get('entregado') == 'Sí':
            ultima_entregada = extract_factura_info(f)
            break
            
    ultima_rechazada = None
    for f in reversed(facturas):
        if 'Rechazad' in f.get('estado', '') or 'Cancelado' in f.get('estado', ''):
            ultima_rechazada = extract_factura_info(f)
            break
            
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
    year = request.args.get('year', 'Todos')
    reportes_raw = leer_json('reportes.json').get('reportes', [])
    facturas_raw = leer_json('facturas.json').get('facturas', [])
    
    reportes, facturas = filtrar_por_anio(reportes_raw, facturas_raw, year)
    
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
            
            unidad_eco = "N/A"
            for r in reportes_raw:
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
    
    choferes_count = Counter()
    for r in reportes:
        e = r.get('empleado')
        if e and e != 'N/A':
            choferes_count[e] += 1
    top_choferes = [{"nombre": k, "cantidad": v} for k, v in choferes_count.most_common(5)]
    
    unidades_count = Counter()
    for r in reportes:
        u = r.get('unidad')
        if u and u != 'N/A':
            unidades_count[u] += 1
    top_unidades_averias = [{"unidad": k, "cantidad": v} for k, v in unidades_count.most_common(5)]
    
    copes_count = Counter()
    for r in reportes:
        c = r.get('cope')
        if c and c != 'N/A':
            copes_count[c] += 1
    top_copes = [{"cope": k, "cantidad": v} for k, v in copes_count.most_common(5)]
    
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

@analitica_bp.route('/api/analitica/charts', methods=['GET'])
def analitica_charts():
    year = request.args.get('year', 'Todos')
    reportes_raw = leer_json('reportes.json').get('reportes', [])
    facturas_raw = leer_json('facturas.json').get('facturas', [])
    
    reportes, facturas = filtrar_por_anio(reportes_raw, facturas_raw, year)
    
    estados_count = Counter()
    for f in facturas:
        st = f.get('estado', 'Desconocido')
        if st == 'Pendiente de Revisión': st = 'Pendiente'
        estados_count[st] += 1
        
    factura_ids = {str(f.get('id_reporte', f.get('numero_reporte'))) for f in facturas}
    for r in reportes:
        if str(r.get('id')) not in factura_ids:
            estados_count['Sin Asignar'] += 1
            
    mant_count = Counter()
    for r in reportes:
        m = r.get('mantenimiento', 'Desconocido')
        mant_count[m] += 1
        
    copes_count = Counter()
    for r in reportes:
        c = r.get('cope', 'Desconocido')
        copes_count[c] += 1

    meses_count = Counter()
    for r in reportes:
        fecha = r.get('fecha', '')
        if len(fecha) >= 7:
            mes = fecha[:7] # YYYY-MM
            meses_count[mes] += 1
    
    talleres_dinero = {}
    for f in facturas:
        p = f.get('proveedor')
        if p and p != 'N/A':
            precio = float(f.get('precio_estimado', f.get('precio', 0)))
            talleres_dinero[p] = talleres_dinero.get(p, 0) + precio
    top_dinero = sorted(talleres_dinero.items(), key=lambda x: x[1], reverse=True)[:5]
    
    marcas_count = Counter()
    for r in reportes:
        m = r.get('marca', 'Desconocido')
        marcas_count[m] += 1

    return jsonify({
        "status": "success",
        "pie_estados": {"labels": list(estados_count.keys()), "data": list(estados_count.values())},
        "pie_mantenimiento": {"labels": list(mant_count.keys()), "data": list(mant_count.values())},
        "pie_copes": {"labels": list(copes_count.keys()), "data": list(copes_count.values())},
        "bar_meses": {"labels": list(meses_count.keys()), "data": list(meses_count.values())},
        "bar_talleres": {"labels": [k for k, v in top_dinero], "data": [v for k, v in top_dinero]},
        "bar_marcas": {"labels": [k for k, v in marcas_count.most_common(5)], "data": [v for k, v in marcas_count.most_common(5)]}
    })
