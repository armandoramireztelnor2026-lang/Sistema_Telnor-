// static/seccion_reportes.js

document.addEventListener('DOMContentLoaded', () => {
    // Inicialización si es necesaria
});

let reportesCombinadosGlobal = []; // Para tener acceso a todos los datos sin recargar

async function cargarSeccionReportes() {
    try {
        if (!window.reportesGlobal || window.reportesGlobal.length === 0) {
            let resRep = await fetch(`/api/reportes/lista?_=${new Date().getTime()}`);
            let dataRep = await resRep.json();
            window.reportesGlobal = dataRep.reportes || [];
        }

        const res = await fetch(`/api/seccion_reportes/lista?_=${new Date().getTime()}`);
        const data = await res.json();

        if (data.status === 'error') {
            console.error("Error al obtener la sección de reportes:", data.message);
            return;
        }

        const facturas = data.facturas || [];
        const reportes = window.reportesGlobal || [];
        
        let asignadosIds = new Set();
        facturas.forEach(f => {
            let t = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : (f.id_reporte || f.id || 'S/T');
            if (t) asignadosIds.add(String(t));
        });

        let listaCombinada = [...facturas];

        // Filtrar tickets eliminados, rechazados o cancelados y evitar duplicados
        let idsProcesados = new Set();
        listaCombinada = listaCombinada.filter(t => {
            if (t.estado === 'Cancelado_Cotizacion_Cara') return false;
            if (t.estado === 'Rechazado') return false;
            if (t.estado === 'Eliminado') return false;

            let tId = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(t) : (t.id_reporte || t.id);
            if (!tId) return true;
            if (idsProcesados.has(String(tId))) return false;
            idsProcesados.add(String(tId));
            
            return true;
        });

        // Ordenamos del más reciente al más antiguo
        listaCombinada.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        reportesCombinadosGlobal = listaCombinada;

        renderizarTablaReportes(reportesCombinadosGlobal);

    } catch (err) {
        console.error("Error cargando la sección de reportes:", err);
    }
}

function renderizarTablaReportes(lista) {
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

        // NUEVO CALCULO DE TIEMPO DEL TICKET
        let fechaTicketFinalizado = f.fecha_cierre || pendienteHTML;
        let tiempoTicket = "En Proceso";
        
        if (fechaTicket !== pendienteHTML && fechaTicketFinalizado !== pendienteHTML) {
            let ft1 = new Date(fechaTicket);
            let ft2 = new Date(fechaTicketFinalizado);
            if (!isNaN(ft1) && !isNaN(ft2)) {
                let diffMsT = Math.abs(ft2 - ft1);
                let diffDaysT = Math.floor(diffMsT / (1000 * 60 * 60 * 24));
                let diffHoursT = Math.floor((diffMsT % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let diffMinutesT = Math.floor((diffMsT % (1000 * 60 * 60)) / (1000 * 60));
                tiempoTicket = `${diffDaysT}d ${diffHoursT}h ${diffMinutesT}m`;
            }
        }

        // Determinar el Estado
        let estado = 'N/A';
        let tieneCotizacion = f.cotizaciones && f.cotizaciones.length > 0;
        let isCara = f.precio && parseFloat(f.precio) >= 10001;
        let apSuper = f.aprobado_admin === true;
        let apAdmin = f.aprobado_admin_10k === true;
        let apCorp = f.aprobado_corp === true;

        let confirmadaTotal = false;
        if (isCara) {
            confirmadaTotal = (apSuper && apAdmin && apCorp);
        } else {
            confirmadaTotal = (apSuper && apCorp);
        }

        if (f.estado === 'Cancelado_Cotizacion_Cara') {
            estado = "Incosteable";
        } else if (f.estado === 'Archivado') {
            estado = "Finalizado / Histórico";
        } else if (f.is_unassigned) {
            if (!f.asignado_a) {
                estado = "Pendiente / Asig. Taller";
            } else {
                estado = "Pendiente de Cotización";
            }
        } else {
            // Está en facturas.json
            if (!tieneCotizacion || f.estado === 'Rechazado' || f.estado === 'Rechazada_Por_Cotizacion_Normal_U_Otra') {
                estado = "Pendiente de Cotización";
            } else {
                if (confirmadaTotal) {
                    if (!f.codigo_liberacion) {
                        estado = "En Reparación (Taller)";
                    } else if (f.entregado !== 'Sí') {
                        estado = "Validación / Pin (Chofer)";
                    } else {
                        if (!f.factura_pdf || f.validacion_fiscal === 'Rechazada') {
                            estado = "Esperando Facturación (Taller)";
                        } else if (f.validacion_fiscal !== 'Aprobada') {
                            estado = "Esperando Rev/Factura";
                        } else if (!f.numero_doc50) {
                            estado = "Esperando Num. Contable";
                        } else {
                            estado = "Finalizado / Histórico";
                        }
                    }
                } else {
                    if (isCara) {
                        if (!apSuper) {
                            estado = "Esperando / Aprob. Cotizacion (Supervisor)";
                        } else if (!apAdmin) {
                            estado = "Esperando / Aprob. Cotizacion (Admin)";
                        } else if (!apCorp) {
                            estado = "Esperando / Aprob. Cotizacion (Corp)";
                        } else {
                            estado = "En Reparación (Taller)";
                        }
                    } else {
                        estado = "Esperando / Aprob. Cotizacion (Supervisor)";
                    }
                }
            }
        }
        
        // Asignar el estado al objeto para el filtrado
        f.estado_calculado = estado;

        let compania = f.compania || pendienteHTML;
        let departamento = f.departamento || f.area || reporteOrig.departamento || pendienteHTML;
        let cope = f.cope || reporteOrig.cope || pendienteHTML;
        let ciudad = f.ciudad || reporteOrig.ciudad || pendienteHTML;

        let proveedor = f.proveedor || pendienteHTML;
        let nombreSup = f.supervisor_nombre || "No asignado";
        let nombreAdmin = f.administrador_nombre || "No asignado";
        let nombreJefatura = f.jefatura_nombre || "No asignado";
        let fechaEntrada = f.fecha || pendienteHTML;
        let fechaSalida = f.fecha_cierre || pendienteHTML;
        let tiempoTaller = pendienteHTML;
        // Calculate days in shop for Top 10
        f.dias_taller = 0;
        if (fechaEntrada !== pendienteHTML && fechaSalida !== pendienteHTML) {
            let f1 = new Date(f.fecha);
            let f2 = new Date(f.fecha_cierre);
            if (!isNaN(f1) && !isNaN(f2)) {
                let diffMs = Math.abs(f2 - f1);
                let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                f.dias_taller = diffDays;
                
                let diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                tiempoTaller = `${diffDays}d ${diffHours}h ${diffMinutes}m`;
            }
        }

        let isOperando = true;
        if (f.is_unassigned) {
            isOperando = !f.asignado_a;
        } else {
            isOperando = (f.entregado === 'Sí');
        }
        let statusUnidad = isOperando
            ? '<span style="background:#10b981; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Operando</span>'
            : '<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">No Operando</span>';
        let isLiberado = f.liberado_admin || f.estado === 'Archivado' || (f.numero_doc50 && f.numero_doc50 !== '');
        let statusDocContable = isLiberado
            ? '<span style="background:#10b981; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Liberado</span>'
            : '<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">No Liberado</span>';

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
            retroText = retroText.replace(/\[TICKET:.*?\]\s*REPORTE ORIGINAL DEL CHOFER:\s*/i, '').trim();
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
        let commentSafe = f.comentarios ? f.comentarios.replace(/'/g, "\\\'").replace(/"/g, "&quot;").replace(/\n/g, "\\n").replace(/\r/g, "") : "";
        let autorSafe = f.autor_comentario ? f.autor_comentario.replace(/'/g, "\\\'").replace(/"/g, "&quot;") : "";
        let btnText = hasComment ? "💬 Ver/Actualizar Comentario" : "💬 Añadir Comentario";
        let btnComentarios = `<button onclick="abrirModalComentarios('${f.id}', ${is_unass}, '${commentSafe}', '${autorSafe}')" style="background:${btnColor}; color:white; border:none; padding:5px 10px; border-radius:12px; font-size:0.85em; cursor:pointer;">${btnText}</button>`;

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
                <td style="vertical-align:top; padding-top:15px;">${tiempoTicket}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaTicketFinalizado}</td>
                <td style="vertical-align:top; padding-top:15px;"><span style="background:#0ea5e9; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">${estado}</span></td>
                <td style="vertical-align:top; padding-top:15px;">${statusUnidad}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreSup}</td>
                <td style="vertical-align:top; padding-top:15px;">${compania}</td>
                <td style="vertical-align:top; padding-top:15px;">${departamento}</td>
                <td style="vertical-align:top; padding-top:15px;">${cope}</td>
                <td style="vertical-align:top; padding-top:15px;">${ciudad}</td>
                <td style="vertical-align:top; padding-top:15px;"><div style="max-width:250px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${htmlRetro}</div></td>
                <td style="vertical-align:top; padding-top:15px;" data-costo="${ticketGasto}"><strong>${htmlCosto}</strong></td>
                <td style="vertical-align:top; padding-top:15px;">${proveedor}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaEntrada}</td>
                <td style="vertical-align:top; padding-top:15px;">${tiempoTaller}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaSalida}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumPedido}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumOrden}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlBtnPdfFactura}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreAdmin}</td>
                <td style="vertical-align:top; padding-top:15px;">${statusDocContable}</td>
                <td style="vertical-align:top; padding-top:15px;">${htmlNumContable}</td>
                <td style="vertical-align:top; padding-top:15px;">${btnComentarios}</td>
                <td style="vertical-align:top; padding-top:15px;">${nombreJefatura}</td>
            </tr>
        `;
        tbody.innerHTML += rowHtml;
    });

    actualizarKPIs(totalGasto, pendientesDoc50, pendientesOC);

    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
}

// ==========================================
// FILTROS Y KPIS
// ==========================================

function aplicarFiltrosReportes() {
    let texto = document.getElementById('filtro-texto-reportes').value.toLowerCase();
    let estado = document.getElementById('filtro-estado-reportes').value;
    let prov = document.getElementById('filtro-proveedor-reportes').value.toLowerCase();
    let ciudad = document.getElementById('filtro-ciudad-reportes').value.toLowerCase();

    let tbody = document.getElementById('tabla-seccion-reportes');
    let trs = tbody.getElementsByTagName('tr');
    
    let totalGasto = 0;
    
    for(let i=0; i<trs.length; i++) {
        let tr = trs[i];
        // Skip if it's the "No data" row
        if(tr.cells.length === 1) continue;
        
        let match = true;
        
        // Texto general (Ticket, Num Eco)
        if(texto) {
            let trText = tr.innerText.toLowerCase();
            if(!trText.includes(texto)) match = false;
        }
        
        // Estado
        if(estado) {
            let trEstado = tr.getAttribute('data-estado');
            if(estado === 'Pendiente de Cotizacion' && trEstado !== 'Pendiente de Cotización') match = false;
            else if(estado === 'Esperando Aprobacion' && trEstado !== 'Esperando Aprobación') match = false;
            else if(estado === 'Esperando Reparacion' && trEstado !== 'Esperando Reparación') match = false;
            else if(estado === 'Validacion y PIN' && trEstado !== 'Validación y PIN') match = false;
            else if(estado === 'Liberacion de Documentos' && trEstado !== 'Liberación Doc') match = false;
            else if(estado === 'Cierre Interno' && trEstado !== 'Cierre Interno') match = false;
            else if(estado === 'Finalizado' && trEstado !== 'Finalizado / Histórico') match = false;
        }
        
        // Proveedor
        if(prov) {
            let trProv = tr.getAttribute('data-prov');
            if(!trProv || !trProv.includes(prov)) match = false;
        }
        
        // Ciudad
        if(ciudad) {
            let trCiudad = tr.getAttribute('data-ciudad');
            if(!trCiudad || !trCiudad.includes(ciudad)) match = false;
        }
        
        tr.style.display = match ? '' : 'none';
        
        if(match) {
            let costoCell = tr.querySelector('td[data-costo]');
            if(costoCell) {
                totalGasto += parseFloat(costoCell.getAttribute('data-costo') || 0);
            }
        }
    }
    
    let elGasto = document.getElementById('kpi-total-gasto');
    if (elGasto) elGasto.innerText = '$' + totalGasto.toLocaleString('en-US', {minimumFractionDigits: 2});
}

function limpiarFiltrosReportes() {
    document.getElementById('filtro-texto-reportes').value = '';
    document.getElementById('filtro-estado-reportes').value = '';
    document.getElementById('filtro-proveedor-reportes').value = '';
    document.getElementById('filtro-ciudad-reportes').value = '';
    aplicarFiltrosReportes();
}

function actualizarKPIs(gasto, doc50, oc) {
    let elGasto = document.getElementById('kpi-total-gasto');
    if (elGasto) elGasto.innerText = '$' + gasto.toLocaleString('en-US', {minimumFractionDigits: 2});
    
    let elDoc50 = document.getElementById('kpi-pendientes-doc50');
    if (elDoc50) elDoc50.innerText = doc50;
    
    let elOc = document.getElementById('kpi-pendientes-oc');
    if (elOc) elOc.innerText = oc;
}

// ==========================================
// TOP 10 RANKING
// ==========================================

function mostrarTop10() {
    let top = [...reportesCombinadosGlobal].filter(x => x.dias_taller > 0).sort((a,b) => b.dias_taller - a.dias_taller).slice(0, 10);
    
    let ul = document.getElementById('lista-top10');
    ul.innerHTML = '';
    if(top.length === 0) {
        ul.innerHTML = '<li style="padding:15px; text-align:center; color:#94a3b8;">No hay unidades con tiempo registrado.</li>';
    } else {
        top.forEach((item, index) => {
            let numEco = item.unidad ? `8090-${item.unidad.replace('8090-', '')}` : 'S/T';
            let medalla = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '▪️';
            ul.innerHTML += `
                <li style="padding:10px 0; border-bottom:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
                    <span><span style="font-size:1.2em; margin-right:10px;">${medalla}</span> <strong>${numEco}</strong> - ${item.ciudad || 'Sin Ciudad'}</span>
                    <span style="background:#ef4444; color:white; padding:4px 8px; border-radius:12px; font-weight:bold;">${item.dias_taller} días</span>
                </li>
            `;
        });
    }
    
    document.getElementById('modal-top10').style.display = 'flex';
}


// ==========================================
// EXPORTACION / IMPRESION
// ==========================================

function toggleAllReportes(source) {
    let checkboxes = document.querySelectorAll('.chk-reporte');
    for(let i=0; i<checkboxes.length; i++) {
        let tr = checkboxes[i].closest('tr');
        if(tr.style.display !== 'none') {
            checkboxes[i].checked = source.checked;
        }
    }
}

function getSelectedRows() {
    let checkboxes = document.querySelectorAll('.chk-reporte:checked');
    let rows = [];
    checkboxes.forEach(chk => {
        let tr = chk.closest('tr');
        if(tr && tr.style.display !== 'none') {
            rows.push(tr);
        }
    });
    return rows;
}

function imprimirSeleccion() {
    let rows = getSelectedRows();
    if(rows.length === 0) {
        alert("Selecciona al menos un ticket para imprimir.");
        return;
    }
    if(!confirm("¿Estás seguro de que deseas generar un reporte PDF para imprimir con los " + rows.length + " registros seleccionados?")) {
        return;
    }
    if(rows.length === 0) {
        alert("Selecciona al menos un ticket para imprimir.");
        return;
    }
    
    // Crear una ventana de impresión
    let printWindow = window.open('', '_blank');
    let html = `
        <html>
        <head>
            <title>Impresión de Reportes</title>
            <style>
                @media print {
                    @page { size: landscape; margin: 10mm; }
                }
                body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                h1 { text-align: center; color: #1e3a8a; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 11px; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
                th { background-color: #f1f5f9; font-weight: bold; }
                .estado { font-weight: bold; }
                /* Asegurar que los saltos de línea de las opciones se vean bien */
                td { white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h1>Reporte de Mantenimiento Vehicular</h1>
            <p>Fecha de impresión: ${new Date().toLocaleDateString()}</p>
            <table>
                <thead>
                    <tr>
                        <th>TICKET</th>
                        <th>NUM. ECO</th>
                        <th>FECHA</th>
                        <th>ESTADO</th>
                        <th>CIUDAD</th>
                        <th>COSTO</th>
                        <th>PROVEEDOR</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    rows.forEach(tr => {
        // Extraemos el texto de las celdas relevantes
        // td[1]=Ticket, td[2]=Eco, td[3]=Fecha, td[4]=Estado, td[10]=Ciudad, td[12]=Costo, td[13]=Proveedor
        let c = tr.cells;
        html += `
            <tr>
                <td>${c[1].innerText}</td>
                <td>${c[2].innerText}</td>
                <td>${c[3].innerText}</td>
                <td class="estado">${c[4].innerText}</td>
                <td>${c[10].innerText}</td>
                <td>${c[12].innerText}</td>
                <td>${c[13].innerText}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
            <br>
            <p style="text-align:right;"><strong>Total Tickets Seleccionados:</strong> ${rows.length}</p>
        </body>
        </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.focus();
    // setTimeout to allow rendering before printing
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

function exportarExcel() {
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

    let csvContent = "\uFEFF"; // BOM for UTF-8 in Excel
    
    // Headers (skip checkbox)
    let ths = trs[0].querySelectorAll('th');
    let headerRow = [];
    for(let i=1; i<ths.length; i++) {
        headerRow.push(`"${ths[i].innerText.replace(/"/g, '""')}"`);
    }
    csvContent += headerRow.join(",") + "\r\n";
    
    // Data (targetRows was already defined above)
    
    targetRows.forEach(tr => {
        let rowData = [];
        let tds = tr.querySelectorAll('td');
        for(let i=1; i<tds.length; i++) {
            let text = tds[i].innerText.replace(/"/g, '""');
            // Remove newlines
            text = text.replace(/\r?\n|\r/g, ' | ');
            rowData.push(`"${text}"`);
        }
        csvContent += rowData.join(",") + "\r\n";
    });
    
    let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
    if (link.download !== undefined) {
        let url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", "reporte_mantenimiento.csv");
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// ==========================================
// FUNCIONES PARA MODAL DE COMENTARIOS
// ==========================================

function abrirModalComentarios(id, is_unassigned, comentarioActual, autorActual) {
    document.getElementById('comentario-ticket-id').value = id;
    document.getElementById('comentario-is-unassigned').value = is_unassigned;

    let decoded = comentarioActual.replace(/&quot;/g, '"');
    document.getElementById('comentario-texto').value = decoded;

    let autorDiv = document.getElementById('comentario-autor');
    if (autorActual && autorActual.trim() !== '') {
        autorDiv.innerText = "Última actualización por: " + autorActual.replace(/&quot;/g, '"');
    } else {
        autorDiv.innerText = "";
    }

    document.getElementById('modal-comentarios').style.display = 'flex';
}

async function guardarComentario(action = "save") {
    if (action === "save") {
        if (!confirm('¿Estás seguro de guardar los cambios en este comentario?')) return;
    }

    const id = document.getElementById('comentario-ticket-id').value;
    const is_unassigned = document.getElementById('comentario-is-unassigned').value === 'true';
    const comentario = document.getElementById('comentario-texto').value.trim();

    try {
        const res = await fetch('/api/seccion_reportes/comentario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, is_unassigned, comentario, action })
        });
        const data = await res.json();

        if (data.status === 'success') {
            let finalComment = data.comentario_final || "";
            let finalAuthor = data.autor_comentario || "";
            let finalDeletedBy = data.eliminado_por || "";
            if (is_unassigned && window.reportesGlobal) {
                let r = window.reportesGlobal.find(x => String(x.id) === String(id));
                if (r) {
                    r.comentarios = finalComment;
                    r.autor_comentario = finalAuthor;
                    r.eliminado_por = finalDeletedBy;
                }
            }
            if (action === "delete") {
                document.getElementById('comentario-texto').value = "";
            }
            document.getElementById('modal-comentarios').style.display = 'none';
            cargarSeccionReportes(); // Refrescar tabla
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al guardar el comentario.');
    }
}

async function eliminarComentario() {
    if (!confirm('¿Estás seguro de eliminar este comentario?')) return;
    await guardarComentario("delete");
}
