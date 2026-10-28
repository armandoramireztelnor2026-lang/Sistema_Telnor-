# -*- coding: utf-8 -*-
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import rutas_chat

def test_presence():
    print("=== INICIANDO PRUEBAS DE DETECCIÓN DE PRESENCIA Y ÚLTIMA CONEXIÓN ===")

    user_test = "test_user_presence_123"

    cache = rutas_chat._cargar_presencia()
    if user_test in cache:
        del cache[user_test]

    # 1. Sin registrar nada -> Desconectado
    estado0 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado0["en_linea"] is False
    assert estado0["texto"] == "Desconectado"
    print("OK: Usuario sin historial retorna 'Desconectado'")

    # 2. Registrar actividad ahora -> 'En línea'
    rutas_chat.registrar_actividad(user_test)
    estado1 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado1["en_linea"] is True
    assert estado1["texto"] == "En línea"
    print("OK: Usuario recién activo retorna 'En línea'")

    # 3. Simular hace 5 minutos (300 segundos)
    cache = rutas_chat._cargar_presencia()
    cache[user_test]["timestamp"] = int(time.time()) - 300
    estado2 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado2["en_linea"] is False
    assert "En línea hace 5 min" in estado2["texto"]
    print(f"OK: Simulación de 5 minutos retorna: '{estado2['texto']}'")

    # 4. Simular hace 2 horas hoy
    cache[user_test]["timestamp"] = int(time.time()) - 7200
    estado3 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado3["en_linea"] is False
    assert "Últ. vez hoy a las" in estado3["texto"]
    print(f"OK: Simulación de hoy más temprano retorna: '{estado3['texto']}'")

    # 5. Simular ayer
    ayer_ts = int((datetime.now() - timedelta(days=1, hours=2)).timestamp())
    cache[user_test]["timestamp"] = ayer_ts
    estado4 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado4["en_linea"] is False
    assert "Últ. vez ayer a las" in estado4["texto"]
    print(f"OK: Simulación de ayer retorna: '{estado4['texto']}'")

    # 6. Simular hace 4 días
    hace_4_dias_ts = int((datetime.now() - timedelta(days=4)).timestamp())
    cache[user_test]["timestamp"] = hace_4_dias_ts
    estado5 = rutas_chat.obtener_estado_presencia(user_test)
    assert estado5["en_linea"] is False
    assert "Últ. vez el" in estado5["texto"]
    print(f"OK: Simulación de días previos retorna: '{estado5['texto']}'")

    # 7. Pruebas de integración vía API con Flask test_client
    with app.test_client() as client:
        sup_user = 'Samuel_Giron-RUMN-2026-admin'
        taller_user = 'AUTOPARTESYMOTORESB.C.-RUMN-2026-prov'

        # Simular que taller estuvo activo hace 10 minutos
        rutas_chat.registrar_actividad(taller_user)
        rutas_chat._cargar_presencia()[taller_user]["timestamp"] = int(time.time()) - 600

        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": sup_user,
                "rol": "administracion",
                "datos_perfil": {
                    "nombre": "Samuel Giron",
                    "subrol": "Supervisor"
                }
            }

        # Consultar contactos como Supervisor
        res_contactos = client.get('/api/chat/contactos')
        assert res_contactos.status_code == 200
        contactos = res_contactos.get_json()['contactos']
        contacto_taller = next(c for c in contactos if c['usuario'] == taller_user)
        assert 'en_linea' in contacto_taller
        assert 'estado_presencia' in contacto_taller
        assert "En línea hace 10 min" in contacto_taller['estado_presencia']
        print(f"OK: API /api/chat/contactos incluye presencia: {contacto_taller['estado_presencia']}")

        # Consultar /api/chat/no_leidos con parámetro de contacto_activo
        res_nl = client.get(f'/api/chat/no_leidos?contacto_activo={taller_user}')
        assert res_nl.status_code == 200
        data_nl = res_nl.get_json()
        assert 'contacto_presencia' in data_nl
        assert data_nl['contacto_presencia']['en_linea'] is False
        assert "En línea hace 10 min" in data_nl['contacto_presencia']['texto']
        print(f"OK: API /api/chat/no_leidos sincroniza presencia en vivo del contacto activo: {data_nl['contacto_presencia']['texto']}")

        # Consultar endpoint dedicado /api/chat/presencia/<usuario>
        res_p = client.get(f'/api/chat/presencia/{taller_user}')
        assert res_p.status_code == 200
        data_p = res_p.get_json()
        assert data_p['en_linea'] is False
        assert "En línea hace 10 min" in data_p['estado_presencia']
        print(f"OK: API /api/chat/presencia/{taller_user} responde correctamente")

    print("\n=== TODAS LAS PRUEBAS DE PRESENCIA Y ÚLTIMA CONEXIÓN PASARON AL 100% ===")

if __name__ == '__main__':
    test_presence()
