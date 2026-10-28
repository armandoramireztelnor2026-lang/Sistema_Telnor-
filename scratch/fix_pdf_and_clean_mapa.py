# -*- coding: utf-8 -*-
import sys

print("Applying updates: removing duplicate download button from Mapa de Etapas and fixing PDF export...")

# 1. Update templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the export card from mapa-etapas-grid
export_card = """                            <a href="javascript:void(0)" onclick="descargarDiagramaFlujo()" class="nav-rapida-paso" style="border-top: 3px solid #10b981; background: rgba(16, 185, 129, 0.08);" title="Descargar Diagrama de Flujo en PDF">
                                <span class="nav-rapida-num" style="color: #34d399;">EXPORTAR</span>
                                <span class="nav-rapida-nombre" style="color: #86efac;">📥 Descargar PDF</span>
                            </a>"""

export_card_norm = export_card.replace('\r\n', '\n')
html_norm = html.replace('\r\n', '\n')

if export_card_norm in html_norm:
    html_norm = html_norm.replace(export_card_norm, '')
    print("Removed duplicate download card from Mapa de Etapas.")
else:
    print("Warning: export_card_norm not found directly.")

# Update subtitle to 11 pasos operativos
html_norm = html_norm.replace('11 pasos operativos + Exportación', '11 pasos operativos de punta a punta')

# Update CSS for mapa-etapas-grid
old_grid_css = """                    @media (min-width: 1200px) {
                        .mapa-etapas-grid {
                            grid-template-columns: repeat(6, 1fr);
                        }
                    }"""

new_grid_css = """                    @media (min-width: 1200px) {
                        .mapa-etapas-grid {
                            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        }
                    }"""

html_norm = html_norm.replace(old_grid_css.replace('\r\n', '\n'), new_grid_css.replace('\r\n', '\n'))

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html_norm)
print("Updated templates/administracion.html.")

# 2. Update static/script.js: fix descargarDiagramaFlujo()
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_marker = "function descargarDiagramaFlujo() {"
end_marker = "function imprimirDiagramaDirecto() {"

idx1 = js.find(start_marker)
idx2 = js.find(end_marker)

if idx1 != -1 and idx2 != -1:
    new_descargar_js = """function descargarDiagramaFlujo() {
    // 1. Asegurar que todas las etapas del diagrama estén visibles antes de exportar
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

    // 2. Ocultar temporalmente los botones del mapa de navegación de etapas
    const mapaEtapas = contenedorOriginal.querySelector('.mapa-etapas-contenedor');
    const estadoMapa = mapaEtapas ? mapaEtapas.style.display : '';
    if (mapaEtapas) {
        mapaEtapas.style.display = 'none';
    }

    // 3. Insertar encabezado institucional temporal en el contenedor
    const headerPdf = document.createElement('div');
    headerPdf.id = 'flujo-pdf-temp-header';
    headerPdf.style.textAlign = 'center';
    headerPdf.style.padding = '10px 10px 22px 10px';
    headerPdf.style.marginBottom = '25px';
    headerPdf.style.borderBottom = '2px solid #1f395a';
    headerPdf.innerHTML = `
        <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
            TELNOR • DIAGRAMA DE FLUJO DE TRABAJO
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 4px;">
            Sistema Integral de Flota Automotriz • Procedimiento Operativo Oficial de Tickets
        </div>
        <div style="font-size: 0.76rem; color: #38bdf8; margin-top: 5px; font-weight: 700;">
            Fecha de emisión: ${new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </div>
    `;
    contenedorOriginal.insertBefore(headerPdf, contenedorOriginal.firstChild);

    // 4. Insertar pie de página institucional temporal en el contenedor
    const footerPdf = document.createElement('div');
    footerPdf.id = 'flujo-pdf-temp-footer';
    footerPdf.style.textAlign = 'center';
    footerPdf.style.padding = '20px 10px 10px 10px';
    footerPdf.style.marginTop = '30px';
    footerPdf.style.borderTop = '1px solid #1f395a';
    footerPdf.innerHTML = `
        <div style="font-size: 0.74rem; color: #64748b; font-weight: 700;">
            Documento de control interno institucional • Flujo completo de autorización, reparación, fiscalización y garantía Telnor
        </div>
    `;
    contenedorOriginal.appendChild(footerPdf);

    // Recordar posición previa de scroll y desplazar a la parte superior para calibrar el lienzo de html2canvas
    const scrollPrevio = window.scrollY;
    window.scrollTo(0, 0);

    const fechaHoy = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Diagrama_Flujo_Trabajo_Telnor_${fechaHoy}.pdf`;

    // Opciones para captura directa del contenedor en el DOM (sin envoltorios fijos que provoquen páginas en blanco)
    const opciones = {
        margin: [0.35, 0.25, 0.35, 0.25], // pulgadas (superior, izquierda, inferior, derecha)
        filename: nombreArchivo,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: '#081322'
        },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
        pagebreak: { 
            mode: ['css', 'legacy'],
            avoid: ['.flujo-box', '.etapa-header-bar', '.flujo-flecha-conector', '.lane-cotizacion']
        }
    };

    const cleanup = () => {
        if (mapaEtapas) mapaEtapas.style.display = estadoMapa;
        if (headerPdf && headerPdf.parentNode) headerPdf.parentNode.removeChild(headerPdf);
        if (footerPdf && footerPdf.parentNode) footerPdf.parentNode.removeChild(footerPdf);
        window.scrollTo(0, scrollPrevio);
        if (btn) {
            btn.innerHTML = textoOriginal;
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    };

    // Pequeña pausa de 120ms para que el navegador procese el renderizado del header antes de tomar la captura
    setTimeout(() => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opciones).from(contenedorOriginal).save().then(() => {
                cleanup();
                if (btn) {
                    btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">✅</span><span>¡Descargado!</span>';
                    setTimeout(() => {
                        btn.innerHTML = textoOriginal;
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }, 2500);
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
    }, 120);
}

"""
    js = js[:idx1] + new_descargar_js + js[idx2:]
    
    # Also in imprimirDiagramaDirecto, make sure .mapa-etapas-contenedor is hidden
    if '.mapa-etapas-contenedor' not in js[idx2:]:
        js = js.replace("a, .nav-rapida-paso, button { display: none !important; }",
                        "a, .nav-rapida-paso, .mapa-etapas-contenedor, button { display: none !important; }")
    
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated static/script.js.")
else:
    print(f"Error finding function boundaries: idx1={idx1}, idx2={idx2}")

print("All done!")

