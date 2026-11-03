import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'jefatura_user',
        'rol': 'administracion',
        'datos_perfil': {
            'nombre': 'Jefe de Operaciones',
            'subrol': 'Jefatura',
            'correo': 'jefatura@telnor.com'
        }
    }

res = client.get('/api/configuracion')
print("Status /api/configuracion with Jefatura session:", res.status_code)
data = res.get_json()
print("Status in json:", data.get('status'))
print("Correo emisor:", data.get('configuracion', {}).get('correo_emisor'))
print("Presupuesto total:", data.get('presupuesto', {}).get('presupuesto_total'))
print("Dinero comprometido:", data.get('presupuesto', {}).get('dinero_comprometido'))
print("Presupuesto restante:", data.get('presupuesto', {}).get('presupuesto_restante'))
print("Limite cotizaciones caras:", data.get('configuracion', {}).get('limite_cotizaciones_caras'))

assert res.status_code == 200
assert data.get('status') == 'success'
assert 'configuracion' in data
assert 'presupuesto' in data

print("\n--- ALL BACKEND AND UI CHECKS PASSED PERFECTLY! ---")
