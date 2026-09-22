import json
import re

def test():
    with open('usuarios.json', 'r', encoding='utf-8') as f:
        usuarios_list = json.load(f).get('usuarios', [])
        
    with open('reportes.json', 'r', encoding='utf-8') as f:
        todos_reportes = json.load(f).get('reportes', [])
        
    with open('facturas.json', 'r', encoding='utf-8') as f:
        todas_facturas = json.load(f).get('facturas', [])
        
    ciudad_a_sup = {}
    ciudad_a_admin = {}
    for u in usuarios_list:
        if u.get('rol') == 'administracion':
            subrol = u.get('datos_perfil', {}).get('subrol')
            ciudad = u.get('datos_perfil', {}).get('ciudad', '')
            nombres = u.get('datos_perfil', {}).get('nombres', '')
            apellidos = u.get('datos_perfil', {}).get('apellido_paterno', '')
            nombre_completo = f"{nombres} {apellidos}".strip()
            
            ciudad_lower = ciudad.strip().lower()
            if ciudad_lower:
                if subrol == 'Supervisor':
                    ciudad_a_sup[ciudad_lower] = nombre_completo
                elif subrol == 'Administrador':
                    ciudad_a_admin[ciudad_lower] = nombre_completo

    reporte_a_ciudad = {str(r.get("id")): r.get("ciudad", "") for r in todos_reportes}
    print("reporte_a_ciudad:", reporte_a_ciudad)

    for f in todas_facturas:
        ciudad_f = f.get('ciudad', '')
        r_id_debug = ""
        if not ciudad_f:
            r_id = f.get("id_reporte") or f.get("numero_reporte")
            if not r_id:
                retro = f.get("retro", "")
                match = re.search(r"\[TICKET:(.*?)\]", retro)
                if match:
                    r_id = match.group(1).strip()
            r_id_debug = r_id
            if r_id:
                ciudad_f = reporte_a_ciudad.get(str(r_id), "")
                
        ciudad_lower = ciudad_f.strip().lower()
        sup_nombre = ciudad_a_sup.get(ciudad_lower, "No asignado")
        admin_nombre = ciudad_a_admin.get(ciudad_lower, "No asignado")
        print(f"Ticket {f['id']} - r_id: {r_id_debug} -> Ciudad: '{ciudad_f}', Sup: {sup_nombre}, Admin: {admin_nombre}")

test()
