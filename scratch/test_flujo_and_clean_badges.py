# -*- coding: utf-8 -*-
import unittest
import urllib.request
import re

class TestFlujoAndCleanBadges(unittest.TestCase):
    def test_sidebar_buttons_placement(self):
        with open('templates/administracion.html', 'r', encoding='utf-8') as f:
            html = f.read()

        # 1. Supervisor section check
        sup_block_match = re.search(r"{% if usuario\.datos_perfil\.subrol == 'Supervisor' %}(.*?){% endif %}", html, re.DOTALL)
        self.assertIsNotNone(sup_block_match, "Supervisor block not found")
        sup_block = sup_block_match.group(1)
        
        self.assertIn("cambiarVistaAdmin('flujo-trabajo')", sup_block)
        self.assertIn("cambiarVistaAdmin('analitica')", sup_block)
        
        pos_flujo_sup = sup_block.find("cambiarVistaAdmin('flujo-trabajo')")
        pos_ana_sup = sup_block.find("cambiarVistaAdmin('analitica')")
        self.assertLess(pos_flujo_sup, pos_ana_sup, "In Supervisor, Flujo de Trabajo must be above Analitica")

        # 2. Administrador section check
        admin_block_match = re.search(r"{% if usuario\.datos_perfil\.subrol == 'Administrador' %}(.*?){% endif %}", html, re.DOTALL)
        self.assertIsNotNone(admin_block_match, "Administrador block not found")
        admin_block = admin_block_match.group(1)

        self.assertIn("cambiarVistaAdmin('flujo-trabajo')", admin_block)
        self.assertIn("cambiarVistaAdmin('analitica')", admin_block)

        pos_flujo_admin = admin_block.find("cambiarVistaAdmin('flujo-trabajo')")
        pos_ana_admin = admin_block.find("cambiarVistaAdmin('analitica')")
        self.assertLess(pos_flujo_admin, pos_ana_admin, "In Administrador, Flujo de Trabajo must be above Analitica")
        print("[PASS] Flujo de Trabajo is correctly positioned directly above Analítica in both Supervisor and Administrador.")

    def test_clean_word_badges_no_dots(self):
        with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
            js = f.read()

        # Ensure no inner dot in valRetrabajoFinalizado
        self.assertNotIn('width:8px; height:8px', js)
        self.assertIn('display:inline-block;">Sí</span>', js)
        self.assertIn('display:inline-block;">No</span>', js)
        print("[PASS] Column Retrabajo Finalizado displays pure word 'Sí' / 'No' without dots.")

    def test_server_status(self):
        res = urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)
        self.assertEqual(res.status, 200)
        print("[PASS] Flask server responded with HTTP 200.")

if __name__ == '__main__':
    unittest.main()

