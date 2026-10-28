# -*- coding: utf-8 -*-
import re

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="vista-flujo-trabajo"')
if idx != -1:
    flujo = text[idx:]
    matches = [m.start() for m in re.finditer(r'telnor', flujo, re.IGNORECASE)]
    print(f'Matches of Telnor in flujo-trabajo: {len(matches)}')
    for m in matches:
        print(repr(flujo[max(0, m-50):min(len(flujo), m+60)]))
        print('---')
else:
    print('vista-flujo-trabajo not found')

with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

idx_js = js.find('function descargarDiagramaFlujo()')
if idx_js != -1:
    js_desc = js[idx_js:idx_js+2000]
    matches_js = [m.start() for m in re.finditer(r'telnor', js_desc, re.IGNORECASE)]
    print(f'Matches of Telnor in descargarDiagramaFlujo: {len(matches_js)}')
    for m in matches_js:
        print(repr(js_desc[max(0, m-50):min(len(js_desc), m+60)]))
        print('---')

