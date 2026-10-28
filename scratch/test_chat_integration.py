# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = app.test_client()

print("=== INICIANDO PRUEBAS DE INTEGRACIÓN DEL CHAT INTERNO ===")

# 1. Prueba sin autenticación
res = client.get('/api/chat/contactos')
assert res.status_code == 401, f"Esperado 401 sin sesión, obtenido {res.status_code}"
print("OK: Acceso denegado a usuarios no autenticados (401)")

# 2. Prueba como Taller
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov',
        'rol': 'proveedores',
        'datos_perfil': {
            'rol': 'proveedores',
            'nombre_proveedor': 'AUTOPARTES Y MOTORES B.C.',
            'encargado': 'Armando Ramirez'
        }
    }

res = client.get('/api/chat/contactos')
data = res.get_json()
assert data['status'] == 'success'
assert data['mi_rol'] == 'Taller'
contactos = data['contactos']
# Validar que TODOS los contactos permitidos sean exclusivamente 'Supervisor'
for c in contactos:
    assert c['rol'] == 'Supervisor', f"Error: Taller recibió contacto con rol {c['rol']}"
print(f"OK: Taller solo ve Supervisores ({len(contactos)} contactos encontrados)")

# Taller enviando mensaje a Supervisor
res_send = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'Samuel_Giron-RUMN-2026-admin',
    'mensaje': 'Hola Supervisor, ¿ya tiene la autorización del presupuesto?'
})
assert res_send.status_code == 200, f"Error al enviar mensaje: {res_send.get_json()}"
print("OK: Taller envió mensaje con éxito a Supervisor")

# Taller intentando enviar mensaje a otro Taller (prohibido)
res_block = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'GALLEGOS-RUMN-2026-prov',
    'mensaje': 'Mensaje indebido entre talleres'
})
assert res_block.status_code == 403, f"Esperado 403, obtenido {res_block.status_code}"
print("OK: Bloqueo de Taller intentando escribir a otro Taller (403 Forbidden)")

# 3. Prueba como Supervisor
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'Samuel_Giron-RUMN-2026-admin',
        'rol': 'administracion',
        'datos_perfil': {
            'subrol': 'Supervisor',
            'nombres': 'Samuel',
            'apellido_paterno': 'Giron'
        }
    }

# Supervisor revisa mensajes no leidos
res_nl = client.get('/api/chat/no_leidos')
data_nl = res_nl.get_json()
assert data_nl['status'] == 'success'
assert data_nl['total_no_leidos'] >= 1
print(f"OK: Supervisor detecta mensaje no leído ({data_nl['total_no_leidos']} pendientes)")

# Supervisor abre conversacion con Taller (debe marcar como leido)
res_conv = client.get('/api/chat/conversacion/AUTOPARTESYMOTORESB.C.-RUMN-2026-prov')
data_conv = res_conv.get_json()
assert data_conv['status'] == 'success'
assert len(data_conv['mensajes']) >= 1
print("OK: Supervisor abrió conversación y los mensajes se leyeron correctamente")

# Supervisor responde al Taller
res_resp = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov',
    'mensaje': 'Enterado, la cotización de $8,500 ya fue autorizada en el sistema.'
})
assert res_resp.status_code == 200
print("OK: Supervisor respondió al Taller con éxito")

# Supervisor escribe a Administrador (permitido)
res_sup_adm = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'ManuelAlejandro_Marquez-RUMN-2026-admin',
    'mensaje': 'Estimado Admin, favor de revisar el número de orden del ticket.'
})
assert res_sup_adm.status_code == 200
print("OK: Supervisor envió mensaje a Administrador con éxito")

# 4. Prueba como Administrador
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'ManuelAlejandro_Marquez-RUMN-2026-admin',
        'rol': 'administracion',
        'datos_perfil': {
            'subrol': 'Administrador',
            'nombres': 'Manuel Alejandro',
            'apellido_paterno': 'Marquez'
        }
    }

# Administrador intenta escribir a Taller (prohibido según la regla)
res_adm_taller = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov',
    'mensaje': 'Hola Taller directo'
})
assert res_adm_taller.status_code == 403
print("OK: Administrador bloqueado para escribir directamente a Taller (403 Forbidden)")

# Administrador escribe a Jefatura (permitido)
res_adm_jef = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'EfrainHumberto_Perusquia -RUMN-2026-admin',
    'mensaje': 'Jefatura, orden 4452 validada.'
})
assert res_adm_jef.status_code == 200
print("OK: Administrador envió mensaje a Jefatura con éxito")

# 5. Prueba como Corporativos
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'Alejandro_Gimenez-RUMN-2026-corp',
        'rol': 'corporativos',
        'datos_perfil': {
            'rol': 'corporativos',
            'nombres': 'Luisa Alejandra',
            'apellido_paterno': 'Gimenez'
        }
    }

# Corporativos solo puede escribir a Supervisores
res_corp_sup = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'Samuel_Giron-RUMN-2026-admin',
    'mensaje': 'Supervisor, autorizada la cotización mayor de 10k.'
})
assert res_corp_sup.status_code == 200
print("OK: Corporativos escribió a Supervisor con éxito")

# Corporativos intenta escribir a Taller (prohibido)
res_corp_taller = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov',
    'mensaje': 'Hola taller'
})
assert res_corp_taller.status_code == 403
print("OK: Corporativos bloqueado para escribir a Taller (403 Forbidden)")

# 6. Prueba como Jefatura (puede escribir a todos)
with client.session_transaction() as sess:
    sess['usuario'] = {
        'usuario': 'EfrainHumberto_Perusquia -RUMN-2026-admin',
        'rol': 'administracion',
        'datos_perfil': {
            'subrol': 'Jefatura',
            'nombres': 'Efrain Humberto',
            'apellido_paterno': 'Perusquia'
        }
    }

# Jefatura escribe a Taller
res_jef_taller = client.post('/api/chat/enviar', json={
    'receptor_usuario': 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov',
    'mensaje': 'Aviso de Jefatura sobre tiempos de entrega.'
})
assert res_jef_taller.status_code == 200
print("OK: Jefatura escribió a Taller con éxito (permiso total)")

print("\n=== TODAS LAS PRUEBAS DE INTEGRACIÓN DEL CHAT PASARON EXITOSAMENTE (100%) ===")
