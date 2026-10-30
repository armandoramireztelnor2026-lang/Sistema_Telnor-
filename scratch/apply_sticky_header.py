# -*- coding: utf-8 -*-

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

target_html = '''                    <div class="table-responsive" style="overflow-x: auto; max-width: 100%;">
                        <table style="min-width: 1500px; white-space: nowrap;" id="tabla-exportable-reportes">'''

repl_html = '''                    <div class="table-responsive contenedor-tabla-reportes" style="overflow-x: auto; overflow-y: auto; max-height: calc(100vh - 280px); min-height: 420px; max-width: 100%; position: relative; border-radius: 8px; border: 1px solid #1f395a; background: #0b1728;">
                        <table style="min-width: 1500px; white-space: nowrap; margin-top: 0;" id="tabla-exportable-reportes">'''

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
    print("SUCCESS: administracion.html updated with sticky header container.")
else:
    print("ERROR: Target not found in administracion.html")

# 2. Append sticky header rules to static/style.css
sticky_css = """

/* ========================================================
   ENCABEZADO FIJO (STICKY HEADER) PARA SECCIÓN DE REPORTES
   Permite desplazamiento horizontal pero mantiene fija la
   cabecera de nombres de columnas verticalmente al scrollear
   ======================================================== */
.contenedor-tabla-reportes {
    overflow-x: auto !important;
    overflow-y: auto !important;
    max-height: calc(100vh - 280px) !important;
    min-height: 420px !important;
    max-width: 100% !important;
    position: relative !important;
    border-radius: 8px !important;
    border: 1px solid #1f395a !important;
    background: #0b1728 !important;
}

#tabla-exportable-reportes {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    margin-top: 0 !important;
}

#tabla-exportable-reportes thead {
    position: sticky !important;
    top: 0 !important;
    z-index: 30 !important;
}

#tabla-exportable-reportes thead tr {
    position: sticky !important;
    top: 0 !important;
    z-index: 30 !important;
}

#tabla-exportable-reportes th {
    position: sticky !important;
    top: 0 !important;
    z-index: 30 !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.6) !important;
}
"""

with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

is_crlf_css = '\r\n' in css
if "ENCABEZADO FIJO (STICKY HEADER) PARA SECCIÓN DE REPORTES" not in css:
    if is_crlf_css:
        sticky_css = sticky_css.replace('\n', '\r\n')
    css += sticky_css
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("SUCCESS: style.css updated with sticky header rules.")
else:
    print("INFO: Sticky header rules already present in style.css.")

