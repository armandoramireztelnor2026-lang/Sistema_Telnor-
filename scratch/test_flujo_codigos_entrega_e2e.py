# -*- coding: utf-8 -*-
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import json
from app import app

def run_tests():
    client = app.test_client()

    print("=== TEST: FLUJO DE CÓDIGOS DE ENTREGA Y LIBERACIÓN RETRABAJO ===")

    # 1. Preparar tickets de prueba en retrabajos.json y facturas.json
    retrabajos_data = json.load(open("retrabajos.json", encoding="utf-8"))
    facturas_data = json.load(open("facturas.json", encoding="utf-8"))
    reportes_data = json.load(open("reportes.json", encoding="utf-8"))

    t1 = "TEST-COD-1111"
    t2 = "TEST-COD-2222"

    for t in [t1, t2]:
        retrabajos_data["retrabajos"] = [r for r in retrabajos_data.get("retrabajos", []) if r.get("id") != t]
        facturas_data["facturas"] = [f for f in facturas_data.get("facturas", []) if f.get("id_reporte") != t]
        reportes_data["reportes"] = [r for r in reportes_data.get("reportes", []) if r.get("id") != t]

    for t, u in [(t1, "8090-1111"), (t2, "8090-2222")]:
        retrabajos_data["retrabajos"].append({
            "id": t,
            "ticket_original": t,
            "unidad": u,
            "proveedor": "AUTOPARTES Y MOTORES B.C.",
            "cope": "CENTRO",
            "ciudad": "TIJUANA",
            "estado": "Reasignado",
            "motivo_chofer": "Falla de prueba para codigos",
            "fecha_reasignacion": "2026-10-30 12:00:00",
            "factura_id": f"FAC-{t}",
            "seccion_1": {
                "empleado": "Chofer de Prueba",
                "email": "armandoramireztelnor2026@gmail.com"
            }
        })
        facturas_data["facturas"].append({
            "id": f"FAC-{t}",
            "id_reporte": t,
            "unidad": u,
            "estado": "Retrabajo",
            "estado_retrabajo": "Reasignado",
            "estado_previo": "Archivado",
            "retrabajo": "Sí",
            "num_retrabajo": 1,
            "retrabajo_unidad_entregada": "No"
        })
        reportes_data["reportes"].append({
            "id": t,
            "unidad": u,
            "empleado": "Chofer de Prueba",
            "email": "armandoramireztelnor2026@gmail.com",
            "estado": "Retrabajo",
            "entregado": "No"
        })

    with open("retrabajos.json", "w", encoding="utf-8") as f:
        json.dump(retrabajos_data, f, indent=4, ensure_ascii=False)
    with open("facturas.json", "w", encoding="utf-8") as f:
        json.dump(facturas_data, f, indent=4, ensure_ascii=False)
    with open("reportes.json", "w", encoding="utf-8") as f:
        json.dump(reportes_data, f, indent=4, ensure_ascii=False)

    print("1. Tickets de prueba preparados en 'Reasignado'")

    # 2. Taller marca como listo el ticket 1
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "AUTOPARTESYMOTORESB.C.-RUMN-2026-prov",
            "rol": "proveedores",
            "datos_perfil": {
                "nombre_proveedor": "AUTOPARTES Y MOTORES B.C.",
                "correo": "armandoramireztelnor2026@gmail.com"
            }
        }

    res_fin1 = client.post("/api/garantia/taller/finalizar", json={"ticket": t1})
    print(f"2. Taller marca {t1} como listo: Status={res_fin1.status_code}")
    assert res_fin1.status_code == 200
    assert res_fin1.get_json()["status"] == "success"

    # Verificar que se generaron los códigos
    ret_chk = json.load(open("retrabajos.json", encoding="utf-8"))
    obj1 = next(r for r in ret_chk["retrabajos"] if r.get("id") == t1)
    cod_chofer_1 = obj1.get("codigo_chofer")
    cod_super_1 = obj1.get("codigo_supervisor")
    assert cod_chofer_1 and len(cod_chofer_1) == 6, f"Código chofer inválido: {cod_chofer_1}"
    assert cod_super_1 and len(cod_super_1) == 6, f"Código supervisor inválido: {cod_super_1}"
    assert obj1.get("estado") == "Por Liberar"
    assert obj1.get("unidad_entregada") == "No"
    print(f"   -> Códigos generados exitosamente: Chofer={cod_chofer_1}, Supervisor={cod_super_1}")

    # Verificar facturas.json
    fac_chk = json.load(open("facturas.json", encoding="utf-8"))
    fac1 = next(f for f in fac_chk["facturas"] if f.get("id_reporte") == t1)
    assert fac1.get("retrabajo_unidad_entregada") == "No"
    assert fac1.get("estado_retrabajo") == "Por Liberar"
    print("   -> Confirmado: facturas.json tiene retrabajo_unidad_entregada = 'No'")

    # 3. Supervisor intenta liberar con código ERRÓNEO
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

    res_fail = client.post("/api/garantia/supervisor/liberar", json={"ticket": t1, "codigo": "000000"})
    print(f"3. Intento con código erróneo: Status={res_fail.status_code}, Res={res_fail.get_json()}")
    assert res_fail.status_code == 400
    assert "incorrecto" in res_fail.get_json()["message"].lower()

    # 4. Supervisor valida con el CÓDIGO DEL CHOFER
    res_ok_chofer = client.post("/api/garantia/supervisor/liberar", json={"ticket": t1, "codigo": cod_chofer_1})
    print(f"4. Validación con código de chofer ({cod_chofer_1}): Status={res_ok_chofer.status_code}")
    assert res_ok_chofer.status_code == 200
    assert res_ok_chofer.get_json()["status"] == "success"

    # Verificar estados finales de ticket 1
    ret_post1 = json.load(open("retrabajos.json", encoding="utf-8"))
    fac_post1 = json.load(open("facturas.json", encoding="utf-8"))
    rep_post1 = json.load(open("reportes.json", encoding="utf-8"))

    o1_fin = next(r for r in ret_post1["retrabajos"] if r.get("id") == t1)
    f1_fin = next(f for f in fac_post1["facturas"] if f.get("id_reporte") == t1)
    r1_fin = next(r for r in rep_post1["reportes"] if r.get("id") == t1)

    assert o1_fin["estado"] == "Finalizado"
    assert o1_fin["unidad_entregada"] == "Sí"
    assert o1_fin["tipo_codigo_validado"] == "Código de Chofer"
    assert f1_fin["retrabajo_unidad_entregada"] == "Sí"
    assert r1_fin["entregado"] == "Sí"
    print("   -> Confirmado: Ticket 1 liberado con código de chofer, retrabajo_unidad_entregada = 'Sí'")

    # 5. Taller marca como listo el ticket 2 y probamos el CÓDIGO DE RESPALDO DE SUPERVISIÓN
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "AUTOPARTESYMOTORESB.C.-RUMN-2026-prov",
            "rol": "proveedores",
            "datos_perfil": {
                "nombre_proveedor": "AUTOPARTES Y MOTORES B.C.",
                "correo": "armandoramireztelnor2026@gmail.com"
            }
        }

    res_fin2 = client.post("/api/garantia/taller/finalizar", json={"ticket": t2})
    assert res_fin2.status_code == 200
    ret_chk2 = json.load(open("retrabajos.json", encoding="utf-8"))
    obj2 = next(r for r in ret_chk2["retrabajos"] if r.get("id") == t2)
    cod_super_2 = obj2.get("codigo_supervisor")

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

    res_ok_super = client.post("/api/garantia/supervisor/liberar", json={"ticket": t2, "codigo": cod_super_2})
    print(f"5. Validación con código de respaldo de supervisor ({cod_super_2}): Status={res_ok_super.status_code}")
    assert res_ok_super.status_code == 200
    assert res_ok_super.get_json()["status"] == "success"

    ret_post2 = json.load(open("retrabajos.json", encoding="utf-8"))
    fac_post2 = json.load(open("facturas.json", encoding="utf-8"))
    o2_fin = next(r for r in ret_post2["retrabajos"] if r.get("id") == t2)
    f2_fin = next(f for f in fac_post2["facturas"] if f.get("id_reporte") == t2)

    assert o2_fin["estado"] == "Finalizado"
    assert o2_fin["unidad_entregada"] == "Sí"
    assert o2_fin["tipo_codigo_validado"] == "Código de Respaldo de Supervisión"
    assert f2_fin["retrabajo_unidad_entregada"] == "Sí"
    print("   -> Confirmado: Ticket 2 liberado con código de respaldo, retrabajo_unidad_entregada = 'Sí'")

    # Limpiar datos de prueba
    for t in [t1, t2]:
        ret_post2["retrabajos"] = [r for r in ret_post2["retrabajos"] if r.get("id") != t]
        fac_post2["facturas"] = [f for f in fac_post2["facturas"] if f.get("id_reporte") != t]
        reportes_data["reportes"] = [r for r in reportes_data.get("reportes", []) if r.get("id") != t]

    with open("retrabajos.json", "w", encoding="utf-8") as f:
        json.dump(ret_post2, f, indent=4, ensure_ascii=False)
    with open("facturas.json", "w", encoding="utf-8") as f:
        json.dump(fac_post2, f, indent=4, ensure_ascii=False)
    with open("reportes.json", "w", encoding="utf-8") as f:
        json.dump(reportes_data, f, indent=4, ensure_ascii=False)

    print("\n>>> TODOS LOS TESTS DE CÓDIGOS Y LIBERACIÓN PASARON AL 100% <<<")

if __name__ == "__main__":
    run_tests()
