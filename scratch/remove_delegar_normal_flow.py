with open('static/facturas_principal.js', 'r', encoding='utf-8', newline='') as f:
    text = f.read()

# 1. Update line 727 in tabla-facturas (Cotizaciones y Órdenes)
target_1_lf = '''                        // Unidad entregada, pendiente de liberación por Admin
                        if (subrolAct === 'Supervisor') {
                            btnAccion += `<button class="btn-cobertura" style="font-size:0.8em; padding:8px 10px; width:100%; box-sizing: border-box; border:none; margin-top:2px; font-weight:bold; cursor:pointer; border-radius:6px;" onclick="delegarLiberarTicket('${f.id}', '${f.unidad || ''}')">🛡️ Asumir Proceso (Liberar por Ausencia)</button>`;
                            btnAccion += `<button class="btn-info" style="background:#f59e0b; color:white; font-size:0.75em; padding:6px 10px; width:100%; box-sizing: border-box; border:none; margin-top:3px; font-weight:bold; cursor:pointer; border-radius:4px;" onclick="notificarAdminLiberacion('${f.id}')">🔔 Notificar al Administrador</button>`;
                        } else {'''

replacement_1_lf = '''                        // Unidad entregada, pendiente de liberación por Admin
                        if (subrolAct === 'Supervisor') {
                            btnAccion += `<span style="color:#f59e0b; font-size:0.8em; font-weight:bold; margin-top:3px; text-align:center;">⌛ Pendiente Liberación (Admin)</span>`;
                            btnAccion += `<button class="btn-info" style="background:#f59e0b; color:white; font-size:0.75em; padding:6px 10px; width:100%; box-sizing: border-box; border:none; margin-top:3px; font-weight:bold; cursor:pointer; border-radius:4px;" onclick="notificarAdminLiberacion('${f.id}')">🔔 Notificar al Administrador</button>`;
                        } else {'''

# 2. Update line 985 in tabla-facturas-finales (Facturas)
target_2_lf = '''                            // Nuevo botón manual para notificar al Admin
                            if (f.liberado_admin === false) {
                                if (subrolAct === 'Supervisor') {
                                    btnAdminExtra += `<button class="btn-cobertura" onclick="delegarLiberarTicket('${f.id}', '${f.unidad || ''}')" style="display:block; width:100%; margin:0; margin-top:5px;">🛡️ Asumir Proceso (Liberar por Ausencia)</button>`;
                                } else {
                                    btnAdminExtra += `<button class="btn-liberar-facturacion" onclick="liberarTicketAdmin('${f.id}')" style="display:block; width:100%; margin:0; margin-top:5px;">🔓 Liberar Facturación</button>`;
                                }
                            }'''

replacement_2_lf = '''                            // Nuevo botón manual para notificar al Admin
                            if (f.liberado_admin === false) {
                                if (subrolAct === 'Supervisor') {
                                    btnAdminExtra += `<span style="color:#f59e0b; font-size:0.8em; font-weight:bold; margin-top:5px; text-align:center;">⌛ Pendiente Liberación (Admin)</span>`;
                                } else {
                                    btnAdminExtra += `<button class="btn-liberar-facturacion" onclick="liberarTicketAdmin('${f.id}')" style="display:block; width:100%; margin:0; margin-top:5px;">🔓 Liberar Facturación</button>`;
                                }
                            }'''

if '\r\n' in text:
    target_1 = target_1_lf.replace('\n', '\r\n')
    replacement_1 = replacement_1_lf.replace('\n', '\r\n')
    target_2 = target_2_lf.replace('\n', '\r\n')
    replacement_2 = replacement_2_lf.replace('\n', '\r\n')
else:
    target_1 = target_1_lf
    replacement_1 = replacement_1_lf
    target_2 = target_2_lf
    replacement_2 = replacement_2_lf

assert target_1 in text, "target_1 not found in facturas_principal.js"
assert target_2 in text, "target_2 not found in facturas_principal.js"

text = text.replace(target_1, replacement_1, 1)
text = text.replace(target_2, replacement_2, 1)

with open('static/facturas_principal.js', 'w', encoding='utf-8', newline='') as f:
    f.write(text)

print("Updated static/facturas_principal.js successfully")

# Bump cache buster in administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8', newline='') as f:
    html = f.read()

assert 'src="/static/facturas_principal.js?v=70"' in html
html = html.replace('src="/static/facturas_principal.js?v=70"', 'src="/static/facturas_principal.js?v=71"')

with open('templates/administracion.html', 'w', encoding='utf-8', newline='') as f:
    f.write(html)

print("Updated templates/administracion.html cache buster to v=71 successfully")

