import json

def load(f):
    with open(f, 'r', encoding='utf-8') as file:
        return json.load(file)

reportes = load('reportes.json').get('reportes', [])
for r in reportes:
    print(f"REP | ID: {r.get('id')} | Unidad: {r.get('unidad')} | COPE: {r.get('cope')} | Estado: {r.get('estado')}")

print('-' * 20)

facturas = load('facturas.json').get('facturas', [])
for f in facturas:
    print(f"FAC | ID: {f.get('id')} | Unidad: {f.get('unidad')} | COPE: {f.get('cope')} | Estado: {f.get('estado')} | NumRep: {f.get('numero_reporte')} | IdRep: {f.get('id_reporte')}")
