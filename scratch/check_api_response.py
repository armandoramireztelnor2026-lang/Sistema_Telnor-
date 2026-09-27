import json, re

def leer_json(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

reportes_data = leer_json('reportes.json')
facturas_data = leer_json('facturas.json')

todos_reportes = reportes_data.get("reportes", [])
todas_facturas = facturas_data.get("facturas", [])

facturas_ids = set()
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

reportes_no_asignados = [r for r in todos_reportes if str(r.get("id")) not in facturas_ids]

print(f"Facturas IDs conocidas: {facturas_ids}")
print(f"Reportes totales: {len(todos_reportes)}")
print(f"Reportes no asignados (is_unassigned): {len(reportes_no_asignados)}")
print(f"Facturas: {len(todas_facturas)}")
print(f"Total combinado que va al frontend: {len(reportes_no_asignados) + len(todas_facturas)}")
for r in reportes_no_asignados:
    print(f"\n  Reporte: {r.get('id')}")
    print(f"  timestamp: {r.get('timestamp')}")
    print(f"  estado: {r.get('estado')}")
    print(f"  cope: {r.get('cope')}")
    print(f"  ciudad: {r.get('ciudad')}")
