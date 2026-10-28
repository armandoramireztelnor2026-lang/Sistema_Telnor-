# -*- coding: utf-8 -*-
import sys
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app import app
from rutas_reportes import leer_json, escribir_json

print("=== INICIANDO PRUEBAS DEL FLUJO DE REASIGNACIÓN DE RETRABAJO AL TALLER ===")

# 1. Asegurar que tenemos un retrabajo de prueba con estado 'Pendiente'
retrabajos_data = leer_json("retrabajos.json")
todos = retrabajos_data.get("retrabajos", [])
test_ticket = "REP-20261008131643"

target_ret = None
for r in todos:
    if r.get("id") == test_ticket or r.get("ticket_original") == test_ticket:
        target_ret = r
        break

if not target_ret:
    print("Creando retrabajo de prueba...")
    target_ret = {
        "id": test_ticket,
        "ticket": test_ticket,
        "ticket_original": test_ticket,
        "factura_id": "20261008133951",
        "unidad": "1212",
        "cope": "PE CALLE 10",
        "ciudad": "Tijuana",
        "fecha_solicitud": "2026-10-28",
        "motivo_chofer": "Falla persistente no reparada de manera correcta",
        "supervisor_asignado": "Samuel Giron",
        "supervisor_usuario": "Samuel_Giron-RUMN-2026-admin",
        "estado": "Pendiente",
        "seccion_1": {"ticket": test_ticket, "unidad": "1212", "empleado": "Doroteo Arango"},
        "seccion_2": {"proveedor": "AUTOPARTES Y MOTORES B.C.", "responsable": "Andres Avila", "precio_total": 7600.0}
    }
    todos.append(target_ret)
    retrabajos_data["retrabajos"] = todos
    escribir_json("retrabajos.json", retrabajos_data)
else:
    # Reset to Pendiente for test
    target_ret["estado"] = "Pendiente"
    escribir_json("retrabajos.json", retrabajos_data)

# 2. Test reasignar como Supervisor
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "Samuel_Giron-RUMN-2026-admin",
            "rol": "administracion",
            "datos_perfil": {
                "subrol": "Supervisor",
                "nombres": "Samuel",
                "apellido_paterno": "Giron",
                "cope": "PE CALLE 10"
            }
        }

    res = client.post("/api/garantia/reasignar", json={"ticket": test_ticket})
    assert res.status_code == 200, f"Error en reasignar: {res.status_code} - {res.get_json()}"
    data = res.get_json()
    assert data.get("status") == "success", f"Status no es success: {data}"
    print("OK: Supervisor reasignó la unidad exitosamente sin error 500!")
    print(f"    Respuesta: {data.get('message')}")

# 3. Test que el taller correspondiente recibe la orden de retrabajo
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "AUTOPARTESYMOTORESB.C.-RUMN-2026-prov",
            "rol": "proveedores",
            "datos_perfil": {
                "nombre_proveedor": "AUTOPARTES Y MOTORES B.C.",
                "correo": "armandoramireztelnor2026@gmail.com"
            }
        }

    res_prov = client.get("/api/garantia/proveedor/lista")
    assert res_prov.status_code == 200, f"Error en proveedor lista: {res_prov.status_code}"
    data_prov = res_prov.get_json()
    assert data_prov.get("status") == "success", "Status proveedor lista no es success"
    retrabajos_prov = data_prov.get("retrabajos", [])
    
    encontrado = any(r.get("id") == test_ticket or r.get("ticket_original") == test_ticket for r in retrabajos_prov)
    assert encontrado, f"El taller AUTOPARTES Y MOTORES B.C. NO recibió el ticket {test_ticket} en su lista de retrabajos!"
    print(f"OK: El taller recibió correctamente la orden de retrabajo ({len(retrabajos_prov)} órdenes encontradas).")

# 4. Test que otro taller NO ve el retrabajo asignado a AUTOPARTES
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "GALLEGOS-RUMN-2026-prov",
            "rol": "proveedores",
            "datos_perfil": {
                "nombre_proveedor": "GALLEGOS",
                "correo": "gallegos@test.com"
            }
        }

    res_otro = client.get("/api/garantia/proveedor/lista")
    assert res_otro.status_code == 200
    otro_prov = res_otro.get_json().get("retrabajos", [])
    assert not any(r.get("id") == test_ticket for r in otro_prov), "Otro taller vio el ticket que no le correspondía!"
    print("OK: Otro taller NO tiene acceso al retrabajo del taller del ticket.")

print("\n=== TODAS LAS PRUEBAS DEL FLUJO DE REASIGNACIÓN PASARON EXITOSAMENTE AL 100% ===")
