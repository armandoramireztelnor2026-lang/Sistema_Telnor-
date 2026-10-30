import requests

BASE_URL = "http://127.0.0.1:5000"

def test_workshop_retrabajo():
    print("=== TEST 1: LOGIN TALLER AUTOPARTES Y MOTORES B.C. ===")
    s = requests.Session()
    r = s.post(f"{BASE_URL}/login", json={
        "usuario": "AUTOPARTESYMOTORESB.C.-RUMN-2026-prov",
        "password": "RX1Nzc1O",
        "rol": "proveedores"
    })
    print("Login status:", r.status_code, "Resp:", r.json())
    assert r.status_code == 200 and r.json().get("status") == "success", "Fallo login taller"

    # Llamar al endpoint de lista de retrabajos del proveedor
    res_list = s.get(f"{BASE_URL}/api/garantia/proveedor/lista")
    print("Lista status:", res_list.status_code)
    data = res_list.json()
    print("Total retrabajos encontrados:", data.get("total"))
    tickets = [r.get("ticket_original") or r.get("ticket") or r.get("id") for r in data.get("retrabajos", [])]
    print("Tickets encontrados:", tickets)
    assert "REP-20261008131643" in tickets, "El ticket REP-20261008131643 debe estar presente para el taller asignado"
    print("[OK] TEST 1 PASADO: El taller asignado ve la orden de retrabajo correctamente.")

    print("\n=== TEST 2: LOGIN OTRO TALLER (AYALA PULIDO ESPERANZA) ===")
    s2 = requests.Session()
    r2 = s2.post(f"{BASE_URL}/login", json={
        "usuario": "AYALAPULIDOESPERANZA-RUMN-2026-prov",
        "password": "Ekc62xqw",
        "rol": "proveedores"
    })
    print("Login otro taller status:", r2.status_code, "Resp:", r2.json())
    assert r2.status_code == 200 and r2.json().get("status") == "success", "Fallo login otro taller"

    res_list2 = s2.get(f"{BASE_URL}/api/garantia/proveedor/lista")
    data2 = res_list2.json()
    tickets2 = [r.get("ticket_original") or r.get("ticket") or r.get("id") for r in data2.get("retrabajos", [])]
    print("Tickets encontrados para otro taller:", tickets2)
    assert "REP-20261008131643" not in tickets2, "El ticket no debe aparecer para un taller ajeno"
    print("[OK] TEST 2 PASADO: Taller ajeno no ve el retrabajo de AUTOPARTES Y MOTORES B.C.")

    print("\n=== TODOS LOS TESTS PASARON EXITOSAMENTE ===")

if __name__ == "__main__":
    test_workshop_retrabajo()
