# -*- coding: utf-8 -*-
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from app import app

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

    res = client.get("/administracion")
    assert res.status_code == 200, f"Error cargando administracion: {res.status_code}"
    html = res.get_data(as_text=True)

    pos_reasig = html.find('id="btn-reasignar-retrabajo"')
    pos_cancel_reasig = html.find('id="btn-cancelar-reasignacion"')
    # Buscar el botón Cancelar del footer que está después de Cancelar Reasignacion
    pos_cancel = html.find("cerrarModal('modal-detalle-retrabajo')", pos_cancel_reasig)

    assert pos_reasig != -1, "No se encontró el botón btn-reasignar-retrabajo"
    assert pos_cancel_reasig != -1, "No se encontró el botón btn-cancelar-reasignacion"
    assert pos_cancel != -1, "No se encontró el botón Cancelar en el footer"

    assert pos_reasig < pos_cancel_reasig < pos_cancel, "El orden de los botones no es de arriba hacia abajo (Reasignar -> Cancelar Reasignacion -> Cancelar)"
    print("OK: Los 3 botones existen y están ordenados verticalmente (Reasignar -> Cancelar Reasignación -> Cancelar).")

    # Fragmento entre el inicio del footer y el final del footer
    footer_start = html.rfind('<div style="background: #081322; padding: 18px 24px;', 0, pos_reasig)
    footer_end = html.find('</div>', pos_cancel)
    fragmento = html[footer_start:footer_end]
    
    assert "justify-content: flex-end" not in fragmento, "Todavía existe el div wrapper horizontal"
    assert "flex-direction: column" in fragmento, "No está configurado como flex-direction: column"
    print("OK: El footer es flex-direction: column sin wrappers horizontales intermediarios.")

print("=== VERIFICACIÓN DE BOTONES EXITOSA AL 100% ===")
