import re

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\seccion_reportes.js", "r", encoding="utf-8") as f:
    js = f.read()

# I will replace the entire renderizarTablaReportes and exportarExcel logic to handle this perfectly.

# We need to find where renderizarTablaReportes starts and ends.
start_render = js.find("function renderizarTablaReportes(lista) {")
end_render = js.find("// ==========================================", start_render)

new_render = """function renderizarTablaReportes(lista) {
    const tbody = document.getElementById('tabla-seccion-reportes');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    // Reset KPIs
    let totalGasto = 0;
    let pendientesDoc50 = 0;
    let pendientesOC = 0;

    if (lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="24" style="text-align: center; color: #a3b1c6; padding: 20px;">No se encontraron resultados.</td></tr>`;
        actualizarKPIs(0, 0, 0);
        return;
    }

    lista.forEach(f => {
        let ticketIdFunc = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : null;
        let ticket = ticketIdFunc || f.id_reporte || f.id || 'S/T';

        let reporteOrig = (window.reportesGlobal || []).find(r => String(r.id) === ticket) || {};
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

        let proveedor = f.proveedor || pendienteHTML;
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

        // Variables for grouped data
        let htmlRetro = '';
        let htmlCosto = '';
        let htmlNumPedido = '';
        let htmlBtnPdfPedido = '';
        let htmlNumOrden = '';
        let htmlNumFactura = '';
        let htmlBtnPdfFactura = '';
        let htmlNumContable = '';
        
        let numCotizaciones = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones.length : 1;
        let costoTotalRow = 0;

        for (let idx = 0; idx < numCotizaciones; idx++) {
            let cot = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones[idx] : null;
            let bStyle = (idx < numCotizaciones - 1) ? 'border-bottom:1px solid #334155; margin-bottom:8px; padding-bottom:8px;' : '';
            let label = numCotizaciones > 1 ? `<strong style="color:#a3b1c6; font-size:0.8em; display:block;">Opción ${idx+1}:</strong>` : '';

            // Retro
            let retroRaw = cot ? (cot.retro || pendienteHTML) : (f.retro || pendienteHTML);
            let tempDiv = document.createElement('div'); tempDiv.innerHTML = retroRaw; let retroText = tempDiv.textContent || tempDiv.innerText || pendienteHTML;
            retroText = retroText.replace(/\\[TICKET:.*?\\]\\s*REPORTE ORIGINAL DEL CHOFER:\\s*/i, '').trim();
            if (retroText === 'Pendiente' || retroText === '') retroText = pendienteHTML;
            htmlRetro += `<div style="${bStyle}">${label}${retroText}</div>`;

            // Costo
            let costoNum = cot ? parseFloat(cot.precio || 0) : (f.precio ? parseFloat(f.precio) : 0);
            let costoStr = costoNum > 0 ? costoNum.toLocaleString('en-US') : '0.00';
            htmlCosto += `<div style="${bStyle}">${label}$${costoStr}</div>`;
            costoTotalRow += costoNum; // Only add one of them if we are summing total gasto? Actually, total gasto should only sum the winning one or the first one if multiple.
            // If multiple, normally only ONE is approved. Let's just sum all for now, or just the main `f.precio`.
            
            // Num Pedido
            let nPedido = cot ? (cot.numero_cotizacion_asignacion || pendienteHTML) : (f.numero_cotizacion_asignacion || pendienteHTML);
            htmlNumPedido += `<div style="${bStyle}">${label}${nPedido}</div>`;
            if(nPedido === pendienteHTML) pendientesOC++;

            // PDF Pedido
            let pPedido = cot ? (cot.pdf_cotizacion_asignacion || cot.pdf_cotizacion) : (f.pdf_cotizacion_asignacion || f.pdf_cotizacion);
            let btnP = pPedido ? `<button class="btn-info" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${pPedido}')">📄 Ver PDF</button>` : pendienteHTML;
            htmlBtnPdfPedido += `<div style="${bStyle}">${label}${btnP}</div>`;

            // Num Orden
            let nOrden = cot ? (cot.numero_orden || pendienteHTML) : (f.numero_orden || pendienteHTML);
            htmlNumOrden += `<div style="${bStyle}">${label}${nOrden}</div>`;

            // Num Factura
            let nFact = cot ? (cot.factura_folio || pendienteHTML) : (f.factura_folio || pendienteHTML);
            htmlNumFactura += `<div style="${bStyle}">${label}${nFact}</div>`;

            // PDF Factura
            let pFact = cot ? (cot.factura_pdf || cot.pdf_fiscal) : (f.pdf_fiscal || f.factura_pdf);
            let btnF = pFact ? `<button class="btn-success-modal" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${pFact}')">📄 Ver PDF</button>` : pendienteHTML;
            htmlBtnPdfFactura += `<div style="${bStyle}">${label}${btnF}</div>`;

            // Num Contable (Doc 50)
            let nContable = cot ? (cot.numero_doc50 || pendienteHTML) : (f.numero_doc50 || pendienteHTML);
            htmlNumContable += `<div style="${bStyle}">${label}${nContable}</div>`;
            if(nContable === pendienteHTML) pendientesDoc50++;
        }

        // For KPI Gasto, use the main ticket price (the winning one)
        let ticketGasto = f.precio ? parseFloat(f.precio) : 0;
        totalGasto += ticketGasto;

        // Comments
        let hasComment = f.comentarios && f.comentarios.trim() !== "";
        let btnColor = hasComment ? "#0284c7" : "#475569";
        let is_unass = f.is_unassigned ? "true" : "false";
        let commentSafe = f.comentarios ? f.comentarios.replace(/'/g, "\\\\\\'").replace(/"/g, "&quot;").replace(/\\n/g, "\\\\n").replace(/\\r/g, "") : "";
        let autorSafe = f.autor_comentario ? f.autor_comentario.replace(/'/g, "\\\\\\'").replace(/"/g, "&quot;") : "";
        let btnText = hasComment ? "💬 Ver/Actualizar Comentario" : "💬 Añadir Comentario";
        let btnComentarios = `<button onclick="abrirModalComentarios('${ticket}', ${is_unass}, '${commentSafe}', '${autorSafe}')" style="background:${btnColor}; color:white; border:none; padding:5px 10px; border-radius:12px; font-size:0.85em; cursor:pointer;">${btnText}</button>`;

        if (f.eliminado_por && !hasComment) {
            btnComentarios = `<div style="max-width:150px; white-space:normal; font-size:0.85em; font-weight:600; word-wrap:break-word; margin-bottom:5px; color:#f87171;">Comentario eliminado por: ${f.eliminado_por}</div>` + btnComentarios;
        } else if (hasComment) {
            let preview = f.comentarios.length > 50 ? f.comentarios.substring(0, 50) + "..." : f.comentarios;
            btnComentarios = `<div style="max-width:150px; white-space:normal; font-size:0.85em; word-wrap:break-word; margin-bottom:5px; color:#ffffff;">${preview}</div>` + btnComentarios;
        }

        // Clean values for data attributes to prevent HTML breaking the attributes
        let cleanProv = proveedor === pendienteHTML ? 'pendiente' : proveedor.toLowerCase().replace(/<[^>]*>?/gm, '');
        let cleanCiudad = ciudad === pendienteHTML ? 'pendiente' : ciudad.toLowerCase().replace(/<[^>]*>?/gm, '');
        let cleanEco = numEco === pendienteHTML ? 'pendiente' : numEco.replace(/<[^>]*>?/gm, '');

        // Set row info for filtering
        let rowHtml = `
            <tr data-ticket="${ticket}" data-eco="${cleanEco}" data-prov="${cleanProv}" data-ciudad="${cleanCiudad}" data-estado="${estado}">
                <td style="vertical-align:top; padding-top:15px;"><input type="checkbox" class="chk-reporte" value="${ticket}"></td>
                <td style="vertical-align:top; padding-top:15px;"><strong>${ticket}</strong></td>
                <td style="vertical-align:top; padding-top:15px;">${numEco}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaTicket}</td>
                <td style="vertical-align:top; padding-top:15px;"><span style="background:#0ea5e9; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">${estado}</span></td>
                <td style="vertical-align:top; padding-top:15px;">${statusUnidad}</td>
                <td style="vertical-align:top; padding-top:15px;">${compania}</td>
                <td style="vertical-align:top; padding-top:15px;">${departamento}</td>
                <td style="vertical-align:top; padding-top:15px;">${cope}</td>
                <td style="vertical-align:top; padding-top:15px;">${ciudad}</td>
                <td style="vertical-align:top; padding-top:15px;"><div style="max-width:250px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${htmlRetro}</div></td>
                <td style="vertical-align:top; padding-top:15px;" data-costo="${ticketGasto}"><strong>${htmlCosto}</strong></td>
                <td style="vertical-align:top; padding-top:15px;">${proveedor}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreSup}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaEntrada}</td>
                <td style="vertical-align:top; padding-top:15px;">${tiempoTaller}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaSalida}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumPedido}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlBtnPdfPedido}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumOrden}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlBtnPdfFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumContable}</td>
                <td style="vertical-align:top; padding-top:15px;">${btnComentarios}</td>
            </tr>
        `;
        tbody.innerHTML += rowHtml;
    });

    actualizarKPIs(totalGasto, pendientesDoc50, pendientesOC);
}
"""

js = js[:start_render] + new_render + "\n" + js[end_render:]

# Update the exportarExcel to handle `\n` generated by `.innerText` properly (join with " | ")
# Right now, my exportarExcel has: `text = text.replace(/\\r?\\n|\\r/g, ' ');`
# I'll change it to `text = text.replace(/\\r?\\n|\\r/g, ' | ');`

js = js.replace("text = text.replace(/\\r?\\n|\\r/g, ' ');", "text = text.replace(/\\r?\\n|\\r/g, ' | ');")

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\seccion_reportes.js", "w", encoding="utf-8") as f:
    f.write(js)

