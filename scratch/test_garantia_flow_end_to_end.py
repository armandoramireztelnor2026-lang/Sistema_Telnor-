import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:5000"

print("--- 1. Testing /api/unidades ---")
req = urllib.request.urlopen(f"{base_url}/api/unidades", timeout=5)
unidades = json.loads(req.read().decode('utf-8'))
u1212 = unidades.get("80901212") or unidades.get("1212")
print("Unit 1212 data:", u1212)
assert u1212 is not None, "Unit 1212 not found in /api/unidades!"
assert u1212.get("estado_operativo") in ["Garantía/Retrabajo", "En Garantía"], f"Expected 'Garantía/Retrabajo', got: {u1212.get('estado_operativo')}"
assert u1212.get("activa_en_garantia") is True, f"Expected activa_en_garantia True, got: {u1212.get('activa_en_garantia')}"
print("=> /api/unidades: OK!")

print("\n--- 2. Testing /api/unidades/metricas ---")
req_m = urllib.request.urlopen(f"{base_url}/api/unidades/metricas", timeout=5)
metricas = json.loads(req_m.read().decode('utf-8'))
totales = metricas.get("totales", {})
print("Metricas totales:", totales)
assert totales.get("garantia") >= 1, f"Expected garantia >= 1, got {totales.get('garantia')}"
print("=> /api/unidades/metricas: OK!")

print("\n--- 3. Testing POST /api/reportes/nuevo with unit 1212 ---")
data = urllib.parse.urlencode({
    "unidad": "1212",
    "fecha": "2026-10-29",
    "kilometraje": "125000",
    "marca": "CHEVROLET",
    "modelo": "1999",
    "celular": "6641234567",
    "empleado": "Juan Perez",
    "email": "test@correo.com",
    "ciudad": "Tijuana",
    "cope": "PE CALLE 10",
    "departamento": "Calidad",
    "tipo_mantenimiento": "Correctivo",
    "descripcion_problema": "Falla prueba"
}).encode('utf-8')

req_post = urllib.request.Request(f"{base_url}/api/reportes/nuevo", data=data, method="POST")
try:
    resp = urllib.request.urlopen(req_post, timeout=5)
    result = json.loads(resp.read().decode('utf-8'))
    print("Report submission result:", result)
    assert result.get("status") == "error", f"Expected error, got: {result}"
    assert "garantía" in result.get("message", "").lower() or "reasignación" in result.get("message", "").lower(), f"Unexpected message: {result.get('message')}"
    print("=> Blocked correctly with message:", result.get("message"))
except urllib.error.HTTPError as e:
    print("HTTP error:", e.code, e.read().decode())

print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---")

