# -*- coding: utf-8 -*-
import sys
import os
import unittest
from unittest.mock import patch

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app import app
from rutas_reportes import leer_json, escribir_json
import rutas_reportes

print("=== INICIANDO PRUEBAS DE NOTIFICACIÓN DE RETRABAJO A TALLER Y SUPERVISOR ===")

test_ticket = "REP-20261008131643"
retrabajos_data = leer_json("retrabajos.json")
for r in retrabajos_data.get("retrabajos", []):
    if r.get("id") == test_ticket or r.get("ticket_original") == test_ticket:
        r["estado"] = "Pendiente"
        r["supervisor_correo"] = "supervisor_prueba@telnor.com"
        r["supervisor_asignado"] = "Samuel Giron"
        break
escribir_json("retrabajos.json", retrabajos_data)

correos_enviados = []

def mock_correo_taller(correo_taller, nombre_taller, ticket, unidad, motivo_retrabajo, nombre_supervisor=None):
    correos_enviados.append({
        "destinatario": "taller",
        "correo": correo_taller,
        "nombre": nombre_taller,
        "ticket": ticket,
        "unidad": unidad,
        "motivo": motivo_retrabajo,
        "supervisor": nombre_supervisor
    })
    return True, "Enviado"

def mock_correo_supervisor(correo_supervisor, nombre_supervisor, ticket, unidad, nombre_taller, motivo_retrabajo):
    correos_enviados.append({
        "destinatario": "supervisor",
        "correo": correo_supervisor,
        "nombre": nombre_supervisor,
        "ticket": ticket,
        "unidad": unidad,
        "taller": nombre_taller,
        "motivo": motivo_retrabajo
    })
    return True, "Enviado"

with patch('rutas_reportes.enviar_correo_retrabajo_taller', side_effect=mock_correo_taller), \
     patch('rutas_reportes.enviar_correo_retrabajo_exitoso_supervisor', side_effect=mock_correo_supervisor):

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["usuario"] = {
                "usuario": "Samuel_Giron-RUMN-2026-admin",
                "rol": "administracion",
                "correo": "samuel.giron@telnor.com",
                "datos_perfil": {
                    "subrol": "Supervisor",
                    "nombres": "Samuel",
                    "apellido_paterno": "Giron",
                    "correo": "samuel.giron@telnor.com",
                    "cope": "PE CALLE 10"
                }
            }

        res = client.post("/api/garantia/reasignar", json={"ticket": test_ticket})
        assert res.status_code == 200, f"Error en reasignar: {res.status_code} - {res.get_json()}"
        data = res.get_json()
        assert data.get("status") == "success"
        print("OK: Endpoint /api/garantia/reasignar respondió 200 SUCCESS.")

# Verificar que AMBOS correos fueron despachados
print(f"Total correos mockeados registrados: {len(correos_enviados)}")
assert len(correos_enviados) == 2, f"Se esperaban 2 correos (taller y supervisor), pero se enviaron {len(correos_enviados)}"

taller_mail = next(m for m in correos_enviados if m["destinatario"] == "taller")
sup_mail = next(m for m in correos_enviados if m["destinatario"] == "supervisor")

print(f"OK: Correo al taller despachado a {taller_mail['correo']} para {taller_mail['nombre']}.")
print(f"OK: Correo al supervisor despachado a {sup_mail['correo']} confirmando la reasignación exitosa para ticket {sup_mail['ticket']}.")

# Reset to Pendiente for user testing
for r in retrabajos_data.get("retrabajos", []):
    if r.get("id") == test_ticket or r.get("ticket_original") == test_ticket:
        r["estado"] = "Pendiente"
        break
escribir_json("retrabajos.json", retrabajos_data)

print("\n=== TODAS LAS PRUEBAS DE NOTIFICACIÓN PASARON AL 100% ===")

