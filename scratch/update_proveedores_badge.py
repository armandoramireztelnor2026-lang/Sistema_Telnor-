# -*- coding: utf-8 -*-

with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = """                    <div style="text-align: center; color: #4ade80; font-size: 1.05rem; font-weight: 700; font-family: 'Poppins', sans-serif; letter-spacing: 0.8px; white-space: nowrap; width: 100%; box-sizing: border-box; padding: 4px 0 2px 0;">Garantía</div>
                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv('retrabajo')">Retrabajo</button>"""

repl1 = """                    <div style="text-align: center; color: #4ade80; font-size: 1.05rem; font-weight: 700; font-family: 'Poppins', sans-serif; letter-spacing: 0.8px; white-space: nowrap; width: 100%; box-sizing: border-box; padding: 4px 0 2px 0;">Garantía</div>
                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv('retrabajo')" style="display: flex; align-items: center; justify-content: center; gap: 6px;">
                        <span>Retrabajo</span>
                        <span id="badge-retrabajo-prov" style="display: none; background: #ef4444; color: white; padding: 2px 7px; border-radius: 10px; font-size: 0.72rem; font-weight: 800; min-width: 18px; text-align: center; line-height: 1;">0</span>
                    </button>"""

if target1 in c:
    c = c.replace(target1, repl1, 1)
    print("OK: Replaced target1 in proveedores.html (LF)")
elif target1.replace('\n', '\r\n') in c:
    c = c.replace(target1.replace('\n', '\r\n'), repl1.replace('\n', '\r\n'), 1)
    print("OK: Replaced target1 in proveedores.html (CRLF)")
else:
    print("Warning: target1 not found in proveedores.html")

# Bump script.js version in proveedores.html
c = c.replace('/static/script.js?v=1000016', '/static/script.js?v=1000027')
c = c.replace('/static/script.js?v=1000026', '/static/script.js?v=1000027')

with open('templates/proveedores.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Actualizado proveedores.html")

