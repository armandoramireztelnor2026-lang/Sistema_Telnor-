import re

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\seccion_reportes.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update renderizarTablaReportes
# Find the start of the list loop
start_loop = js.find("lista.forEach(f => {")
end_loop = js.find("actualizarKPIs(totalGasto, pendientesDoc50, pendientesOC);")

new_loop = """
    lista.forEach(f => {
        let ticketIdFunc = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : null;
        let ticket_base = ticketIdFunc || f.id_reporte || f.id || 'S/T';

        let numCotizaciones = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones.length : 1;

        for (let idx = 0; idx < numCotizaciones; idx++) {
            let cot = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones[idx] : null;
            let ticket = numCotizaciones > 1 ? `${ticket_base} (Op ${idx+1})` : ticket_base;
            let realId = ticket_base; // For comments

            let reporteOrig = (window.reportesGlobal || []).find(r => String(r.id) === ticket_base) || {};
            let pendienteHTML = '<span style="background:#ef4444; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Pendiente</span>';

            let numEco = f.unidad ? `8090-${f.unidad.replace('8090-', '')}` : pendienteHTML;
            let fechaTicket = f.fecha || reporteOrig.fecha || pendienteHTML;

            // Determinar el Estado
            let estado = 'N/A';
            if (f.is_unassigned) {
                estado = "Pendiente de Cotización";
            } else if (f.entregado === 'Sí') {
                estado = "Finalizado / Histórico";
            } else if (f.estado === 'Cancelado_Cotizacion_Cara') {
                estado = "Incosteable";
            } else {
                let apAdmin = f.aprobado_admin !== undefined ? f.aprobado_admin : (f.estado === 'Confirmada');
                let apCorp = f.aprobado_corp !== undefined ? f.aprobado_corp : (f.estado === 'Confirmada');
                let confirmadaTotal = (apAdmin && apCorp);

                if (confirmadaTotal) {
                    estado = "Esperando Reparación";
                } else {
                    let tieneCotizacion = f.cotizaciones && f.cotizaciones.length > 0;
                    if (!tieneCotizacion) {
                        estado = "Pendiente de Cotización";
                    } else {
                        if (!apAdmin || !apCorp) {
                            estado = "Esperando Aprobación";
                        }
                    }
                }
                if(f.estado === 'Confirmada' && f.entregado !== 'Sí') {
                    estado = "Validación y PIN";
                }
                if(f.factura_pdf && f.liberado !== 'Sí') {
                    estado = "Liberación Doc";
                }
                if(f.liberado === 'Sí' && !f.numero_doc50) {
                    estado = "Cierre Interno";
                }
            }
            
            // Asignar el estado al objeto para el filtrado
            f.estado_calculado = estado;

            let compania = f.compania || pendienteHTML;
            let departamento = f.departamento || f.area || reporteOrig.departamento || pendienteHTML;
            let cope = f.cope || reporteOrig.cope || pendienteHTML;
            let ciudad = f.ciudad || reporteOrig.ciudad || pendienteHTML;

            // Data from cotizacion if exists, else from ticket
            let retroRaw = cot ? (cot.retro || pendienteHTML) : (f.retro || pendienteHTML);
            let tempDiv = document.createElement('div'); tempDiv.innerHTML = retroRaw; let retro = tempDiv.textContent || tempDiv.innerText || pendienteHTML;
            retro = retro.replace(/\\[TICKET:.*?\\]\\s*REPORTE ORIGINAL DEL CHOFER:\\s*/i, '').trim();
            if (retro === 'Pendiente' || retro === '') retro = pendienteHTML;

            let costoNum = cot ? parseFloat(cot.precio || 0) : (f.precio ? parseFloat(f.precio) : 0);
            totalGasto += costoNum;
            let costo = costoNum > 0 ? costoNum.toLocaleString('en-US') : '0.00';
            
            let proveedor = f.proveedor || pendienteHTML;

            let numPedido = cot ? (cot.numero_cotizacion_asignacion || pendienteHTML) : (f.numero_cotizacion_asignacion || pendienteHTML);
            let pdfPedido = cot ? (cot.pdf_cotizacion_asignacion || cot.pdf_cotizacion) : (f.pdf_cotizacion_asignacion || f.pdf_cotizacion);
            let btnPdfPedido = pdfPedido ?
                `<button class="btn-info" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${pdfPedido}')">📄 Ver PDF</button>` :
                pendienteHTML;
                
            let realPedido = cot ? cot.numero_cotizacion_asignacion : f.numero_cotizacion_asignacion;
            if (!realPedido) pendientesOC++;

            let numOrden = cot ? (cot.numero_orden || pendienteHTML) : (f.numero_orden || pendienteHTML);

            let numFactura = cot ? (cot.factura_folio || pendienteHTML) : (f.factura_folio || pendienteHTML);
            let pdfFact = cot ? (cot.factura_pdf || cot.pdf_fiscal) : (f.pdf_fiscal || f.factura_pdf);
            let btnPdfFactura = pdfFact ?
                `<button class="btn-success-modal" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${pdfFact}')">📄 Ver PDF</button>` :
                pendienteHTML;

            let numContable = cot ? (cot.numero_doc50 || pendienteHTML) : (f.numero_doc50 || pendienteHTML);
            let realDoc50 = cot ? cot.numero_doc50 : f.numero_doc50;
            if (!realDoc50) pendientesDoc50++;
            
            let hasComment = f.comentarios && f.comentarios.trim() !== "";
            let btnColor = hasComment ? "#0284c7" : "#475569";
            let is_unass = f.is_unassigned ? "true" : "false";

            let commentSafe = f.comentarios ? f.comentarios.replace(/'/g, "\\\\\\'").replace(/"/g, "&quot;").replace(/\\n/g, "\\\\\\n").replace(/\\r/g, "") : "";
            let autorSafe = f.autor_comentario ? f.autor_comentario.replace(/'/g, "\\\\\\'").replace(/"/g, "&quot;") : "";

            let btnText = hasComment ? "💬 Ver/Actualizar Comentario" : "💬 Añadir Comentario";
            let btnComentarios = `<button onclick="abrirModalComentarios('${realId}', ${is_unass}, '${commentSafe}', '${autorSafe}')" style="background:${btnColor}; color:white; border:none; padding:5px 10px; border-radius:12px; font-size:0.85em; cursor:pointer;">${btnText}</button>`;

            if (f.eliminado_por && !hasComment) {
                btnComentarios = `<div style="max-width:150px; white-space:normal; font-size:0.85em; font-weight:600; word-wrap:break-word; margin-bottom:5px; color:#f87171;">Comentario eliminado por: ${f.eliminado_por}</div>` + btnComentarios;
            } else if (hasComment) {
                let preview = f.comentarios.length > 50 ? f.comentarios.substring(0, 50) + "..." : f.comentarios;
                btnComentarios = `<div style="max-width:150px; white-space:normal; font-size:0.85em; word-wrap:break-word; margin-bottom:5px; color:#ffffff;">${preview}</div>` + btnComentarios;
            }

            let nombreSup = f.responsable || pendienteHTML;
            let fechaEntrada = f.fecha || pendienteHTML;
            let fechaSalida = f.fecha_cierre || pendienteHTML;
            let tiempoTaller = pendienteHTML;
            
            // Calculate days in shop for Top 10
            f.dias_taller = 0;
            if (fechaEntrada !== pendienteHTML && fechaSalida !== pendienteHTML) {
                let f1 = new Date(f.fecha);
                let f2 = new Date(f.fecha_cierre);
                if (!isNaN(f1) && !isNaN(f2)) {
                    let diffDays = Math.ceil(Math.abs(f2 - f1) / (1000 * 60 * 60 * 24));
                    tiempoTaller = diffDays + ' día(s)';
                    f.dias_taller = diffDays;
                }
            }

            let isOperando = f.is_unassigned ? true : (f.entregado === 'Sí');
            let statusUnidad = isOperando
                ? '<span style="background:#10b981; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Operando</span>'
                : '<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">No Operando</span>';

            // Clean values for data attributes to prevent HTML breaking the attributes
            let cleanProv = proveedor === pendienteHTML ? 'pendiente' : proveedor.toLowerCase().replace(/<[^>]*>?/gm, '');
            let cleanCiudad = ciudad === pendienteHTML ? 'pendiente' : ciudad.toLowerCase().replace(/<[^>]*>?/gm, '');
            let cleanEco = numEco === pendienteHTML ? 'pendiente' : numEco.replace(/<[^>]*>?/gm, '');

            // Set row info for filtering
            let rowHtml = `
                <tr data-ticket="${ticket_base}" data-eco="${cleanEco}" data-prov="${cleanProv}" data-ciudad="${cleanCiudad}" data-estado="${estado}">
                    <td><input type="checkbox" class="chk-reporte" value="${ticket}"></td>
                    <td><strong>${ticket}</strong></td>
                    <td>${numEco}</td>
                    <td>${fechaTicket}</td>
                    <td><span style="background:#0ea5e9; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">${estado}</span></td>
                    <td>${statusUnidad}</td>
                    <td>${compania}</td>
                    <td>${departamento}</td>
                    <td>${cope}</td>
                    <td>${ciudad}</td>
                    <td><div style="max-width:200px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${retro}</div></td>
                    <td data-costo="${costoNum}"><strong>$${costo}</strong></td>
                    <td>${proveedor}</td>
                    <td>${nombreSup}</td>
                    <td>${fechaEntrada}</td>
                    <td>${tiempoTaller}</td>
                    <td>${fechaSalida}</td>
                    <td>${numPedido}</td>
                    <td>${btnPdfPedido}</td>
                    <td>${numOrden}</td>
                    <td>${numFactura}</td>
                    <td>${btnPdfFactura}</td>
                    <td>${numContable}</td>
                    <td>${btnComentarios}</td>
                </tr>
            `;
            tbody.innerHTML += rowHtml;
        }
    });
"""

js = js[:start_loop] + new_loop + js[end_loop:]

# 2. Add confirmation to imprimirSeleccion
js = js.replace("""function imprimirSeleccion() {
    let rows = getSelectedRows();""", """function imprimirSeleccion() {
    let rows = getSelectedRows();
    if(rows.length === 0) {
        alert("Selecciona al menos un ticket para imprimir.");
        return;
    }
    if(!confirm("¿Estás seguro de que deseas generar un reporte PDF para imprimir con los " + rows.length + " registros seleccionados?")) {
        return;
    }""")

# 3. Add confirmation to exportarExcel
js = js.replace("""function exportarExcel() {
    // Si no hay seleccionados, exportamos todos los visibles
    let rows = getSelectedRows();""", """function exportarExcel() {
    // Si no hay seleccionados, exportamos todos los visibles
    let rows = getSelectedRows();
    let table = document.getElementById('tabla-exportable-reportes');
    let trs = table.getElementsByTagName('tr');
    let targetRows = rows.length > 0 ? rows : Array.from(trs).slice(1).filter(tr => tr.style.display !== 'none' && tr.cells.length > 1);
    
    if(targetRows.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }
    
    if(!confirm("¿Estás seguro de que deseas exportar a Excel " + targetRows.length + " registros?")) {
        return;
    }
""")
# fix targetRows duplicated logic in exportarExcel since we moved it up:
js = js.replace("""    // Data
    let targetRows = rows.length > 0 ? rows : Array.from(trs).slice(1).filter(tr => tr.style.display !== 'none' && tr.cells.length > 1);
    
    if(targetRows.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }""", """    // Data (targetRows was already defined above)""")

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\seccion_reportes.js", "w", encoding="utf-8") as f:
    f.write(js)
