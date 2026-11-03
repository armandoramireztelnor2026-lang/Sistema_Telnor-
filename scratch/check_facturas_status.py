import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('facturas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total facturas: {len(data.get('facturas', []))}")
for f in data.get('facturas', [])[:5]:
    print("---")
    print(f"ID: {f.get('id')}, Unidad: {f.get('unidad')}, Precio: {f.get('precio')}, Estado: {f.get('estado')}")
    print(f"aprobado_admin: {f.get('aprobado_admin')}, aprobado_admin_10k: {f.get('aprobado_admin_10k')}, aprobado_corp: {f.get('aprobado_corp')}")
    print(f"liberado_admin: {f.get('liberado_admin')}, reparado: {f.get('reparado')}, entregado: {f.get('entregado')}")

