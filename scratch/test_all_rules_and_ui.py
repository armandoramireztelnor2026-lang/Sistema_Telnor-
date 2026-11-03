import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from rutas_facturas import revaluar_cotizaciones_por_limite, obtener_limite_cotizaciones_caras

client = app.test_client()

print("--- 1. Testing Business Rules in revaluar_cotizaciones_por_limite ---")

with open('facturas.json', 'r', encoding='utf-8') as f:
    original_facturas = f.read()

try:
    data = json.loads(original_facturas)
    facturas_list = data.get('facturas', [])

    # Ticket T1: Already working in workshop (Rule 1: Inmutable)
    t1 = {
        "id": "TEST_T1",
        "unidad": "8090-9901",
        "precio": 12000.0,
        "estado": "pendiente",
        "aprobado_admin": True,
        "aprobado_admin_10k": True,
        "aprobado_corp": True,
        "liberado_admin": True,
        "taller_trabajando": True
    }
    # Ticket T2: Expensive ticket, supervisor already approved, waiting for Admin (Rule 3 test)
    t2 = {
        "id": "TEST_T2",
        "unidad": "8090-9902",
        "precio": 11000.0,
        "estado": "pendiente",
        "aprobado_admin": True,
        "aprobado_admin_10k": False,
        "aprobado_corp": False,
        "liberado_admin": None
    }
    # Ticket T3: Non-expensive ticket pending supervisor approval (Rule 2 test)
    t3 = {
        "id": "TEST_T3",
        "unidad": "8090-9903",
        "precio": 9000.0,
        "estado": "pendiente",
        "aprobado_admin": False,
        "aprobado_admin_10k": False,
        "aprobado_corp": True,
        "liberado_admin": None
    }

    facturas_list.extend([t1, t2, t3])
    data['facturas'] = facturas_list
    with open('facturas.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # Test Case A: Increase limit to 15,000
    # Expected:
    # - T1 untouched (Rule 1)
    # - T2 (11,000 < 15,000) was cara waiting for admin, now becomes non-cara -> goes direct to workshop! (Rule 3)
    #   aprobado_corp = True, aprobado_admin_10k = True, liberado_admin = False
    liberados = revaluar_cotizaciones_por_limite(15000.0)
    print(f"Liberados con límite 15,000: {liberados}")
    assert liberados >= 1, "T2 should have been cleared for workshop!"

    with open('facturas.json', 'r', encoding='utf-8') as f:
        d_after = json.load(f)
    t_map = {f['id']: f for f in d_after.get('facturas', [])}

    assert t_map['TEST_T1']['taller_trabajando'] == True, "T1 was modified but shouldn't be!"
    assert t_map['TEST_T2']['aprobado_corp'] == True, "T2 should be aprobado_corp=True"
    assert t_map['TEST_T2']['aprobado_admin_10k'] == True, "T2 should be aprobado_admin_10k=True"
    assert t_map['TEST_T2']['liberado_admin'] == False, "T2 should be liberado_admin=False"
    print("Rule 3 & Rule 1 verified successfully!")

    # Test Case B: Lower limit to 8,000
    # Expected:
    # - T3 (9,000 >= 8,000) was non-cara and now qualifies as cara -> must go to corporativos (Rule 2)
    #   aprobado_corp = False, aprobado_admin_10k = False
    revaluar_cotizaciones_por_limite(8000.0)
    with open('facturas.json', 'r', encoding='utf-8') as f:
        d_after2 = json.load(f)
    t_map2 = {f['id']: f for f in d_after2.get('facturas', [])}
    assert t_map2['TEST_T3']['aprobado_corp'] == False, "T3 should require corporativos with limit 8,000!"
    print("Rule 2 verified successfully!")

finally:
    # Restore original facturas.json
    with open('facturas.json', 'w', encoding='utf-8') as f:
        f.write(original_facturas)
    print("facturas.json restaurado.")

print("\n--- 2. Testing API endpoint POST /api/configuracion/limite_caras/guardar ---")
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'jefatura_admin',
        'rol': 'administracion',
        'datos_perfil': {
            'nombre': 'Jefe de Operaciones Telnor',
            'subrol': 'Jefatura'
        }
    }

res = client.post('/api/configuracion/limite_caras/guardar', json={'limite_cotizaciones_caras': 10000.0})
assert res.status_code == 200
data_res = res.get_json()
print("Endpoint response:", data_res['message'])
assert data_res['status'] == 'success'
assert data_res['limite_cotizaciones_caras'] == 10000.0

print("\n--- 3. Verifying HTML Template (templates/administracion.html) ---")
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    tpl = f.read()

assert 'id="tab-btn-cfg-correo"' in tpl
assert 'id="tab-btn-cfg-presupuesto"' in tpl
assert 'id="tab-btn-cfg-limite"' in tpl
assert 'Paso 1 de 3' not in tpl, "Paso 1 should be gone"
assert 'Paso 2 de 3' not in tpl, "Paso 2 should be gone"
assert 'Paso 3 de 3' not in tpl, "Paso 3 should be gone"
assert 'Siguiente: Control Presupuestal' not in tpl, "Wizard forward button should be gone"
assert 'tabla-cotizaciones-presupuesto' not in tpl, "Budget cotizaciones table should be gone"
assert 'buscar-cotizaciones-presupuesto' not in tpl, "Budget search input should be gone"
assert 'Reglas del Flujo de Cotizaciones' in tpl, "Rules explanation should be present"
assert 'configuraciones_jefatura.js?v=3' in tpl, "Cache buster v=3 should be present"
print("HTML template checks passed!")

print("\n--- 4. Verifying JS confirmations in static/configuraciones_jefatura.js ---")
with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

assert '¿Confirmas que deseas guardar y actualizar las credenciales' in js
assert '¿Confirmas que deseas registrar y agregar la nueva cuenta' in js
assert '¿Confirmas que deseas activar la cuenta' in js
assert '¿Confirmas que deseas establecer el Presupuesto Total' in js
assert '¿Confirmas que deseas establecer el Límite de Cotizaciones Caras' in js
print("All JS confirmations verified!")

print("\n==========================================")
print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("==========================================")
