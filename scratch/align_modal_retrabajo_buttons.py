# -*- coding: utf-8 -*-
import re

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

target_html = """            <!-- Footer Modal Retrabajo: Botones Reasignar y Cancelar Reasignación arriba del botón Cancelar con diseño homogéneo -->
            <div style="background: #081322; padding: 16px 24px; border-top: 1px solid #1f395a; display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: flex-end; align-items: center;">
                    <button type="button" id="btn-reasignar-retrabajo" class="btn-footer-retrabajo btn-footer-retrabajo-reasignar" onclick="accionReasignarRetrabajo()">
                        Reasignar
                    </button>
                    <button type="button" id="btn-cancelar-reasignacion" class="btn-footer-retrabajo btn-footer-retrabajo-cancelar-reasig" onclick="abrirModalCancelarReasignacion()">
                        Cancelar Reasignacion
                    </button>
                </div>
                <button type="button" class="btn-footer-retrabajo btn-footer-retrabajo-cerrar" onclick="cerrarModal('modal-detalle-retrabajo')">
                    Cancelar
                </button>
            </div>"""

repl_html = """            <!-- Footer Modal Retrabajo: 3 Botones ordenados de arriba hacia abajo con el mismo diseño y tamaño -->
            <div style="background: #081322; padding: 18px 24px; border-top: 1px solid #1f395a; display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                <button type="button" id="btn-reasignar-retrabajo" class="btn-footer-retrabajo btn-footer-retrabajo-reasignar" onclick="accionReasignarRetrabajo()">
                    Reasignar
                </button>
                <button type="button" id="btn-cancelar-reasignacion" class="btn-footer-retrabajo btn-footer-retrabajo-cancelar-reasig" onclick="abrirModalCancelarReasignacion()">
                    Cancelar Reasignacion
                </button>
                <button type="button" class="btn-footer-retrabajo btn-footer-retrabajo-cerrar" onclick="cerrarModal('modal-detalle-retrabajo')">
                    Cancelar
                </button>
            </div>"""

if target_html in html:
    html = html.replace(target_html, repl_html, 1)
    print("OK: Replaced in administracion.html (LF)")
elif target_html.replace('\n', '\r\n') in html:
    html = html.replace(target_html.replace('\n', '\r\n'), repl_html.replace('\n', '\r\n'), 1)
    print("OK: Replaced in administracion.html (CRLF)")
else:
    print("Trying regex match for administracion.html...")
    pattern = r'<!-- Footer Modal Retrabajo:.*?<button[^>]+id="btn-reasignar-retrabajo".*?<button[^>]+id="btn-cancelar-reasignacion".*?<button[^>]+cerrarModal\(\'modal-detalle-retrabajo\'\)[^>]*>.*?Cancelar\s*</button>\s*</div>'
    html, count = re.subn(pattern, repl_html, html, flags=re.DOTALL)
    print(f"Regex replacements in administracion.html: {count}")

# Bump style.css and script.js cache buster
html = re.sub(r'style\.css\?v=\d+', 'style.css?v=1000029', html)
if 'style.css?v=' not in html:
    html = html.replace('/static/style.css', '/static/style.css?v=1000029')
html = re.sub(r'script\.js\?v=\d+', 'script.js?v=1000029', html)

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved templates/administracion.html")

# 2. Update static/style.css
with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_css = """.btn-footer-retrabajo {
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    border: none !important;
    color: #ffffff !important;
    min-width: 165px !important;
    height: 42px !important;
    text-align: center !important;
    font-family: 'Poppins', sans-serif !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    box-sizing: border-box !important;
}"""

repl_css = """.btn-footer-retrabajo {
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    border: none !important;
    color: #ffffff !important;
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;
    height: 44px !important;
    text-align: center !important;
    font-family: 'Poppins', sans-serif !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    box-sizing: border-box !important;
    letter-spacing: 0.3px !important;
    white-space: nowrap !important;
}"""

if target_css in css:
    css = css.replace(target_css, repl_css, 1)
    print("OK: Replaced in style.css (LF)")
elif target_css.replace('\n', '\r\n') in css:
    css = css.replace(target_css.replace('\n', '\r\n'), repl_css.replace('\n', '\r\n'), 1)
    print("OK: Replaced in style.css (CRLF)")
else:
    print("Trying regex match for style.css...")
    pattern_css = r'\.btn-footer-retrabajo\s*\{[^}]+\}'
    css, count_css = re.subn(pattern_css, repl_css, css, count=1)
    print(f"Regex replacements in style.css: {count_css}")

with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Saved static/style.css")

