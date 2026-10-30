import re

# 1. Update static/style.css
with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css_rules = '''
/* BOTONES DE ACCION EN TABLA RETRABAJO DEL PROVEEDOR (DISEÑO HOMOGÉNEO VERTICAL) */
.btn-accion-retrabajo-prov {
    width: 170px !important;
    min-width: 170px !important;
    max-width: 170px !important;
    height: 36px !important;
    padding: 0 14px !important;
    border-radius: 8px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    text-align: center !important;
    white-space: nowrap !important;
    border: none !important;
    color: #ffffff !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

.btn-accion-retrabajo-detalles {
    background: #0284c7 !important;
    box-shadow: 0 3px 10px rgba(2, 132, 199, 0.35) !important;
}
.btn-accion-retrabajo-detalles:hover {
    background: #0369a1 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(2, 132, 199, 0.45) !important;
}

.btn-accion-retrabajo-ver {
    background: #10b981 !important;
    box-shadow: 0 3px 10px rgba(16, 185, 129, 0.35) !important;
}
.btn-accion-retrabajo-ver:hover {
    background: #059669 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(16, 185, 129, 0.45) !important;
}

.btn-accion-retrabajo-finalizar {
    background: #16a34a !important;
    box-shadow: 0 3px 10px rgba(22, 163, 74, 0.35) !important;
}
.btn-accion-retrabajo-finalizar:hover {
    background: #15803d !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(22, 163, 74, 0.45) !important;
}
'''

target_css = '.btn-footer-retrabajo-cerrar:hover {\n    background: #334155 !important;\n    transform: translateY(-1px) !important;\n    box-shadow: 0 6px 16px rgba(71, 85, 105, 0.35) !important;\n}'

if target_css in css:
    css = css.replace(target_css, target_css + '\n' + css_rules, 1)
    print("Added action buttons CSS to static/style.css")
else:
    print("target_css not found in static/style.css")

with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 2. Update static/script.js
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_actions_block = '''                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">
                        <div style="display: flex; gap: 6px; justify-content: center; align-items: center; flex-wrap: wrap;">
                            <button class="btn-info" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #0284c7; color: white; border: none;" onclick="abrirDetallesTicketRetrabajo('${ticketId}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button class="btn-success" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #10b981; color: white; border: none;" onclick="abrirDetalleRetrabajo('${ticketId}')">
                                Ver Retrabajo
                            </button>
                            <button class="btn-primary" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #16a34a; color: white; border: none;" onclick="marcarRetrabajoFinalizado('${ticketId}')">
                                Retrabajo Finalizado
                            </button>
                        </div>
                    </td>'''

new_actions_block = '''                    <td style="white-space: nowrap; vertical-align: middle; text-align: center; padding: 12px 10px;">
                        <div style="display: flex; flex-direction: column; gap: 8px; justify-content: center; align-items: center; width: 100%;">
                            <button type="button" class="btn-accion-retrabajo-prov btn-accion-retrabajo-detalles" onclick="abrirDetallesTicketRetrabajo('${ticketId}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button type="button" class="btn-accion-retrabajo-prov btn-accion-retrabajo-ver" onclick="abrirDetalleRetrabajo('${ticketId}')">
                                Ver Retrabajo
                            </button>
                            <button type="button" class="btn-accion-retrabajo-prov btn-accion-retrabajo-finalizar" onclick="marcarRetrabajoFinalizado('${ticketId}')">
                                Retrabajo Finalizado
                            </button>
                        </div>
                    </td>'''

if old_actions_block in js:
    js = js.replace(old_actions_block, new_actions_block, 1)
    print("Updated table action buttons in static/script.js")
else:
    print("old_actions_block not found in static/script.js")

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js)


# 3. Update templates/proveedores.html
with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update <th>Acciones</th> to ensure proper width and centering
old_th = '<th>Acciones</th>'
new_th = '<th style="text-align: center; min-width: 190px;">Acciones</th>'
if old_th in html:
    html = html.replace(old_th, new_th, 1)
    print("Updated <th>Acciones</th> in templates/proveedores.html")

# Bump cache versions
html = re.sub(r'href="/static/style\.css\?v=\d+"', 'href="/static/style.css?v=51065"', html)
html = re.sub(r'src="/static/script\.js\?v=\d+"', 'src="/static/script.js?v=1000038"', html)

with open('templates/proveedores.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated templates/proveedores.html successfully")

