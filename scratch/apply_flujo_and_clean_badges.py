# -*- coding: utf-8 -*-

# 1. Update static/seccion_reportes.js
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

target_js = """            if (estaFinalizado) {
                valRetrabajoFinalizado = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-flex; align-items:center; gap:6px;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#4ade80; box-shadow:0 0 6px #4ade80;"></span> Sí</span>`;
            } else {
                valRetrabajoFinalizado = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-flex; align-items:center; gap:6px;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#f87171; box-shadow:0 0 6px #f87171;"></span> No</span>`;
            }"""

repl_js = """            if (estaFinalizado) {
                valRetrabajoFinalizado = `<span style="background:#15803d; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">Sí</span>`;
            } else {
                valRetrabajoFinalizado = `<span style="background:#b91c1c; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap; display:inline-block;">No</span>`;
            }"""

is_crlf_js = '\r\n' in js_text
js_norm = js_text.replace('\r\n', '\n')
t_js_norm = target_js.replace('\r\n', '\n')
r_js_norm = repl_js.replace('\r\n', '\n')

if t_js_norm in js_norm:
    js_norm = js_norm.replace(t_js_norm, r_js_norm, 1)
    if is_crlf_js:
        final_js = js_norm.replace('\n', '\r\n')
    else:
        final_js = js_norm
    with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
        f.write(final_js)
    print("SUCCESS: seccion_reportes.js updated (dot removed, pure word).")
else:
    print("ERROR: Target not found in seccion_reportes.js")

# 2. Update templates/administracion.html for Flujo de Trabajo in Supervisor and Administrador (above Analitica)
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

# Supervisor replacement:
target_sup = """                <!-- ========== SUPERVISOR ========== -->
                {% if usuario.datos_perfil.subrol == 'Supervisor' %}
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('reportes')">Bandeja de Reportes</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('facturas')">Cotizaciones y Órdenes</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('facturas_finales')">Facturas</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('documentos-contables')">Documentos Contables</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-prov')">Directorio Talleres</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-corp')">Lista de Corporativos</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-admin')">Lista Automotriz</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('unidades')">Unidades</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('accesos')">Accesos (Credenciales)</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>"""

repl_sup = """                <!-- ========== SUPERVISOR ========== -->
                {% if usuario.datos_perfil.subrol == 'Supervisor' %}
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('reportes')">Bandeja de Reportes</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('facturas')">Cotizaciones y Órdenes</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('facturas_finales')">Facturas</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('documentos-contables')">Documentos Contables</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-prov')">Directorio Talleres</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-corp')">Lista de Corporativos</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('lista-admin')">Lista Automotriz</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('unidades')">Unidades</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('accesos')">Accesos (Credenciales)</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('flujo-trabajo')">Flujo de Trabajo</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>"""

# Administrador replacement:
target_admin = """                <!-- ========== ADMINISTRADOR ========== -->
                {% if usuario.datos_perfil.subrol == 'Administrador' %}
                <button class="btn-sidebar" onclick="verCotizacionesMas10000()">Cotizaciones +10000</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('liberar-doc-contable')">Liberar Doc. Contable</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>"""

repl_admin = """                <!-- ========== ADMINISTRADOR ========== -->
                {% if usuario.datos_perfil.subrol == 'Administrador' %}
                <button class="btn-sidebar" onclick="verCotizacionesMas10000()">Cotizaciones +10000</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('liberar-doc-contable')">Liberar Doc. Contable</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('flujo-trabajo')">Flujo de Trabajo</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>"""

# Jefatura adjustment (place Flujo de Trabajo above Analitica too, for full consistency):
target_jef = """                <button class="btn-sidebar" onclick="cambiarVistaAdmin('panel-control')">Panel de Control</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('flujo-trabajo')">Flujo de Trabajo</button>"""

repl_jef = """                <button class="btn-sidebar" onclick="cambiarVistaAdmin('panel-control')">Panel de Control</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('flujo-trabajo')">Flujo de Trabajo</button>
                <button class="btn-sidebar" onclick="cambiarVistaAdmin('analitica')">Analítica</button>"""

is_crlf_html = '\r\n' in html_text
html_norm = html_text.replace('\r\n', '\n')

def replace_html_block(content, t, r, name):
    t_n = t.replace('\r\n', '\n')
    r_n = r.replace('\r\n', '\n')
    if t_n in content:
        print(f"SUCCESS: {name}")
        return content.replace(t_n, r_n, 1)
    else:
        print(f"FAILED: {name}")
        return content

html_norm = replace_html_block(html_norm, target_sup, repl_sup, "Supervisor Flujo de Trabajo button")
html_norm = replace_html_block(html_norm, target_admin, repl_admin, "Administrador Flujo de Trabajo button")
html_norm = replace_html_block(html_norm, target_jef, repl_jef, "Jefatura Flujo de Trabajo button reordered")

if is_crlf_html:
    final_html = html_norm.replace('\n', '\r\n')
else:
    final_html = html_norm

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("administracion.html update complete.")

