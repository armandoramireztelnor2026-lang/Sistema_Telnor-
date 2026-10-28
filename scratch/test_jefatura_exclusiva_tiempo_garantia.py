# -*- coding: utf-8 -*-
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_jefatura_tiempo_garantia():
    print("=== INICIANDO PRUEBAS DE EXCLUSIVIDAD DE TIEMPO/GARANTÍA PARA JEFATURA ===")

    # 1. Verificar HTML de proveedores.html: NO debe existir el botón Tiempo/Garantía
    with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
        prov_html = f.read()
    assert "abrirModalGarantiaProveedor" not in prov_html, "El botón de abrir modal de garantía no debe existir en proveedores.html"
    assert "btn-sidebar-retrabajo\" style=\"border-color: rgba(56, 189, 248, 0.5)" not in prov_html
    print("OK: El botón 'Tiempo/Garantía' fue retirado exitosamente de la barra lateral de proveedores (Taller)")

    # 2. Verificar HTML de administracion.html:
    with open('templates/administracion.html', 'r', encoding='utf-8') as f:
        admin_html = f.read()

    # Buscar todas las apariciones de "tiempo-garantia" en botones
    botones_tiempo_garantia = re.findall(r'<button[^>]*onclick="cambiarVistaAdmin\(\'tiempo-garantia\'\)"[^>]*>Tiempo/Garantía</button>', admin_html)
    assert len(botones_tiempo_garantia) == 1, f"Debe haber exactamente 1 botón de Tiempo/Garantía en administracion.html, encontrados: {len(botones_tiempo_garantia)}"

    # Verificar que el botón esté dentro del bloque de Jefatura
    pos_jefatura = admin_html.find("{% if usuario.datos_perfil.subrol == 'Jefatura' %}")
    pos_supervisor = admin_html.find("{% if usuario.datos_perfil.subrol == 'Supervisor' %}")
    pos_boton = admin_html.find("cambiarVistaAdmin('tiempo-garantia')")

    assert pos_jefatura < pos_boton < pos_supervisor, "El botón de Tiempo/Garantía debe encontrarse exclusivamente dentro del bloque de Jefatura"
    print("OK: El botón 'Tiempo/Garantía' está única y exclusivamente en el rol de Jefatura")

    # 3. Verificar que Supervisor solo tenga Retrabajo
    pos_retrabajo_sup = admin_html.find("cambiarVistaAdmin('retrabajo')")
    assert pos_supervisor < pos_retrabajo_sup, "El botón Retrabajo debe estar en Supervisor"
    print("OK: Supervisor tiene 'Retrabajo' y NO 'Tiempo/Garantía'")

    # 4. Probar endpoints de Tiempo/Garantía con sesión de Jefatura
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['usuario'] = {
                "usuario": "jefatura_test",
                "rol": "administracion",
                "datos_perfil": {
                    "nombre": "Jefe General",
                    "subrol": "Jefatura"
                }
            }

        # Jefatura consulta la lista de tiempos de garantía de los talleres
        res_talleres = client.get('/api/garantia/talleres_tiempo')
        assert res_talleres.status_code == 200, f"Error al consultar talleres_tiempo: {res_talleres.data}"
        data_talleres = res_talleres.get_json()
        assert data_talleres['status'] == 'success'
        talleres = data_talleres['talleres']
        assert len(talleres) > 0, "Debe haber al menos un taller listado"
        taller_test = talleres[0]['usuario']
        print(f"OK: Jefatura consultó exitosamente los tiempos de garantía ({len(talleres)} talleres encontrados)")

        # Jefatura ajusta el tiempo de garantía de un taller a 45 días
        res_ajuste = client.post('/api/garantia/taller/actualizar_dias', json={
            "usuario": taller_test,
            "dias_garantia": 45,
            "horas_garantia": 0,
            "minutos_garantia": 0,
            "segundos_garantia": 0
        })
        assert res_ajuste.status_code == 200, f"Error al ajustar garantía: {res_ajuste.data}"
        data_ajuste = res_ajuste.get_json()
        assert data_ajuste['status'] == 'success'
        assert "45 días" in data_ajuste['tiempo_formateado']
        print(f"OK: Jefatura ajustó con éxito el tiempo de garantía para {taller_test} a 45 días")

        # Regresar a 30 días para dejar el valor estándar
        client.post('/api/garantia/taller/actualizar_dias', json={
            "usuario": taller_test,
            "dias_garantia": 30,
            "horas_garantia": 0,
            "minutos_garantia": 0,
            "segundos_garantia": 0
        })

    print("\n=== TODAS LAS PRUEBAS DE EXCLUSIVIDAD DE TIEMPO/GARANTÍA PASARON AL 100% ===")

if __name__ == '__main__':
    test_jefatura_tiempo_garantia()

