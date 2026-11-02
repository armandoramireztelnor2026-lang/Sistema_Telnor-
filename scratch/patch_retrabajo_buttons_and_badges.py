# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8', newline='') as f:
    html = f.read()

target_btn = '<button class="btn-sidebar btn-sidebar-retrabajo" id="btn-sidebar-liberar-retrabajo" title="Liberar/Retrabajo" type="button" onclick="cambiarVistaAdmin(\'liberar-retrabajo\')">Liberar/Retrabajo <span id="badge-liberar-retrabajo" style="display:none; background:#ef4444; color:white; font-size:0.75rem; padding:2px 7px; border-radius:10px; margin-left:6px; font-weight:800;">0</span></button>'
replacement_btn = '<button class="btn-sidebar btn-sidebar-retrabajo" id="btn-sidebar-liberar-retrabajo" title="Liberar/Retrabajo" type="button" onclick="cambiarVistaAdmin(\'liberar-retrabajo\')">Liberar/Retrabajo</button>'

assert target_btn in html, 'target_btn not found in administracion.html'
html = html.replace(target_btn, replacement_btn)

# Bump script.js cache buster
assert 'src="/static/script.js?v=1000051"' in html
html = html.replace('src="/static/script.js?v=1000051"', 'src="/static/script.js?v=1000052"')

with open('templates/administracion.html', 'w', encoding='utf-8', newline='') as f:
    f.write(html)
print('Updated templates/administracion.html successfully')

# 2. Update static/script.js
with open('static/script.js', 'r', encoding='utf-8', newline='') as f:
    js = f.read()

# Action buttons in Liberar/Retrabajo table
old_actions_lf = '''                    <td style="white-space: nowrap; vertical-align: middle; text-align: center; padding: 12px 10px;">
                        <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
                            <button type="button" class="btn-info" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer;" onclick="abrirDetallesTicketRetrabajo('${ticketEscaped}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button type="button" class="btn-success" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: #10b981; border: none; color: white;" onclick="abrirModalValidarCodigoLiberacion('${ticketEscaped}', '${unidadEscaped}', '${tallerEscaped}', '${choferEscaped}')">
                                ✅ Liberar Retrabajo
                            </button>
                        </div>
                    </td>'''

new_actions_lf = '''                    <td style="white-space: nowrap; vertical-align: middle; text-align: center; padding: 10px 12px;">
                        <div style="display: flex; flex-direction: column; gap: 6px; width: 100%; min-width: 145px; box-sizing: border-box;">
                            <button type="button" class="btn-info" style="display: block; width: 100%; padding: 8px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; text-align: center; box-sizing: border-box; margin: 0; border: none;" onclick="abrirDetallesTicketRetrabajo('${ticketEscaped}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button type="button" class="btn-success" style="display: block; width: 100%; padding: 8px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; text-align: center; box-sizing: border-box; margin: 0; background: #10b981; border: none; color: white;" onclick="abrirModalValidarCodigoLiberacion('${ticketEscaped}', '${unidadEscaped}', '${tallerEscaped}', '${choferEscaped}')">
                                ✅ Liberar Retrabajo
                            </button>
                        </div>
                    </td>'''

# Badge in cargarLiberarRetrabajosSupervisor
old_badge_lib_lf = '''        const badge = document.getElementById('badge-liberar-retrabajo');
        if (badge) {
            if (retrabajos.length > 0) {
                badge.innerText = retrabajos.length;
                badge.style.display = 'inline-flex';
                badge.style.alignItems = 'center';
                badge.style.justifyContent = 'center';
            } else {
                badge.style.display = 'none';
            }
        }'''

new_badge_lib_lf = '''        const badge = document.getElementById('badge-liberar-retrabajo');
        if (badge) {
            badge.style.display = 'none';
        }'''

# Badge in actualizarBadgeLiberarRetrabajoSupervisor
old_badge_func_lf = '''window.actualizarBadgeLiberarRetrabajoSupervisor = async function() {
    const badge = document.getElementById('badge-liberar-retrabajo');
    if (!badge) return;
    try {
        const res = await fetch('/api/garantia/supervisor/por_liberar');
        const data = await res.json();
        const count = (data.retrabajos || []).length;
        if (count > 0) {
            badge.innerText = count;
            badge.style.display = 'inline-flex';
            badge.style.alignItems = 'center';
            badge.style.justifyContent = 'center';
        } else {
            badge.style.display = 'none';
        }
    } catch(e) {}
};'''

new_badge_func_lf = '''window.actualizarBadgeLiberarRetrabajoSupervisor = async function() {
    const badge = document.getElementById('badge-liberar-retrabajo');
    if (badge) badge.style.display = 'none';
};'''

# Badge in retrabajo proveedor
old_badge_prov1_lf = '''        const badgeProv = document.getElementById('badge-retrabajo-prov');
        if (badgeProv) {
            if (retrabajos.length > 0) {
                badgeProv.innerText = retrabajos.length;
                badgeProv.style.display = 'inline-flex';
                badgeProv.style.alignItems = 'center';
                badgeProv.style.justifyContent = 'center';
            } else {
                badgeProv.style.display = 'none';
            }
        }'''

new_badge_prov1_lf = '''        const badgeProv = document.getElementById('badge-retrabajo-prov');
        if (badgeProv) {
            badgeProv.style.display = 'none';
        }'''

def normalize(s):
    return s.replace('\n', '\r\n') if '\r\n' in js else s

assert normalize(old_actions_lf) in js, 'old_actions_lf not found in script.js'
assert normalize(old_badge_lib_lf) in js, 'old_badge_lib_lf not found in script.js'
assert normalize(old_badge_func_lf) in js, 'old_badge_func_lf not found in script.js'

js = js.replace(normalize(old_actions_lf), normalize(new_actions_lf), 1)
js = js.replace(normalize(old_badge_lib_lf), normalize(new_badge_lib_lf), 1)
js = js.replace(normalize(old_badge_func_lf), normalize(new_badge_func_lf), 1)

if normalize(old_badge_prov1_lf) in js:
    js = js.replace(normalize(old_badge_prov1_lf), normalize(new_badge_prov1_lf))

with open('static/script.js', 'w', encoding='utf-8', newline='') as f:
    f.write(js)
print('Updated static/script.js successfully')

