# -*- coding: utf-8 -*-
with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = '                    <button class="btn-sidebar btn-sidebar-retrabajo" style="border-color: rgba(56, 189, 248, 0.5) !important; color: #38bdf8 !important;" title="Tiempo de Garantía" type="button" onclick="abrirModalGarantiaProveedor()">⏱️ Tiempo/Garantía</button>\n'

if target in c:
    c = c.replace(target, '')
    print("OK: Removed Tiempo/Garantia from proveedores.html")
else:
    target_crlf = target.replace('\n', '\r\n')
    if target_crlf in c:
        c = c.replace(target_crlf, '')
        print("OK: Removed Tiempo/Garantia from proveedores.html (CRLF)")
    else:
        print("WARN: exact target not found, trying line removal")
        lines = c.splitlines(True)
        lines = [l for l in lines if 'abrirModalGarantiaProveedor' not in l]
        c = "".join(lines)
        print("OK: Filtered out line containing abrirModalGarantiaProveedor")

with open('templates/proveedores.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("proveedores.html actualizado.")

