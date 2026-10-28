# -*- coding: utf-8 -*-
import sys
import re

print("Starting update script...")

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

header_css = """
                    /* ESTILOS DE LA CABECERA DEL FLUJO (AISLADA DE .top-bar) */
                    .flujo-header-box {
                        display: flex !important;
                        flex-direction: column !important;
                        align-items: flex-start !important;
                        justify-content: flex-start !important;
                        gap: 14px !important;
                        width: 100% !important;
                        box-sizing: border-box !important;
                        margin-bottom: 22px !important;
                        padding: 20px 24px !important;
                        background: #081322 !important;
                        border: 1px solid #1f395a !important;
                        border-radius: 14px !important;
                    }
                    .flujo-header-box h2 {
                        white-space: normal !important;
                        color: #ffffff !important;
                        margin: 0 !important;
                    }
                    .flujo-header-box button {
                        width: auto !important;
                        flex-shrink: 0 !important;
                        margin: 0 !important;
                    }
"""

if '.flujo-header-box {' not in html:
    html = html.replace('.flujo-contenedor-principal {', header_css + '\n                    .flujo-contenedor-principal {')
    print("Added .flujo-header-box CSS")
else:
    print(".flujo-header-box CSS already present")

# Replace top-bar in the header of flujo-trabajo
old_header_tag = '<div class="top-bar" style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 22px; padding: 20px 24px; background: #081322; border: 1px solid #1f395a; border-radius: 14px;">'
if old_header_tag in html:
    html = html.replace(old_header_tag, '<div class="flujo-header-box">')
    print("Replaced top-bar class with flujo-header-box")
else:
    print("old_header_tag not found directly, checking regex...")
    pattern = r'<div class="top-bar"[^>]*id="vista-flujo-trabajo"[^>]*>|<div id="vista-flujo-trabajo"[^>]*>[\s\S]*?<div class="top-bar"[^>]*>'
    # Let's inspect around vista-flujo-trabajo

# Ensure the buttons wrapper inside flujo-header-box has width: 100% and box-sizing: border-box
old_buttons_wrapper = 'style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; background: #0b1c30; padding: 8px 12px; border-radius: 10px; border: 1px solid #1f395a; width: fit-content; max-width: 100%;"'
new_buttons_wrapper = 'style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; background: #0b1c30; padding: 8px 12px; border-radius: 10px; border: 1px solid #1f395a; width: 100%; box-sizing: border-box;"'

if old_buttons_wrapper in html:
    html = html.replace(old_buttons_wrapper, new_buttons_wrapper)
    print("Updated buttons wrapper width to 100%")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated templates/administracion.html successfully.")

# 2. Update static/script.js descargarDiagramaFlujo()
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Locate descargarDiagramaFlujo function
start_marker = "function descargarDiagramaFlujo() {"
end_marker = "function imprimirDiagramaDirecto() {"

idx_start = js.find(start_marker)
idx_end = js.find(end_marker)

if idx_start != -1 and idx_end != -1:
    new_descargar_fn = """function descargarDiagramaFlujo() {
    // 1. Asegurar que todas las etapas estén visibles antes de exportar
    if (typeof filtrarRutaFlujo === 'function') {
        filtrarRutaFlujo('todos');
    }

    const contenedorOriginal = document.querySelector('.flujo-contenedor-principal');
    if (!contenedorOriginal) {
        alert("No se encontró el contenedor del diagrama de flujo.");
        return;
    }

    const btn = document.getElementById('btn-descargar-flujo');
    const textoOriginal = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">⏳</span><span>Generando PDF...</span>';
        btn.disabled = true;
        btn.style.opacity = '0.7';
    }

    // 2. Crear un contenedor de exportación en el DOM raíz (fuera de .main-content)
    // Esto elimina por completo el desfase del sidebar de 260px y el scroll horizontal,
    // evitando que el PDF salga recortado a los lados o con bandas vacías.
    const wrapperPdf = document.createElement('div');
    wrapperPdf.id = 'flujo-pdf-export-wrapper';
    wrapperPdf.style.position = 'fixed';
    wrapperPdf.style.top = '0';
    wrapperPdf.style.left = '0';
    wrapperPdf.style.width = '820px';
    wrapperPdf.style.backgroundColor = '#081322';
    wrapperPdf.style.color = '#ffffff';
    wrapperPdf.style.zIndex = '999999';
    wrapperPdf.style.margin = '0';
    wrapperPdf.style.padding = '20px 24px';
    wrapperPdf.style.boxSizing = 'border-box';
    wrapperPdf.style.overflow = 'visible';

    // 3. Clonar el diagrama dentro del wrapper aislado
    const clon = contenedorOriginal.cloneNode(true);
    clon.style.width = '100%';
    clon.style.maxWidth = '100%';
    clon.style.minWidth = '100%';
    clon.style.margin = '0';
    clon.style.padding = '0';
    clon.style.background = 'transparent';
    clon.style.border = 'none';
    clon.style.boxShadow = 'none';

    // Eliminar la barra de anclas de navegación rápida dentro del PDF
    const navRapida = clon.querySelector('.nav-rapida-paso')?.closest('div[style*="overflow-x"]')?.parentElement || clon.querySelector('.nav-rapida-paso')?.parentElement?.parentElement;
    if (navRapida) {
        navRapida.remove();
    }
    // Remover botones que pudieran existir dentro del contenido
    clon.querySelectorAll('button').forEach(b => b.remove());

    // Ajustar columnas de bifurcación (Paso 4) para que quepan completas una al lado de la otra sin desbordar
    clon.querySelectorAll('.lane-cotizacion').forEach(lane => {
        lane.style.minWidth = '0';
        lane.style.flex = '1';
        lane.style.maxWidth = '48%';
        lane.style.boxSizing = 'border-box';
        lane.style.padding = '14px 12px';
    });

    // Ajustar tarjetas y conectores para evitar cortes a la mitad entre páginas (paginación limpia por partes)
    clon.querySelectorAll('.flujo-box, .etapa-header-bar, .flujo-flecha-conector, .lane-cotizacion').forEach(el => {
        el.style.pageBreakInside = 'avoid';
        el.style.breakInside = 'avoid';
        el.style.boxSizing = 'border-box';
    });

    // Encabezado institucional en el PDF
    const headerPdf = document.createElement('div');
    headerPdf.style.textAlign = 'center';
    headerPdf.style.padding = '10px 10px 18px 10px';
    headerPdf.style.marginBottom = '20px';
    headerPdf.style.borderBottom = '2px solid #1f395a';
    headerPdf.innerHTML = `
        <div style="font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
            TELNOR • DIAGRAMA DE FLUJO DE TRABAJO
        </div>
        <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">
            Sistema Integral de Flota Automotriz • Procedimiento Operativo Oficial de Tickets
        </div>
        <div style="font-size: 0.76rem; color: #38bdf8; margin-top: 4px; font-weight: 700;">
            Fecha de emisión: ${new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </div>
    `;
    wrapperPdf.appendChild(headerPdf);
    wrapperPdf.appendChild(clon);

    // Pie de página institucional en el PDF
    const footerPdf = document.createElement('div');
    footerPdf.style.textAlign = 'center';
    footerPdf.style.padding = '18px 10px 10px 10px';
    footerPdf.style.marginTop = '25px';
    footerPdf.style.borderTop = '1px solid #1f395a';
    footerPdf.innerHTML = `
        <div style="font-size: 0.74rem; color: #64748b; font-weight: 700;">
            Documento de control interno institucional • Flujo completo de autorización, reparación, fiscalización y garantía Telnor
        </div>
    `;
    wrapperPdf.appendChild(footerPdf);

    // Adjuntar wrapper al body para que html2canvas lo mida exactamente desde x=0 a x=820px
    document.body.appendChild(wrapperPdf);

    const fechaHoy = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Diagrama_Flujo_Trabajo_Telnor_${fechaHoy}.pdf`;

    // Opciones calibradas al ancho exacto de 820px en hoja Carta vertical (Letter)
    // con márgenes simétricos de 0.25 in y sin parámetros de recorte arbitrarios
    const opciones = {
        margin: [0.35, 0.25, 0.35, 0.25], // pulgadas
        filename: nombreArchivo,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: '#081322',
            scrollY: 0,
            scrollX: 0
        },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
        pagebreak: { 
            mode: ['css', 'legacy'],
            avoid: ['.flujo-box', '.etapa-header-bar', '.flujo-flecha-conector', '.lane-cotizacion']
        }
    };

    const cleanup = () => {
        if (wrapperPdf && wrapperPdf.parentNode) {
            wrapperPdf.parentNode.removeChild(wrapperPdf);
        }
        if (btn) {
            btn.innerHTML = textoOriginal;
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    };

    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opciones).from(wrapperPdf).save().then(() => {
            if (btn) {
                btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">✅</span><span>¡Descargado!</span>';
                setTimeout(cleanup, 2000);
            } else {
                cleanup();
            }
        }).catch(err => {
            console.error("Error al generar PDF con html2pdf:", err);
            cleanup();
            imprimirDiagramaDirecto();
        });
    } else {
        cleanup();
        imprimirDiagramaDirecto();
    }
}

"""
    js = js[:idx_start] + new_descargar_fn + js[idx_end:]
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated static/script.js successfully.")
else:
    print(f"Could not find function markers in static/script.js: idx_start={idx_start}, idx_end={idx_end}")

