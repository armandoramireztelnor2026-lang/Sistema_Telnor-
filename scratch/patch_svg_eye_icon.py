import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update button for cfg-codigo-emisor
old_btn_main = """<button type="button" onclick="toggleMostrarPassword('cfg-codigo-emisor', this)" style="position: absolute; right: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; cursor: pointer; font-size: 1.15rem; color: #94a3b8;" title="Mostrar / Ocultar código">👁️</button>"""

new_btn_main = """<button type="button" onclick="toggleMostrarPassword('cfg-codigo-emisor', this)" style="position: absolute; right: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; cursor: pointer; color: #94a3b8; transition: color 0.2s ease;" title="Mostrar código"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg></button>"""

if old_btn_main in html:
    html = html.replace(old_btn_main, new_btn_main, 1)
    print("Botón en formulario principal actualizado con icono SVG")
else:
    print("Aviso: No se encontró old_btn_main exacto, buscando alternativo...")
    # fallback search
    pos_input = html.find('id="cfg-codigo-emisor"')
    pos_btn = html.find('<button', pos_input)
    pos_btn_end = html.find('</button>', pos_btn) + 9
    print("Actualizando botón de cfg-codigo-emisor:")
    html = html[:pos_btn] + new_btn_main + html[pos_btn_end:]
    print("Reemplazado vía posición")

# Update input in modal-nueva-cuenta-codigo
old_modal_input = """<div>
                            <label style="display: block; color: #cbd5e1; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;">Código / Contraseña de Aplicación:</label>
                            <input type="password" id="modal-nueva-cuenta-codigo" placeholder="Contraseña de app de 16 caracteres" style="width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: white; padding: 9px 12px; border-radius: 6px;">
                        </div>"""

new_modal_input = """<div>
                            <label style="display: block; color: #cbd5e1; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;">Código / Contraseña de Aplicación:</label>
                            <div style="position: relative; width: 100%; display: flex; align-items: center;">
                                <input type="password" id="modal-nueva-cuenta-codigo" placeholder="Contraseña de app de 16 caracteres" style="width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: white; padding: 9px 40px 9px 12px; border-radius: 6px;">
                                <button type="button" onclick="toggleMostrarPassword('modal-nueva-cuenta-codigo', this)" style="position: absolute; right: 6px; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; cursor: pointer; color: #94a3b8; transition: color 0.2s ease;" title="Mostrar código">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                </button>
                            </div>
                        </div>"""

if old_modal_input in html:
    html = html.replace(old_modal_input, new_modal_input, 1)
    print("Input de contraseña en modal actualizado con icono SVG")

# Bump cache buster
html = html.replace('configuraciones_jefatura.js?v=4', 'configuraciones_jefatura.js?v=5')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("templates/administracion.html guardado con éxito!")

# 2. Update static/configuraciones_jefatura.js
with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_toggle = """window.toggleMostrarPassword = function(inputId, btnEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (btnEl) btnEl.innerText = '🙈';
    } else {
        input.type = 'password';
        if (btnEl) btnEl.innerText = '👁️';
    }
};"""

new_toggle = """const SVG_OJO_ABIERTO = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;

const SVG_OJO_CERRADO = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #38bdf8;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

window.toggleMostrarPassword = function(inputId, btnEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isSmall = btnEl && btnEl.querySelector('svg')?.getAttribute('width') === '18';
    const svgAbierto = isSmall ? SVG_OJO_ABIERTO.replace(/width="20" height="20"/g, 'width="18" height="18"') : SVG_OJO_ABIERTO;
    const svgCerrado = isSmall ? SVG_OJO_CERRADO.replace(/width="20" height="20"/g, 'width="18" height="18"') : SVG_OJO_CERRADO;

    if (input.type === 'password') {
        input.type = 'text';
        if (btnEl) {
            btnEl.innerHTML = svgCerrado;
            btnEl.title = 'Ocultar código';
        }
    } else {
        input.type = 'password';
        if (btnEl) {
            btnEl.innerHTML = svgAbierto;
            btnEl.title = 'Mostrar código';
        }
    }
};"""

if old_toggle in js:
    js = js.replace(old_toggle, new_toggle, 1)
    print("toggleMostrarPassword reemplazado con iconos SVG sin emojis")
else:
    print("Aviso: No se encontró old_toggle exacto en JS")
    pos_toggle = js.find('window.toggleMostrarPassword')
    pos_toggle_end = js.find('};', pos_toggle) + 2
    js = js[:pos_toggle] + new_toggle + js[pos_toggle_end:]
    print("Reemplazado por búsqueda de posición")

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("static/configuraciones_jefatura.js actualizado exitosamente!")

