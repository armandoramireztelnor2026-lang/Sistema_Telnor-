# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from app import app

def run_test():
    client = app.test_client()

    print("=== TEST: FLUJO COMPLETO TALLER MARCA LISTO -> SUPERVISOR LIBERA ===")

    # 1. Preparar un ticket de prueba en retrabajos.json y facturas.json
    retrabajos_data = json.load(open("retrabajos.json", encoding="utf-8"))
    facturas_data = json.load(open("facturas.json", encoding="utf-8"))

    test_ticket = "TEST-LIBERAR-9999"
    
    # Limpiar si ya existía
    retrabajos_data["retrabajos"] = [r for r in retrabajos_data.get("retrabajos", []) if r.get("id") != test_ticket and r.get("ticket_original") != test_ticket]
    facturas_data["facturas"] = [f for f in facturas_data.get("facturas", []) if f.get("id_reporte") != test_ticket]

    # Crear registro de prueba en retrabajos
    nuevo_retrabajo = {
        "id": test_ticket,
        "ticket_original": test_ticket,
        "unidad": "8090-TEST",
        "proveedor": "AUTOPARTES Y MOTORES B.C.",
        "cope": "CENTRO",
        "ciudad": "TIJUANA",
        "estado": "Reasignado",
        "motivo_chofer": "Falla prueba para flujo liberar retrabajo",
        "fecha_reasignacion": "2026-10-30 12:00:00",
        "factura_id": "FAC-TEST-9999"
    }
    retrabajos_data["retrabajos"].append(nuevo_retrabajo)

    nuevo_factura = {
        "id": "FAC-TEST-9999",
        "id_reporte": test_ticket,
        "unidad": "8090-TEST",
        "estado": "Retrabajo",
        "estado_retrabajo": "Reasignado",
        "estado_previo": "Archivado",
        "retrabajo": "Sí",
        "num_retrabajo": 1,
        "fecha_retrabajo": "2026-10-30 12:00:00"
    }
    facturas_data["facturas"].append(nuevo_factura)

    with open("retrabajos.json", "w", encoding="utf-8") as f:
        json.dump(retrabajos_data, f, indent=4, ensure_ascii=False)
    with open("facturas.json", "w", encoding="utf-8") as f:
        json.dump(facturas_data, f, indent=4, ensure_ascii=False)

    print(f"1. Creado ticket de prueba {test_ticket} en estado 'Reasignado'")

    # 2. Simular sesión de taller y marcar como listo (/api/garantia/taller/finalizar)
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "AUTOPARTESYMOTORESB.C.-RUMN-2026-prov",
            "rol": "proveedores",
            "datos_perfil": {
                "nombre_proveedor": "AUTOPARTES Y MOTORES B.C."
            }
        }

    res_taller = client.post("/api/garantia/taller/finalizar", json={"ticket": test_ticket})
    print(f"2. Taller marca como listo: Status={res_taller.status_code}, Res={res_taller.get_json()}")
    assert res_taller.status_code == 200
    assert res_taller.get_json()["status"] == "success"

    # Verificar que el estado ahora sea "Por Liberar"
    retrabajos_check = json.load(open("retrabajos.json", encoding="utf-8"))
    ret_obj = next(r for r in retrabajos_check["retrabajos"] if r.get("id") == test_ticket)
    assert ret_obj["estado"] == "Por Liberar", f"Expected 'Por Liberar', got {ret_obj['estado']}"
    assert "fecha_finalizacion_taller" in ret_obj
    print("   -> Confirmado: Estado en retrabajos.json es 'Por Liberar'")

    # 3. Simular sesión de Supervisor y consultar bandejas (/api/garantia/supervisor/por_liberar)
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "Samuel_Giron-RUMN-2026-admin",
            "rol": "administracion",
            "datos_perfil": {
                "subrol": "Supervisor",
                "nombres": "Samuel",
                "apellido_paterno": "Giron",
                "cope": "CENTRO",
                "copes_asignados": ["CENTRO"]
            }
        }

    res_sup_list = client.get("/api/garantia/supervisor/por_liberar")
    print(f"3. Supervisor consulta bandeja 'Liberar/Retrabajo': Status={res_sup_list.status_code}")
    assert res_sup_list.status_code == 200
    items_por_liberar = res_sup_list.get_json().get("retrabajos", [])
    tickets_en_bandeja = [r.get("id") for r in items_por_liberar]
    print(f"   -> Tickets en bandeja Por Liberar: {tickets_en_bandeja}")
    assert test_ticket in tickets_en_bandeja, f"{test_ticket} no encontrado en la bandeja de Liberar/Retrabajo"

    # 4. Supervisor libera el retrabajo (/api/garantia/supervisor/liberar)
    res_liberar = client.post("/api/garantia/supervisor/liberar", json={"ticket": test_ticket})
    print(f"4. Supervisor libera retrabajo: Status={res_liberar.status_code}, Res={res_liberar.get_json()}")
    assert res_liberar.status_code == 200
    assert res_liberar.get_json()["status"] == "success"

    # 5. Verificar estados finales
    retrabajos_final = json.load(open("retrabajos.json", encoding="utf-8"))
    facturas_final = json.load(open("facturas.json", encoding="utf-8"))

    ret_final = next(r for r in retrabajos_final["retrabajos"] if r.get("id") == test_ticket)
    fac_final = next(f for f in facturas_final["facturas"] if f.get("id_reporte") == test_ticket)

    assert ret_final["estado"] == "Finalizado", f"Retrabajo debería ser 'Finalizado', es {ret_final['estado']}"
    assert "fecha_liberacion" in ret_final
    assert fac_final["estado_retrabajo"] == "Finalizado"
    assert fac_final["estado"] == "Archivado" # Estado restaurado
    print(f"5. Estados finales confirmados: Retrabajo={ret_final['estado']}, Factura={fac_final['estado']}, EstadoRetrabajo={fac_final['estado_retrabajo']}")

    # 6. Verificar que ya no aparece en la bandeja de Por Liberar
    res_sup_list_after = client.get("/api/garantia/supervisor/por_liberar")
    tickets_after = [r.get("id") for r in res_sup_list_after.get_json().get("retrabajos", [])]
    assert test_ticket not in tickets_after
    print("6. Confirmado: Ticket ya NO aparece en bandeja de Liberar/Retrabajo tras ser liberado.")

    # Limpiar datos de prueba
    retrabajos_final["retrabajos"] = [r for r in retrabajos_final["retrabajos"] if r.get("id") != test_ticket]
    facturas_final["facturas"] = [f for f in facturas_final["facturas"] if f.get("id_reporte") != test_ticket]
    with open("retrabajos.json", "w", encoding="utf-8") as f:
        json.dump(retrabajos_final, f, indent=4, ensure_ascii=False)
    with open("facturas.json", "w", encoding="utf-8") as f:
        json.dump(facturas_final, f, indent=4, ensure_ascii=False)

    print("\n>>> TODOS LOS TESTS PASARON EXITOSAMENTE (100% OK) <<<")

if __name__ == "__main__":
    run_test()
