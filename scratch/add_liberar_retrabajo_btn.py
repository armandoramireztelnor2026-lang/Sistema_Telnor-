# -*- coding: utf-8 -*-

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

target_html = """                <!-- Módulo de Garantía / Retrabajo (Verde, hasta abajo de delegar) -->
                <div style="margin-top: 15px; padding-top: 5px; display: flex; flex-direction: column; gap: 10px;">
                    <div style="text-align: center; color: #4ade80; font-size: 1.05rem; font-weight: 700; font-family: 'Poppins', sans-serif; letter-spacing: 0.8px; white-space: nowrap; width: 100%; box-sizing: border-box; padding: 4px 0 2px 0;">Garantía</div>
                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaAdmin('retrabajo')">Retrabajo</button>
                </div>"""

repl_html = """                <!-- Módulo de Garantía / Retrabajo (Verde, hasta abajo de delegar) -->
                <div style="margin-top: 15px; padding-top: 5px; display: flex; flex-direction: column; gap: 10px;">
                    <div style="text-align: center; color: #4ade80; font-size: 1.05rem; font-weight: 700; font-family: 'Poppins', sans-serif; letter-spacing: 0.8px; white-space: nowrap; width: 100%; box-sizing: border-box; padding: 4px 0 2px 0;">Garantía</div>
                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaAdmin('retrabajo')">Retrabajo</button>
                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Liberar/Retrabajo" type="button" onclick="abrirLiberarRetrabajoEnDesarrollo()">Liberar/Retrabajo</button>
                </div>"""

is_crlf_html = '\r\n' in html
html_norm = html.replace('\r\n', '\n')
target_html_norm = target_html.replace('\r\n', '\n')
repl_html_norm = repl_html.replace('\r\n', '\n')

if target_html_norm in html_norm:
    html_norm = html_norm.replace(target_html_norm, repl_html_norm, 1)
    if is_crlf_html:
        final_html = html_norm.replace('\n', '\r\n')
    else:
        final_html = html_norm
    with open('templates/administracion.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("SUCCESS: administracion.html updated with Liberar/Retrabajo button.")
else:
    print("ERROR: Target not found in administracion.html")

# 2. Update static/script.js with abrirLiberarRetrabajoEnDesarrollo
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

fn_code = """

window.abrirLiberarRetrabajoEnDesarrollo = function() {
    alert("⚠️ Módulo de 'Liberar/Retrabajo' actualmente en desarrollo.");
};
"""

if "window.abrirLiberarRetrabajoEnDesarrollo" not in js:
    is_crlf_js = '\r\n' in js
    if is_crlf_js:
        fn_code = fn_code.replace('\n', '\r\n')
    js += fn_code
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("SUCCESS: script.js updated with abrirLiberarRetrabajoEnDesarrollo function.")
else:
    print("INFO: Function already present in script.js.")

