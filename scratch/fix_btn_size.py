# -*- coding: utf-8 -*-
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                        <div style="display:flex; flex-direction:column; gap:8px; justify-content:flex-end;">
                            <button id="btn-filtro-garantia" type="button" onclick="toggleFiltroGarantia()"
                                style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:8px 12px; border-radius:5px; cursor:pointer; height:35px; display:inline-flex; align-items:center; justify-content:center; gap:6px; font-size:0.85em; font-weight:600; transition:all 0.2s; width:100%;"
                                title="Mostrar sólo tickets en garantía / retrabajo">
                                <span style="font-size:1.1em;">🛡️</span> Garantía / Retrabajo
                            </button>
                            <div style="display:flex; gap:8px;">
                                <button id="btn-filtro-reactivadas" type="button" onclick="toggleFiltroReactivadas()"
                                    style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:8px 12px; border-radius:5px; cursor:pointer; height:35px; display:inline-flex; align-items:center; gap:6px; font-size:0.85em; font-weight:600; transition:all 0.2s;"
                                    title="Mostrar sólo cotizaciones reactivadas de cotizaciones caras">
                                    <span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras
                                </button>
                                <button onclick="limpiarFiltrosReportes()"
                                    style="background:#475569; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; height:35px;">Limpiar</button>
                            </div>
                        </div>'''

replacement = '''                        <div style="display:flex; gap:8px; align-items:flex-end;">
                            <div style="display:flex; flex-direction:column; gap:8px;">
                                <button id="btn-filtro-garantia" type="button" onclick="toggleFiltroGarantia()"
                                    style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:8px 12px; border-radius:5px; cursor:pointer; height:35px; display:inline-flex; align-items:center; justify-content:center; gap:6px; font-size:0.85em; font-weight:600; transition:all 0.2s; box-sizing:border-box; width:100%; white-space:nowrap;"
                                    title="Mostrar sólo tickets en garantía / retrabajo">
                                    <span style="font-size:1.1em;">🛡️</span> Garantía / Retrabajo
                                </button>
                                <button id="btn-filtro-reactivadas" type="button" onclick="toggleFiltroReactivadas()"
                                    style="background:#334155; color:#cbd5e1; border:1px solid #475569; padding:8px 12px; border-radius:5px; cursor:pointer; height:35px; display:inline-flex; align-items:center; justify-content:center; gap:6px; font-size:0.85em; font-weight:600; transition:all 0.2s; box-sizing:border-box; width:100%; white-space:nowrap;"
                                    title="Mostrar sólo cotizaciones reactivadas de cotizaciones caras">
                                    <span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras
                                </button>
                            </div>
                            <button onclick="limpiarFiltrosReportes()"
                                style="background:#475569; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; height:35px; align-self:flex-end;">Limpiar</button>
                        </div>'''

is_crlf = '\r\n' in text
text_norm = text.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
repl_norm = replacement.replace('\r\n', '\n')

if target_norm in text_norm:
    text_norm = text_norm.replace(target_norm, repl_norm, 1)
    if is_crlf:
        final_text = text_norm.replace('\n', '\r\n')
    else:
        final_text = text_norm
    with open('templates/administracion.html', 'w', encoding='utf-8') as f:
        f.write(final_text)
    print("SUCCESS: Button size and container updated in administracion.html")
else:
    print("ERROR: Target not found")

