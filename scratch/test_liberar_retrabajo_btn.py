# -*- coding: utf-8 -*-
import unittest
import urllib.request
import re

class TestLiberarRetrabajoBtn(unittest.TestCase):
    def test_button_structure_and_exclusivity(self):
        with open('templates/administracion.html', 'r', encoding='utf-8') as f:
            html = f.read()

        # 1. Must be in Supervisor block
        sup_match = re.search(r"{% if usuario\.datos_perfil\.subrol == 'Supervisor' %}(.*?){% endif %}", html, re.DOTALL)
        self.assertIsNotNone(sup_match)
        sup_block = sup_match.group(1)

        self.assertIn('Liberar/Retrabajo', sup_block)
        self.assertIn('abrirLiberarRetrabajoEnDesarrollo()', sup_block)
        self.assertIn('class="btn-sidebar btn-sidebar-retrabajo"', sup_block)

        # Must be below Retrabajo
        pos_ret = sup_block.find("cambiarVistaAdmin('retrabajo')")
        pos_lib_ret = sup_block.find("abrirLiberarRetrabajoEnDesarrollo()")
        self.assertLess(pos_ret, pos_lib_ret, "Liberar/Retrabajo must be below Retrabajo")

        # 2. Must NOT be in Jefatura or Administrador
        jef_match = re.search(r"{% if usuario\.datos_perfil\.subrol == 'Jefatura' %}(.*?){% endif %}", html, re.DOTALL)
        self.assertIsNotNone(jef_match)
        self.assertNotIn('Liberar/Retrabajo', jef_match.group(1))

        admin_match = re.search(r"{% if usuario\.datos_perfil\.subrol == 'Administrador' %}(.*?){% endif %}", html, re.DOTALL)
        self.assertIsNotNone(admin_match)
        self.assertNotIn('Liberar/Retrabajo', admin_match.group(1))

        print("[PASS] Liberar/Retrabajo button is properly styled, positioned below Retrabajo, and exclusive to Supervisor.")

    def test_script_function(self):
        with open('static/script.js', 'r', encoding='utf-8') as f:
            js = f.read()

        self.assertIn('abrirLiberarRetrabajoEnDesarrollo', js)
        self.assertIn('en desarrollo', js)
        print("[PASS] abrirLiberarRetrabajoEnDesarrollo function defined in static/script.js.")

    def test_server_status(self):
        res = urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)
        self.assertEqual(res.status, 200)
        print("[PASS] Flask server running and responding HTTP 200.")

if __name__ == '__main__':
    unittest.main()

