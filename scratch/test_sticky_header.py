# -*- coding: utf-8 -*-
import unittest
import urllib.request
import re

class TestStickyHeader(unittest.TestCase):
    def test_administracion_html(self):
        with open('templates/administracion.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        self.assertIn('contenedor-tabla-reportes', html)
        self.assertIn('overflow-y: auto', html)
        self.assertIn('max-height: calc(100vh - 280px)', html)
        self.assertIn('id="tabla-exportable-reportes"', html)
        print("[PASS] administracion.html contains contenedor-tabla-reportes with vertical/horizontal scrolling.")

    def test_style_css(self):
        with open('static/style.css', 'r', encoding='utf-8') as f:
            css = f.read()

        self.assertIn('.contenedor-tabla-reportes', css)
        self.assertIn('#tabla-exportable-reportes th', css)
        self.assertIn('position: sticky', css)
        self.assertIn('top: 0', css)
        self.assertIn('border-collapse: separate', css)
        print("[PASS] style.css contains sticky header rules (position: sticky, top: 0, border-collapse: separate).")

    def test_server_status(self):
        res = urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)
        self.assertEqual(res.status, 200)
        print("[PASS] Server running and responding with HTTP 200.")

if __name__ == '__main__':
    unittest.main()

