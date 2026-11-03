import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from notificaciones import obtener_credenciales_correo
from rutas_configuracion import obtener_configuracion, calcular_metricas_presupuesto

client = app.test_client()

with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'jefatura_admin',
        'rol': 'administracion',
        'datos_perfil': {
            'nombre': 'Jefe de Operaciones Telnor',
            'subrol': 'Jefatura'
        }
    }

print("=== 1. TEST CORREO ACTIVAR / DESACTIVAR ===")
# Backup configuracion_sistema.json
with open('configuracion_sistema.json', 'r', encoding='utf-8') as f:
    conf_backup = f.read()

try:
    # 1.1 Agregar segunda cuenta
    res_add = client.post('/api/configuracion/correo/agregar', json={
        'nombre': 'Secundaria Respaldo',
        'correo': 'respaldo@telnor.com',
        'codigo': 'respaldopass1234',
        'servidor_smtp': 'smtp.gmail.com',
        'puerto_smtp': 587,
        'activar': False
    })
    assert res_add.status_code == 200
    print("1.1 Cuenta secundaria agregada OK")

    # 1.2 Activar cuenta secundaria
    res_act = client.post('/api/configuracion/correo/activar', json={'correo': 'respaldo@telnor.com'})
    assert res_act.status_code == 200
    assert res_act.get_json()['correo_activo'] == 'respaldo@telnor.com'
    creds = obtener_credenciales_correo()
    assert creds[0] == 'respaldo@telnor.com'
    print("1.2 Cuenta secundaria activada como emisor OK")

    # 1.3 Desactivar cuenta
    res_desact = client.post('/api/configuracion/correo/desactivar', json={'correo': 'respaldo@telnor.com'})
    assert res_desact.status_code == 200
    assert res_desact.get_json()['envio_automatico_activo'] == False
    creds_desact = obtener_credenciales_correo()
    assert creds_desact[0] is None, f"Creds should be None when deactivated, got {creds_desact[0]}"
    print("1.3 Cuenta desactivada y envíos pausados OK")

    # 1.4 Reactivar cuenta principal
    res_react = client.post('/api/configuracion/correo/activar', json={'correo': 'armandoramireztelnor2026@gmail.com'})
    assert res_react.status_code == 200
    assert res_react.get_json()['correo_activo'] == 'armandoramireztelnor2026@gmail.com'
    print("1.4 Cuenta principal reactivada OK")

finally:
    with open('configuracion_sistema.json', 'w', encoding='utf-8') as f:
        f.write(conf_backup)
    print("configuracion_sistema.json restaurado.")

print("\n=== 2. TEST PRESUPUESTO INSUFICIENTE BLOQUEA APROBACIÓN ===")
with open('facturas.json', 'r', encoding='utf-8') as f:
    facturas_backup = f.read()

try:
    # Set presupuesto total en 10,000 y comprometido en 9,500 (saldo disponible 500)
    conf = obtener_configuracion()
    conf['presupuesto_total'] = 10000.0
    with open('configuracion_sistema.json', 'w', encoding='utf-8') as f:
        json.dump(conf, f, indent=4)

    # Crear ticket de prueba con precio 8,000 (excede el saldo restante de 500)
    data_fac = json.loads(facturas_backup)
    test_ticket = {
        "id": "TICKET_PRESUPUESTO_TEST",
        "unidad": "8090-8888",
        "precio": 8000.0,
        "estado": "pendiente",
        "aprobado_admin": False,
        "aprobado_corp": False,
        "cotizaciones": [{"precio": 8000.0, "numero_orden": "ORD-TEST-1"}]
    }
    data_fac['facturas'].append(test_ticket)
    with open('facturas.json', 'w', encoding='utf-8') as f:
        json.dump(data_fac, f, indent=4)

    # Supervisor intenta aprobar la cotización
    res_aprob = client.post('/api/facturas/confirmar_admin', data={
        'id': 'TICKET_PRESUPUESTO_TEST',
        'numero_orden[]': ['ORD-TEST-1'],
        'numero_cotizacion[]': ['COT-TEST-1']
    })
    print(f"Status aprobación cuando excede presupuesto: {res_aprob.status_code}")
    json_aprob = res_aprob.get_json()
    print("Mensaje:", json_aprob.get('message'))
    assert res_aprob.status_code == 400
    assert "Presupuesto Insuficiente" in json_aprob.get('message')
    print("2.1 Bloqueo por presupuesto insuficiente verificado con éxito!")

    print("\n=== 3. TEST RESETEAR PRESUPUESTO UTILIZADO ===")
    res_reset = client.post('/api/configuracion/presupuesto/resetear')
    assert res_reset.status_code == 200
    data_reset = res_reset.get_json()
    print("Mensaje reset:", data_reset.get('message'))
    print("Presupuesto restante después del reset:", data_reset['presupuesto']['presupuesto_restante'])
    assert data_reset['presupuesto']['dinero_comprometido'] == 0.0
    assert data_reset['presupuesto']['presupuesto_restante'] == 10000.0
    print("3.1 Reset de presupuesto verificado con éxito!")

    # Ahora que el presupuesto se reseteó a 10,000 disponible, la cotización de 8,000 SÍ cabe y se aprueba
    res_aprob_ok = client.post('/api/facturas/confirmar_admin', data={
        'id': 'TICKET_PRESUPUESTO_TEST',
        'numero_orden[]': ['ORD-TEST-1'],
        'numero_cotizacion[]': ['COT-TEST-1']
    })
    print(f"Status aprobación tras reset: {res_aprob_ok.status_code}")
    assert res_aprob_ok.status_code == 200
    print("3.2 Aprobación tras reset exitosa!")

finally:
    with open('facturas.json', 'w', encoding='utf-8') as f:
        f.write(facturas_backup)
    with open('configuracion_sistema.json', 'w', encoding='utf-8') as f:
        f.write(conf_backup)
    print("Archivos restaurados.")

print("\n==========================================")
print("TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
print("==========================================")

