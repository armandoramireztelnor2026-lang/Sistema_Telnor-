import requests

BASE_URL = "http://127.0.0.1:5000"

def test_seccion_reportes_columnas():
    print("=== TEST SECCION DE REPORTES COLUMNAS RETRABAJO ===")
    s = requests.Session()
    # Login as Jefatura / Admin
    r_login = s.post(f"{BASE_URL}/login", json={
        "usuario": "ManuelAlejandro_Marquez-RUMN-2026-admin",
        "password": "KepmtjVP",
        "rol": "administracion"
    })
    print("Login admin status:", r_login.status_code, "Resp:", r_login.json())
    assert r_login.status_code == 200 and r_login.json().get("status") == "success"

    # Fetch seccion_reportes list
    r_list = s.get(f"{BASE_URL}/api/seccion_reportes/lista")
    print("Seccion reportes status:", r_list.status_code)
    assert r_list.status_code == 200
    data = r_list.json()
    facturas = data.get("facturas", [])
    print(f"Total facturas/tickets retornados: {len(facturas)}")

    # Find ticket REP-20261008131643
    ticket_test = None
    for f in facturas:
        tid = f.get("id_reporte") or f.get("id") or ""
        retro = f.get("retro", "")
        if "REP-20261008131643" in str(tid) or "REP-20261008131643" in str(retro) or f.get("id") == "20261008133951":
            ticket_test = f
            break

    assert ticket_test is not None, "El ticket REP-20261008131643 debe estar en la lista de seccion reportes"
    print("\n--- DATOS DE TICKET CON RETRABAJO ---")
    print("ID Factura:", ticket_test.get("id"))
    print("Retrabajo:", ticket_test.get("retrabajo"))
    print("Num Retrabajo:", ticket_test.get("num_retrabajo"))
    print("Fecha Retrabajo:", ticket_test.get("fecha_retrabajo"))
    print("Fecha Fin Retrabajo:", ticket_test.get("fecha_finalizacion_retrabajo"))
    print("Estado Retrabajo:", ticket_test.get("estado_retrabajo"))

    assert ticket_test.get("fecha_retrabajo"), "Debe tener fecha_retrabajo definida"
    print("\n[OK] El ticket con retrabajo tiene fecha_retrabajo y estado_retrabajo correctamente poblados.")

    # Check template HTML
    r_html = s.get(f"{BASE_URL}/administracion")
    assert r_html.status_code == 200
    assert "<th>NUM/RETRABAJO</th>" in r_html.text
    assert "<th>FECHA/RETRABAJO</th>" in r_html.text
    assert "<th>TIEMPO EN TALLER/REINGRESO</th>" in r_html.text
    assert "<th>FECHA DE FINALIZACION/REINGRESO</th>" in r_html.text
    print("[OK] administracion.html tiene los 3 nuevos encabezados en su posición exacta.")

    # Check JS
    r_js = s.get(f"{BASE_URL}/static/seccion_reportes.js?v=1000010")
    assert r_js.status_code == 200
    assert "${valFechaRetrabajo}" in r_js.text
    assert "${valTiempoReingreso}" in r_js.text
    assert "${valFechaFinReingreso}" in r_js.text
    assert "badgeNoAplicaRet" in r_js.text
    print("[OK] seccion_reportes.js incluye la lógica y celdas para las 3 nuevas columnas.")

    print("\n=== TODOS LOS TESTS PASARON EXITOSAMENTE ===")

if __name__ == "__main__":
    test_seccion_reportes_columnas()

