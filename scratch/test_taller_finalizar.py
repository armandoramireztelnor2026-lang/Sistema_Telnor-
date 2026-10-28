# -*- coding: utf-8 -*-
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app import app
from rutas_reportes import leer_json

test_ticket = "REP-20261008131643"

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

    res_fin = client.post("/api/garantia/taller/finalizar", json={"ticket": test_ticket})
    assert res_fin.status_code == 200, f"Error finalizando: {res_fin.status_code} - {res_fin.get_json()}"
    data_fin = res_fin.get_json()
    assert data_fin.get("status") == "success", f"Status no es success: {data_fin}"
    print("OK: El taller finalizó el retrabajo exitosamente!")

    # Verificar que ya no aparece como pendiente en la lista de retrabajos del taller
    res_prov = client.get("/api/garantia/proveedor/lista")
    retrabajos_pendientes = res_prov.get_json().get("retrabajos", [])
    assert not any(r.get("id") == test_ticket for r in retrabajos_pendientes), "El ticket finalizado sigue apareciendo como pendiente!"
    print("OK: El ticket ya no aparece en pendientes de retrabajo del taller tras ser finalizado.")

print("=== PRUEBA DE FINALIZACIÓN POR EL TALLER EXITOSA ===")

