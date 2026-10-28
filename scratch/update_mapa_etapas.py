# -*- coding: utf-8 -*-
import sys

print("Applying Mapa de Etapas improvements...")

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace .nav-rapida-paso CSS with the new responsive grid CSS
old_css_target = """                    /* Barra rápida superior */
                    .nav-rapida-paso {
                        flex: 1;
                        min-width: 95px;
                        background: #0b1c30;
                        border: 1px solid #1f395a;
                        border-radius: 8px;
                        padding: 8px 6px;
                        text-align: center;
                        text-decoration: none;
                        display: block;
                        transition: all 0.2s;
                    }"""

new_css = """                    /* MAPA DE ETAPAS - GRID MODERNO Y ESPACIOSO (CERO AMONTONAMIENTO) */
                    .mapa-etapas-contenedor {
                        background: #0b1c30;
                        border: 1px solid #1f395a;
                        border-radius: 14px;
                        padding: 16px 18px;
                        margin-bottom: 26px;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                    }
                    .mapa-etapas-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 12px;
                        flex-wrap: wrap;
                        gap: 8px;
                    }
                    .mapa-etapas-title {
                        color: #94a3b8;
                        font-size: 0.72rem;
                        font-weight: 800;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }
                    .mapa-etapas-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
                        gap: 10px;
                        width: 100%;
                        box-sizing: border-box;
                    }
                    @media (min-width: 1200px) {
                        .mapa-etapas-grid {
                            grid-template-columns: repeat(6, 1fr);
                        }
                    }
                    @media (min-width: 768px) and (max-width: 1199px) {
                        .mapa-etapas-grid {
                            grid-template-columns: repeat(4, 1fr);
                        }
                    }
                    @media (max-width: 767px) {
                        .mapa-etapas-grid {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                    
                    /* Tarjeta de navegación de cada paso */
                    .nav-rapida-paso {
                        background: #081322;
                        border: 1.5px solid #1f395a;
                        border-radius: 10px;
                        padding: 10px 8px;
                        text-align: center;
                        text-decoration: none;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        gap: 4px;
                        transition: all 0.2s ease;
                        min-height: 58px;
                        box-sizing: border-box;
                        cursor: pointer;
                    }
                    .nav-rapida-paso:hover {
                        transform: translateY(-2px);
                        border-color: #38bdf8;
                        background: rgba(56, 189, 248, 0.12);
                        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
                    }
                    .nav-rapida-num {
                        font-size: 0.68rem;
                        font-weight: 800;
                        letter-spacing: 0.6px;
                        text-transform: uppercase;
                        line-height: 1;
                    }
                    .nav-rapida-nombre {
                        font-size: 0.77rem;
                        color: #ffffff;
                        font-weight: 700;
                        line-height: 1.25;
                        text-align: center;
                        white-space: normal;
                        word-break: normal;
                    }
                    
                    /* Efecto de foco temporal al hacer clic */
                    .flujo-step-highlight {
                        animation: pulsoFocoPaso 1.8s ease;
                    }
                    @keyframes pulsoFocoPaso {
                        0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.8); }
                        50% { box-shadow: 0 0 25px 4px rgba(56, 189, 248, 0.5); }
                        100% { box-shadow: none; }
                    }"""

# Normalize CRLF
old_css_norm = old_css_target.replace('\r\n', '\n')
new_css_norm = new_css.replace('\r\n', '\n')
html_norm = html.replace('\r\n', '\n')

if old_css_norm in html_norm:
    html_norm = html_norm.replace(old_css_norm, new_css_norm)
    print("Replaced CSS for nav-rapida-paso.")
else:
    print("Warning: old_css_norm not found, checking partial...")

# Update @media print to include .mapa-etapas-contenedor
html_norm = html_norm.replace('.no-print, .btn-flujo-tab, .nav-rapida-paso, #btn-descargar-flujo',
                              '.no-print, .btn-flujo-tab, .nav-rapida-paso, .mapa-etapas-contenedor, #btn-descargar-flujo')

# Replace the HTML block of BARRA DE ACCESO DIRECTO ENTRE ETAPAS
old_html_start = "<!-- BARRA DE ACCESO DIRECTO ENTRE ETAPAS -->"
old_html_end = "<!-- ======================================================== -->\n                    <!-- SECUENCIA VISUAL COMPLETA CON TARJETAS SEPARADAS         -->"

idx1 = html_norm.find(old_html_start)
idx2 = html_norm.find(old_html_end)

if idx1 != -1 and idx2 != -1:
    new_mapa_html = """<!-- BARRA DE ACCESO DIRECTO ENTRE ETAPAS (GRID RESPONSIVO, CERO AMONTONAMIENTO) -->
                    <div class="mapa-etapas-contenedor">
                        <div class="mapa-etapas-header">
                            <span class="mapa-etapas-title">
                                🗺️ MAPA DE ETAPAS (HAZ CLIC PARA ENFOCAR CADA SECCIÓN)
                            </span>
                            <span style="color: #64748b; font-size: 0.72rem; font-weight: 600;">
                                11 pasos operativos + Exportación
                            </span>
                        </div>
                        <div class="mapa-etapas-grid">
                            <a href="#etapa-1-reporte" onclick="enfocarPasoFlujo('etapa-1-reporte', event)" class="nav-rapida-paso" style="border-top: 3px solid #0284c7;">
                                <span class="nav-rapida-num" style="color: #38bdf8;">PASO 1</span>
                                <span class="nav-rapida-nombre">📝 Reporte</span>
                            </a>
                            <a href="#etapa-2-asignacion" onclick="enfocarPasoFlujo('etapa-2-asignacion', event)" class="nav-rapida-paso" style="border-top: 3px solid #f59e0b;">
                                <span class="nav-rapida-num" style="color: #fbbf24;">PASO 2</span>
                                <span class="nav-rapida-nombre">🎯 Asignación</span>
                            </a>
                            <a href="#etapa-3-cotizacion" onclick="enfocarPasoFlujo('etapa-3-cotizacion', event)" class="nav-rapida-paso" style="border-top: 3px solid #10b981;">
                                <span class="nav-rapida-num" style="color: #34d399;">PASO 3</span>
                                <span class="nav-rapida-nombre">🔍 Cotización</span>
                            </a>
                            <a href="#etapa-4-bifurcacion" onclick="enfocarPasoFlujo('etapa-4-bifurcacion', event)" class="nav-rapida-paso" style="border-top: 3px solid #6366f1;">
                                <span class="nav-rapida-num" style="color: #a5b4fc;">PASO 4</span>
                                <span class="nav-rapida-nombre">⚖️ Cotiz. ≤ / > 10k</span>
                            </a>
                            <a href="#etapa-5-reparacion" onclick="enfocarPasoFlujo('etapa-5-reparacion', event)" class="nav-rapida-paso" style="border-top: 3px solid #0284c7;">
                                <span class="nav-rapida-num" style="color: #38bdf8;">PASO 5</span>
                                <span class="nav-rapida-nombre">🛠️ Reparación y PIN</span>
                            </a>
                            <a href="#etapa-6-entrega" onclick="enfocarPasoFlujo('etapa-6-entrega', event)" class="nav-rapida-paso" style="border-top: 3px solid #10b981;">
                                <span class="nav-rapida-num" style="color: #34d399;">PASO 6</span>
                                <span class="nav-rapida-nombre">🔑 PIN y Garantía</span>
                            </a>
                            <a href="#etapa-7-verificacion-admin" onclick="enfocarPasoFlujo('etapa-7-verificacion-admin', event)" class="nav-rapida-paso" style="border-top: 3px solid #6366f1;">
                                <span class="nav-rapida-num" style="color: #a5b4fc;">PASO 7</span>
                                <span class="nav-rapida-nombre">🔢 Verificación Admin</span>
                            </a>
                            <a href="#etapa-8-factura-taller" onclick="enfocarPasoFlujo('etapa-8-factura-taller', event)" class="nav-rapida-paso" style="border-top: 3px solid #10b981;">
                                <span class="nav-rapida-num" style="color: #34d399;">PASO 8</span>
                                <span class="nav-rapida-nombre">🧾 Factura Taller</span>
                            </a>
                            <a href="#etapa-9-revision-supervisor" onclick="enfocarPasoFlujo('etapa-9-revision-supervisor', event)" class="nav-rapida-paso" style="border-top: 3px solid #f59e0b;">
                                <span class="nav-rapida-num" style="color: #fbbf24;">PASO 9</span>
                                <span class="nav-rapida-nombre">🔍 Revisión Factura</span>
                            </a>
                            <a href="#etapa-10-doc-contable" onclick="enfocarPasoFlujo('etapa-10-doc-contable', event)" class="nav-rapida-paso" style="border-top: 3px solid #10b981;">
                                <span class="nav-rapida-num" style="color: #86efac;">PASO 10</span>
                                <span class="nav-rapida-nombre">🏁 Cierre Contable</span>
                            </a>
                            <a href="#etapa-11-garantia" onclick="enfocarPasoFlujo('etapa-11-garantia', event)" class="nav-rapida-paso" style="border-top: 3px solid #a855f7;">
                                <span class="nav-rapida-num" style="color: #c084fc;">PASO 11</span>
                                <span class="nav-rapida-nombre">🛡️ Garantía</span>
                            </a>
                            <a href="javascript:void(0)" onclick="descargarDiagramaFlujo()" class="nav-rapida-paso" style="border-top: 3px solid #10b981; background: rgba(16, 185, 129, 0.08);" title="Descargar Diagrama de Flujo en PDF">
                                <span class="nav-rapida-num" style="color: #34d399;">EXPORTAR</span>
                                <span class="nav-rapida-nombre" style="color: #86efac;">📥 Descargar PDF</span>
                            </a>
                        </div>
                    </div>

                    """
    html_norm = html_norm[:idx1] + new_mapa_html + html_norm[idx2:]
    print("Replaced Mapa de Etapas HTML successfully.")
else:
    print(f"Error: indices not found: idx1={idx1}, idx2={idx2}")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html_norm)

# 2. Update static/script.js: add enfocarPasoFlujo and ensure descargarDiagramaFlujo cleans .mapa-etapas-contenedor
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add enfocarPasoFlujo if not present
if 'function enfocarPasoFlujo(' not in js:
    enfocar_js = """
// =========================================================
// ENFOCAR PASO DEL DIAGRAMA CON SCROLL SUAVE Y RESALTE
// =========================================================
function enfocarPasoFlujo(idEtapa, ev) {
    if (ev) ev.preventDefault();
    const el = document.getElementById(idEtapa);
    if (!el) return;

    // Si la etapa está oculta por un filtro de pestañas, restablecer a 'todos'
    if (el.style.display === 'none') {
        if (typeof filtrarRutaFlujo === 'function') {
            filtrarRutaFlujo('todos');
        }
    }

    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.add('flujo-step-highlight');
    setTimeout(() => {
        el.classList.remove('flujo-step-highlight');
    }, 1800);
}
"""
    # Append right above descargarDiagramaFlujo
    idx_desc = js.find('function descargarDiagramaFlujo() {')
    if idx_desc != -1:
        js = js[:idx_desc] + enfocar_js + '\n' + js[idx_desc:]
        print("Added enfocarPasoFlujo to static/script.js")
    else:
        js += enfocar_js
        print("Appended enfocarPasoFlujo to static/script.js")

# In descargarDiagramaFlujo, ensure .mapa-etapas-contenedor is cleanly removed in cloned PDF
if '.mapa-etapas-contenedor' not in js:
    js = js.replace("const navRapida = clon.querySelector('.nav-rapida-paso')?.closest('div[style*=\"overflow-x\"]')?.parentElement || clon.querySelector('.nav-rapida-paso')?.parentElement?.parentElement;",
                    "const navRapida = clon.querySelector('.mapa-etapas-contenedor') || clon.querySelector('.nav-rapida-paso')?.closest('div');")
    print("Updated PDF removal logic for .mapa-etapas-contenedor")

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Done! Both files updated.")

