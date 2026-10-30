# -*- coding: utf-8 -*-
import unittest
import json
import urllib.request
import re

class TestRetrabajoFinalizadoColumna(unittest.TestCase):
    def test_facturas_json_num_retrabajo(self):
        with open('facturas.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        found = False
        for fac in data.get('facturas', []):
            if fac.get('id') == '20261008133951':
                self.assertEqual(fac.get('num_retrabajo'), 1, f"num_retrabajo must be 1, found: {fac.get('num_retrabajo')}")
                found = True
        self.assertTrue(found, "Ticket 20261008133951 must be in facturas.json")
        print("[PASS] facturas.json ticket 20261008133951 has num_retrabajo == 1")

    def test_rutas_reportes_safeguard(self):
        with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('Candado: no duplicar conteo si ya se encontraba en proceso activo de reasignacion', code)
        self.assertIn('f.get("estado") != "Retrabajo" or f.get("estado_retrabajo") != "Reasignado"', code)
        print("[PASS] rutas_reportes.py has reasignar counter safeguard")

    def test_html_column_headers(self):
        with open('templates/administracion.html', 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('FECHA DE FINALIZACION/REINGRESO', html)
        self.assertIn('RETRABAJO FINALIZADO', html)
        
        idx_fecha_fin = html.find('FECHA DE FINALIZACION/REINGRESO')
        idx_ret_fin = html.find('RETRABAJO FINALIZADO')
        idx_pedido = html.find('NUM. PEDIDO')
        
        self.assertLess(idx_fecha_fin, idx_ret_fin)
        self.assertLess(idx_ret_fin, idx_pedido)
        self.assertIn('<th class="th-amarillo col-amarillo">RETRABAJO FINALIZADO</th>', html)
        print("[PASS] templates/administracion.html has RETRABAJO FINALIZADO in the correct position")

    def test_js_rendering_cases(self):
        with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
            js = f.read()

        self.assertIn('valRetrabajoFinalizado', js)
        self.assertIn('background:#15803d', js) # Green for Sí
        self.assertIn('background:#b91c1c', js) # Red for No
        self.assertIn('border-radius:50%', js) # Circle
        self.assertIn('${valRetrabajoFinalizado}', js)
        print("[PASS] static/seccion_reportes.js renders Sí (green circle), No (red circle), and No Aplica")

    def test_server_status(self):
        res = urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)
        self.assertEqual(res.status, 200)
        print("[PASS] Server running and responding with HTTP 200.")

if __name__ == '__main__':
    unittest.main()

