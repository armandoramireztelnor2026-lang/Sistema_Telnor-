# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_supervisor_to_supervisor():
    print("=== INICIANDO PRUEBA DE SUPERVISOR A SUPERVISOR ===")
    
    sup1 = 'Samuel_Giron-RUMN-2026-admin'
    sup2 = 'Oscar_Heredia -RUMN-2026-admin'
    sup3 = 'JesusAlfredo_Reyes-RUMN-2026-admin'

    with app.test_client() as client:
        # 1. Sesión como Supervisor 1
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": sup1,
                "rol": "administracion",
                "datos_perfil": {
                    "nombre": "Samuel Giron",
                    "subrol": "Supervisor"
                }
            }

        # 2. Consultar lista de contactos
        res = client.get('/api/chat/contactos')
        assert res.status_code == 200
        contactos = res.get_json()['contactos']
        contactos_ids = [c['usuario'] for c in contactos]

        assert sup1 not in contactos_ids, "El supervisor no debe verse a sí mismo"
        assert sup2 in contactos_ids, "El supervisor debe ver a otros supervisores (sup2)"
        assert sup3 in contactos_ids, "El supervisor debe ver a otros supervisores (sup3)"
        print(f"OK: Supervisor 1 ve a otros supervisores ({sup2}, {sup3})")

        # 3. Supervisor 1 envía mensaje a Supervisor 2
        res_envio = client.post('/api/chat/enviar', json={
            "receptor_usuario": sup2,
            "mensaje": "Hola colega Óscar, ¿cómo va la revisión de las unidades de Mexicali?"
        })
        assert res_envio.status_code == 200, f"Error al enviar: {res_envio.data}"
        msg = res_envio.get_json()['mensaje']
        print(f"OK: Mensaje enviado exitosamente de {sup1} a {sup2} (ID: {msg['id']})")

        # 4. Supervisor 2 abre la conversación y responde
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": sup2,
                "rol": "administracion",
                "datos_perfil": {
                    "nombre": "Oscar Heredia",
                    "subrol": "Supervisor"
                }
            }

        res_conv = client.get(f'/api/chat/conversacion/{sup1}')
        assert res_conv.status_code == 200
        mensajes = res_conv.get_json()['mensajes']
        ultimo = mensajes[-1]
        assert ultimo['emisor_usuario'] == sup1
        assert ultimo['leido'] is True
        print("OK: Supervisor 2 leyó el mensaje correctamente")

        # Supervisor 2 responde
        res_resp = client.post('/api/chat/enviar', json={
            "receptor_usuario": sup1,
            "mensaje": "Hola Samuel, todo en orden, ya firmé las órdenes de salida.",
            "respuesta_a": {
                "id": ultimo['id'],
                "emisor_nombre": "Samuel Giron",
                "mensaje": ultimo['mensaje']
            }
        })
        assert res_resp.status_code == 200
        print("OK: Supervisor 2 respondió al Supervisor 1 exitosamente")

    print("=== PRUEBA DE SUPERVISOR A SUPERVISOR EXITOSA (100%) ===")

if __name__ == '__main__':
    test_supervisor_to_supervisor()

