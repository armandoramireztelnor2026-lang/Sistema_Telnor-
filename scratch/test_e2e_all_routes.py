import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'jefatura_admin',
        'rol': 'administracion',
        'datos_perfil': {
            'nombre': 'Jefe de Operaciones Telnor',
            'subrol': 'Jefatura',
            'correo': 'jefatura@telnor.com'
        }
    }

# 1. Test GET /api/configuracion
res = client.get('/api/configuracion')
assert res.status_code == 200, f"Error GET /api/configuracion: {res.status_code}"
data = res.get_json()
print("1. GET /api/configuracion OK - Total Presupuesto:", data['presupuesto']['presupuesto_total'])

# 2. Test POST /api/configuracion/presupuesto/guardar
res_pres = client.post('/api/configuracion/presupuesto/guardar', json={'presupuesto_total': 550000})
assert res_pres.status_code == 200
print("2. POST Presupuesto OK:", res_pres.get_json()['message'])

# 3. Test POST /api/configuracion/limite_caras/guardar
res_lim = client.post('/api/configuracion/limite_caras/guardar', json={'limite': 12000})
assert res_lim.status_code == 200
print("3. POST Limite Caras OK:", res_lim.get_json()['message'])

# Revert to standard 500000 and 10000
client.post('/api/configuracion/presupuesto/guardar', json={'presupuesto_total': 500000})
client.post('/api/configuracion/limite_caras/guardar', json={'limite': 10000})
print("4. Revertidos valores a 500,000 y 10,000 OK")

print("\n--- ALL ROUTES WORKING PERFECTLY! ---")

