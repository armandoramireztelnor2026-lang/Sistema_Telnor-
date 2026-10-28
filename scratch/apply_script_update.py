# -*- coding: utf-8 -*-
with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_marker = "function descargarDiagramaFlujo() {"
end_marker = "window.descargarDiagramaFlujo = descargarDiagramaFlujo;"

idx1 = js.find(start_marker)
idx2 = js.find(end_marker)

print(f"idx1={idx1}, idx2={idx2}")

if idx1 != -1 and idx2 != -1:
    new_functions_js = """function descargarDiagramaFlujo() {
    // 1. Confirmación obligatoria al usuario
    if (!confirm("¿Deseas generar y descargar el Diagrama de Flujo de Trabajo en formato PDF (1 hoja compacta)?")) {
        return;
    }

    // 2. Asegurar que todas las etapas del diagrama estén visibles antes de exportar
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

    // 3. Ocultar temporalmente los botones del mapa de navegación de etapas
    const mapaEtapas = contenedorOriginal.querySelector('.mapa-etapas-contenedor');
    const estadoMapa = mapaEtapas ? mapaEtapas.style.display : '';
    if (mapaEtapas) {
        mapaEtapas.style.display = 'none';
    }

    // 4. Activar modo compacto temporal (oculta descripciones largas <p> para una sola hoja compacta)
    contenedorOriginal.classList.add('flujo-modo-pdf-compacto');

    // 5. Insertar encabezado institucional sin nombres exclusivos de empresas
    const headerPdf = document.createElement('div');
    headerPdf.id = 'flujo-pdf-temp-header';
    headerPdf.style.textAlign = 'center';
    headerPdf.style.padding = '8px 10px 16px 10px';
    headerPdf.style.marginBottom = '18px';
    headerPdf.style.borderBottom = '2px solid #1f395a';
    headerPdf.innerHTML = `
        <div style="font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
            SISTEMA INTEGRAL DE FLOTA AUTOMOTRIZ • DIAGRAMA DE FLUJO DE TRABAJO
        </div>
        <div style="font-size: 0.86rem; color: #94a3b8; margin-top: 4px;">
            Procedimiento Operativo Oficial de Gestión y Liquidación de Tickets de Servicio
        </div>
        <div style="font-size: 0.74rem; color: #38bdf8; margin-top: 4px; font-weight: 700;">
            Fecha de emisión: ${new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </div>
    `;
    contenedorOriginal.insertBefore(headerPdf, contenedorOriginal.firstChild);

    // 6. Insertar pie de página institucional sin nombres exclusivos de empresas
    const footerPdf = document.createElement('div');
    footerPdf.id = 'flujo-pdf-temp-footer';
    footerPdf.style.textAlign = 'center';
    footerPdf.style.padding = '14px 10px 8px 10px';
    footerPdf.style.marginTop = '20px';
    footerPdf.style.borderTop = '1px solid #1f395a';
    footerPdf.innerHTML = `
        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700;">
            Documento de control interno institucional • Flujo completo de autorización, reparación, fiscalización y garantía automotriz
        </div>
    `;
    contenedorOriginal.appendChild(footerPdf);

    // Recordar posición previa de scroll y desplazar a la parte superior para calibrar el lienzo
    const scrollPrevio = window.scrollY;
    window.scrollTo(0, 0);

    const fechaHoy = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Diagrama_Flujo_Trabajo_Operativo_${fechaHoy}.pdf`;

    // 7. CALCULAR DIMENSIONES DINÁMICAS EXACTAS PARA 1 SOLA HOJA COMPACTA
    const anchoPulgadas = 8.5;
    const margenHoriz = 0.25; // 0.25 in cada lado
    const margenVert = 0.30;  // 0.30 in arriba y abajo
    const anchoImprimible = anchoPulgadas - (margenHoriz * 2); // 8.0 in

    const anchoRealPx = contenedorOriginal.offsetWidth || 1000;
    const altoRealPx = contenedorOriginal.offsetHeight || 1600;

    // Altura proporcional del contenido en pulgadas
    const altoContenidoIn = anchoImprimible * (altoRealPx / anchoRealPx);
    // Altura total de la página: incluye márgenes + 0.35 in de margen de seguridad para garantizar 1 sola página
    const altoTotalIn = parseFloat((altoContenidoIn + (margenVert * 2) + 0.35).toFixed(2));

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
        contenedorOriginal.classList.remove('flujo-modo-pdf-compacto');
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

    // Pausa de 120ms para asegurar que el navegador aplique los estilos compactos antes de renderizar
    setTimeout(() => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opciones).from(contenedorOriginal).save().then(() => {
                cleanup();
                if (btn) {
                    btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">✅</span><span>¡1 Hoja Descargada!</span>';
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

function imprimirDiagramaDirecto() {
    const contenedor = document.querySelector('.flujo-contenedor-principal');
    if (!contenedor) return;

    const ventana = window.open('', '_blank');
    if (!ventana) {
        alert("Por favor permite las ventanas emergentes para imprimir o guardar el diagrama como PDF.");
        return;
    }
    ventana.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Diagrama de Flujo de Trabajo Operativo - Flota Automotriz</title>
            <style>
                body {
                    background: #081322;
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    padding: 15px;
                    margin: 0;
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    max-width: 100% !important;
                }
                * { box-sizing: border-box; }
                a, .nav-rapida-paso, .mapa-etapas-contenedor, button, p { display: none !important; }
                .flujo-box { padding: 9px 12px !important; margin-bottom: 0 !important; }
                .flujo-box h4, .flujo-box h5 { margin: 0 !important; font-size: 0.92rem !important; }
                .lane-cotizacion { min-width: 0 !important; flex: 1 !important; padding: 10px 8px !important; }
                .flujo-flecha-conector { margin: 2px 0 !important; }
                .flujo-flecha-linea { height: 7px !important; }
                .etapa-header-bar { padding: 7px 12px !important; margin: 10px 0 6px 0 !important; }
                @page {
                    size: letter portrait;
                    margin: 8mm;
                }
                @media print {
                    body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
                    .flujo-box, .etapa-header-bar, .lane-cotizacion, .flujo-flecha-conector {
                        page-break-inside: avoid !important;
                        break-inside: avoid !important;
                    }
                }
            </style>
        </head>
        <body>
            <div style="text-align: center; margin-bottom: 18px; border-bottom: 2px solid #1f395a; padding-bottom: 10px;">
                <h1 style="color: #ffffff; margin: 0 0 5px 0; font-size: 1.45rem;">SISTEMA INTEGRAL DE FLOTA AUTOMOTRIZ • DIAGRAMA DE FLUJO DE TRABAJO</h1>
                <p style="display:block !important; margin: 0; color: #94a3b8; font-size: 0.88rem;">Procedimiento Operativo Oficial de Gestión y Liquidación de Tickets de Servicio</p>
            </div>
            ${contenedor.innerHTML}
            <script>
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 500);
                };
            <\/script>
        </body>
        </html>
    `);
    ventana.document.close();
}

"""
    js = js[:idx1] + new_functions_js + js[idx2:]
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated static/script.js successfully.")
else:
    print(f"Error finding markers: idx1={idx1}, idx2={idx2}")

