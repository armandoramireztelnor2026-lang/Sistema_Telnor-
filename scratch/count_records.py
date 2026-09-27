import json

with open('reportes.json', 'r', encoding='utf-8') as f:
    reportes = json.load(f).get('reportes', [])
print(f"Reportes activos: {len(reportes)}")

with open('facturas.json', 'r', encoding='utf-8') as f:
    facturas = json.load(f).get('facturas', [])
print(f"Facturas activas/archivadas: {len(facturas)}")
