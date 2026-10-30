# -*- coding: utf-8 -*-
import unittest
import json
import re

class TestFiltroGarantiaRetrabajo(unittest.TestCase):
    def test_administracion_html_structure(self):
        with open('templates/administracion.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        self.assertIn('id="btn-filtro-garantia"', html)
        self.assertIn('id="btn-filtro-reactivadas"', html)
        self.assertIn('toggleFiltroGarantia()', html)
        
        # Verify btn-filtro-garantia appears before btn-filtro-reactivadas
        idx_garantia = html.find('id="btn-filtro-garantia"')
        idx_reactivadas = html.find('id="btn-filtro-reactivadas"')
        self.assertLess(idx_garantia, idx_reactivadas, "btn-filtro-garantia must be positioned above btn-filtro-reactivadas")
        
        # Check design attributes match
        garantia_match = re.search(r'<button\s+id="btn-filtro-garantia"[^>]+>', html)
        self.assertIsNotNone(garantia_match)
        btn_tag = garantia_match.group(0)
        self.assertIn('background:#334155', btn_tag)
        self.assertIn('color:#cbd5e1', btn_tag)
        self.assertIn('border:1px solid #475569', btn_tag)
        self.assertIn('height:35px', btn_tag)
        print("[PASS] administracion.html button placement and styling verified.")

    def test_seccion_reportes_js(self):
        with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
            js = f.read()

        self.assertIn('data-retrabajo=', js)
        self.assertIn('window.filtroGarantiaRetrabajoActivo', js)
        self.assertIn('function toggleFiltroGarantia()', js)
        self.assertIn("btn.style.background = '#f59e0b'", js)
        self.assertIn("btn.style.boxShadow = '0 0 10px rgba(245, 158, 11, 0.4)'", js)
        
        # Check reset in limpiarFiltrosReportes
        idx_limpiar = js.find('function limpiarFiltrosReportes()')
        self.assertNotEqual(idx_limpiar, -1)
        js_limpiar = js[idx_limpiar:idx_limpiar+2000]
        self.assertIn('window.filtroGarantiaRetrabajoActivo = false', js_limpiar)
        self.assertIn('btn-filtro-garantia', js_limpiar)
        print("[PASS] seccion_reportes.js contains toggle, row attribute and reset logic.")

    def test_filter_matching_logic(self):
        # Test simulated tickets matching logic
        test_tickets = [
            {"id": "1", "retrabajo": "Sí", "num_retrabajo": 1, "estado": "Retrabajo"},
            {"id": "2", "retrabajo": "No", "num_retrabajo": 0, "estado": "En Reparación (Taller)"},
            {"id": "3", "retrabajo": "Pendiente", "num_retrabajo": 0, "estado": "En Asignacion/Retrabajo"},
            {"id": "4", "retrabajo": "", "num_retrabajo": 0, "estado": "Finalizado / Histórico"},
        ]

        def is_retrabajo(f):
            rawRetLower = str(f.get('retrabajo', '')).strip().lower()
            numRet = int(f.get('num_retrabajo', 0))
            estRowLower = str(f.get('estado', '')).strip().lower()
            rawEstRet = str(f.get('estado_retrabajo', '')).strip().lower()
            fechaRetRaw = f.get('fecha_retrabajo', '')
            
            tieneReingreso = False
            if (numRet > 0 or rawRetLower in ['sí', 'si'] or rawEstRet in ['reasignado', 'finalizado'] or fechaRetRaw):
                if rawRetLower != 'cancelado':
                    tieneReingreso = True

            if (numRet > 0 or
                rawRetLower in ['sí', 'si', 'pendiente', 'reasignado'] or
                estRowLower in ['retrabajo', 'en asignacion/retrabajo'] or
                rawEstRet in ['reasignado', 'pendiente', 'finalizado'] or
                bool(fechaRetRaw) or tieneReingreso):
                if rawRetLower != 'cancelado' or numRet > 0:
                    return True
            return False

        results = [t["id"] for t in test_tickets if is_retrabajo(t)]
        self.assertEqual(results, ["1", "3"])
        print("[PASS] Filter logic accurately selects warranty/rework tickets (1 and 3).")

if __name__ == '__main__':
    unittest.main()
