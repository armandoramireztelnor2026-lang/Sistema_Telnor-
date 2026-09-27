import json

with open('facturas.json','r',encoding='utf-8') as file:
    data = json.load(file)
facturas = data.get('facturas',[])
print(f'Total facturas: {len(facturas)}')
for fac in facturas:
    print(f"  ID: {fac.get('id')} | estado: {fac.get('estado')} | is_unassigned: {fac.get('is_unassigned')} | timestamp: {fac.get('timestamp')} | fecha: {fac.get('fecha')}")

with open('reportes.json','r',encoding='utf-8') as file:
    data2 = json.load(file)
reportes = data2.get('reportes',[])
print(f'Total reportes: {len(reportes)}')
for rep in reportes:
    print(f"  ID: {rep.get('id')} | estado: {rep.get('estado')}")
