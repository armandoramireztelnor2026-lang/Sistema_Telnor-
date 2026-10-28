# -*- coding: utf-8 -*-
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('id="vista-flujo-trabajo"')
idx2 = text.find('<!-- VISTA: UNIDADES -->')
if idx2 == -1:
    idx2 = text.find('id="vista-unidades"')

print("vista-flujo-trabajo starts at:", idx1)
# search between idx1 and next view
next_view_idx = text.find('id="vista-', idx1 + 30)
print("next view starts at:", next_view_idx)

flujo_section = text[idx1:next_view_idx]
for line in flujo_section.splitlines():
    if 'telnor' in line.lower():
        print(line)

