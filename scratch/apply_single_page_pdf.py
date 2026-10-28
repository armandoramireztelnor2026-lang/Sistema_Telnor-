# -*- coding: utf-8 -*-
import sys

print("Applying update: Single-page continuous PDF export...")

# 1. Update static/script.js to compute custom format [8.5, altoTotalIn]
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
        btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">⏳</span><span>Generando 1 hoja...</span>';
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

    // Recordar posición previa de scroll y desplazar a la parte superior para calibrar el lienzo
    const scrollPrevio = window.scrollY;
    window.scrollTo(0, 0);

    const fechaHoy = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Diagrama_Flujo_Trabajo_Telnor_${fechaHoy}.pdf`;

    // 5. CALCULAR DIMENSIONES DINÁMICAS EXACTAS PARA 1 SOLA HOJA CONTINUA
    // Ancho base: 8.5 pulgadas (estándar). El largo se calcula proporcional al flujo completo.
    const anchoPulgadas = 8.5;
    const margenHoriz = 0.25; // 0.25 in cada lado
    const margenVert = 0.35;  // 0.35 in arriba y abajo
    const anchoImprimible = anchoPulgadas - (margenHoriz * 2); // 8.0 in

    const anchoRealPx = contenedorOriginal.offsetWidth || 1000;
    const altoRealPx = contenedorOriginal.offsetHeight || 4200;

    // Altura proporcional del contenido en pulgadas
    const altoContenidoIn = anchoImprimible * (altoRealPx / anchoRealPx);
    // Altura total de la página: incluye márgenes + 0.4 in de margen de seguridad para garantizar 1 sola página
    const altoTotalIn = parseFloat((altoContenidoIn + (margenVert * 2) + 0.4).toFixed(2));

    const opciones = {
        margin: [margenVert, margenHoriz, margenVert, margenHoriz],
        filename: nombreArchivo,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: '#081322'
        },
        jsPDF: { 
            unit: 'in', 
            format: [anchoPulgadas, altoTotalIn], 
            orientation: 'portrait' 
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

    // Pausa de 120ms para asegurar que el navegador aplique los cambios visuales antes de renderizar
    setTimeout(() => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opciones).from(contenedorOriginal).save().then(() => {
                cleanup();
                if (btn) {
                    btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">✅</span><span>¡1 Hoja Lista!</span>';
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
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated static/script.js with single-page export.")
else:
    print(f"Error finding function boundaries: idx1={idx1}, idx2={idx2}")

# 2. Update button in templates/administracion.html with tooltip
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_btn_span = """                            <span style="font-size: 0.95rem; line-height: 1;">📥</span>
                            <span>Descargar PDF</span>"""

new_btn_span = """                            <span style="font-size: 0.95rem; line-height: 1;">📥</span>
                            <span>Descargar PDF (1 Hoja)</span>"""

if old_btn_span in html:
    html = html.replace(old_btn_span, new_btn_span)
    print("Updated button text in templates/administracion.html to 'Descargar PDF (1 Hoja)'.")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("All updates applied!")

