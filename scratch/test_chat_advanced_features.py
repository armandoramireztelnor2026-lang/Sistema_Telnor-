# -*- coding: utf-8 -*-
import sys
import os
import json

# Agregar path raiz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from rutas_chat import CHAT_FILE

def test_chat_advanced():
    print("=== INICIANDO PRUEBAS DE RESPONDER, ELIMINAR Y DETALLES DEL CHAT ===")
    
    supervisor_user = 'Samuel_Giron-RUMN-2026-admin'
    taller_user = 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov'
    taller_ajeno = 'AYALAPULIDOESPERANZA-RUMN-2026-prov'

    with app.test_client() as client:
        # 1. Simular sesión de Supervisor
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": supervisor_user,
                "rol": "administracion",
                "datos_perfil": {
                    "nombre": "Samuel Giron",
                    "subrol": "Supervisor"
                }
            }

        # Supervisor envía un mensaje inicial al Taller
        res = client.post('/api/chat/enviar', json={
            "receptor_usuario": taller_user,
            "mensaje": "Mensaje original: ¿En cuánto tiempo queda la unidad 104?"
        })
        assert res.status_code == 200, f"Error al enviar mensaje inicial: {res.data}"
        msg1 = res.get_json()['mensaje']
        msg1_id = msg1['id']
        print(f"OK: Supervisor envió mensaje 1 (ID: {msg1_id})")

        # 2. Simular sesión de Taller para responder
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": taller_user,
                "rol": "proveedores",
                "datos_perfil": {
                    "nombre_proveedor": "AUTOPARTES Y MOTORES B.C.",
                    "encargado": "Carlos Taller"
                }
            }

        # Taller abre la conversación (marca msg1 como leído y registra fecha_leido)
        res_conv = client.get(f'/api/chat/conversacion/{supervisor_user}')
        assert res_conv.status_code == 200
        mensajes_recibidos = res_conv.get_json()['mensajes']
        msg1_actualizado = next(m for m in mensajes_recibidos if m['id'] == msg1_id)
        assert msg1_actualizado['leido'] is True, "El mensaje debería estar leído"
        assert 'fecha_leido' in msg1_actualizado, "Debe tener fecha_leido"
        print(f"OK: Mensaje marcado como leído con fecha: {msg1_actualizado.get('fecha_leido_completa')}")

        # Taller RESPONDE al mensaje del Supervisor (Respuesta con cita)
        res_reply = client.post('/api/chat/enviar', json={
            "receptor_usuario": supervisor_user,
            "mensaje": "Queda lista hoy a las 5:00 PM, ya se cambiaron las balatas.",
            "respuesta_a": {
                "id": msg1_id,
                "emisor_nombre": "Samuel Giron",
                "mensaje": "Mensaje original: ¿En cuánto tiempo queda la unidad 104?"
            }
        })
        assert res_reply.status_code == 200, f"Error al responder: {res_reply.data}"
        msg_reply = res_reply.get_json()['mensaje']
        assert msg_reply['respuesta_a']['id'] == msg1_id, "La respuesta debe incluir la cita al msg1"
        reply_id = msg_reply['id']
        print(f"OK: Taller respondió con cita al mensaje exitosamente (ID: {reply_id})")

        # 3. Probar DETALLES del mensaje
        res_det = client.get(f'/api/chat/mensaje_detalles/{reply_id}')
        assert res_det.status_code == 200, f"Error al consultar detalles: {res_det.data}"
        detalles = res_det.get_json()['detalles']
        assert detalles['emisor_usuario'] == taller_user
        assert detalles['respuesta_a']['emisor_nombre'] == 'Samuel Giron'
        print("OK: Endpoint de detalles retornó la información completa del mensaje")

        # 4. Probar ELIMINACIÓN de mensaje
        # Intentar eliminar con un usuario ajeno (otro taller) debe dar 403
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": taller_ajeno,
                "rol": "proveedores",
                "datos_perfil": { "nombre_proveedor": "Taller Ajeno" }
            }
        res_elim_fail = client.post('/api/chat/eliminar_mensaje', json={ "mensaje_id": reply_id })
        assert res_elim_fail.status_code == 403, "Un usuario ajeno no debe poder eliminar el mensaje"
        print("OK: Bloqueo de eliminación no autorizada (403 Forbidden)")

        # El autor original (taller_user) elimina su mensaje
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": taller_user,
                "rol": "proveedores",
                "datos_perfil": { "nombre_proveedor": "AUTOPARTES Y MOTORES B.C." }
            }
        res_elim_ok = client.post('/api/chat/eliminar_mensaje', json={ "mensaje_id": reply_id })
        assert res_elim_ok.status_code == 200, f"Error al eliminar mensaje propio: {res_elim_ok.data}"
        
        # Verificar que quedó marcado como eliminado en la conversación
        res_conv2 = client.get(f'/api/chat/conversacion/{supervisor_user}')
        mensajes_recibidos2 = res_conv2.get_json()['mensajes']
        msg_reply_post = next(m for m in mensajes_recibidos2 if m['id'] == reply_id)
        assert msg_reply_post['eliminado'] is True, "El mensaje debe tener eliminado = True"
        assert msg_reply_post['mensaje'] == "Este mensaje fue eliminado"
        print("OK: Mensaje eliminado exitosamente y reflejado en la conversación")

    print("\n=== TODAS LAS PRUEBAS DE RESPONDER, ELIMINAR Y DETALLES PASARON AL 100% ===")

if __name__ == '__main__':
    test_chat_advanced()
