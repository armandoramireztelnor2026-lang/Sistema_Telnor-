import json

js_content = """// static/seccion_reportes.js

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

        reportes.forEach(r => {
            if (!asignadosIds.has(String(r.id))) {
                listaCombinada.push({
                    is_unassigned: true,
                    id_reporte: r.id,
                    fecha: r.fecha,
                    unidad: r.unidad,
                    compania: r.compania || 'TELNOR',
                    departamento: r.departamento,
                    cope: r.cope,
                    ciudad: r.ciudad,
                    retro: r.falla,
                    timestamp: r.timestamp,
                    estado_custom: 'Bandeja de Reportes',
                    comentarios: r.comentarios,
                    autor_comentario: r.autor_comentario,
                    eliminado_por: r.eliminado_por
                });
            }
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

        let retro = f.retro || (f.cotizaciones && f.cotizaciones.length > 0 ? (f.cotizaciones[0].retro || pendienteHTML) : pendienteHTML);
        let tempDiv = document.createElement('div'); tempDiv.innerHTML = retro; retro = tempDiv.textContent || tempDiv.innerText || pendienteHTML;
        retro = retro.replace(/\[TICKET:.*?\]\s*REPORTE ORIGINAL DEL CHOFER:\s*/i, '').trim();
        if (retro === 'Pendiente' || retro === '') retro = pendienteHTML;

        let costoNum = f.precio ? parseFloat(f.precio) : 0;
        totalGasto += costoNum;
        let costo = costoNum > 0 ? costoNum.toLocaleString('en-US') : '0.00';
        
        let proveedor = f.proveedor || pendienteHTML;

        let numPedido = f.numero_cotizacion_asignacion || pendienteHTML;
        let btnPdfPedido = f.pdf_cotizacion_asignacion ?
            `<button class="btn-info" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_cotizacion_asignacion}')">📄 Ver PDF</button>` :
            pendienteHTML;
            
        if (!f.numero_cotizacion_asignacion) pendientesOC++;

        let numOrden = f.numero_orden || pendienteHTML;

        let numFactura = f.factura_folio || pendienteHTML;
        let btnPdfFactura = (f.pdf_fiscal || f.factura_pdf) ?
            `<button class="btn-success-modal" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_fiscal || f.factura_pdf}')">📄 Ver PDF</button>` :
            pendienteHTML;

        let numContable = f.numero_doc50 || pendienteHTML;
        if (!f.numero_doc50) pendientesDoc50++;
        
        let hasComment = f.comentarios && f.comentarios.trim() !== "";
        let btnColor = hasComment ? "#0284c7" : "#475569";
        let realId = f.is_unassigned ? f.id_reporte : f.id;
        let is_unass = f.is_unassigned ? "true" : "false";

        let commentSafe = f.comentarios ? f.comentarios.replace(/'/g, "\\\\'").replace(/"/g, "&quot;").replace(/\\n/g, "\\\\n").replace(/\\r/g, "") : "";
        let autorSafe = f.autor_comentario ? f.autor_comentario.replace(/'/g, "\\\\'").replace(/"/g, "&quot;") : "";

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

        // Set row info for filtering
        let rowHtml = `
            <tr data-ticket="${ticket}" data-eco="${numEco}" data-prov="${proveedor.toLowerCase()}" data-ciudad="${ciudad.toLowerCase()}" data-estado="${estado}">
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
    });

    actualizarKPIs(totalGasto, pendientesDoc50, pendientesOC);
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
    
    document.getElementById('kpi-total-gasto').innerText = '$' + totalGasto.toLocaleString('en-US', {minimumFractionDigits: 2});
}

function limpiarFiltrosReportes() {
    document.getElementById('filtro-texto-reportes').value = '';
    document.getElementById('filtro-estado-reportes').value = '';
    document.getElementById('filtro-proveedor-reportes').value = '';
    document.getElementById('filtro-ciudad-reportes').value = '';
    aplicarFiltrosReportes();
}

function actualizarKPIs(gasto, doc50, oc) {
    document.getElementById('kpi-total-gasto').innerText = '$' + gasto.toLocaleString('en-US', {minimumFractionDigits: 2});
    document.getElementById('kpi-pendientes-doc50').innerText = doc50;
    document.getElementById('kpi-pendientes-oc').innerText = oc;
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
    
    // Crear una ventana de impresión
    let printWindow = window.open('', '_blank');
    let html = `
        <html>
        <head>
            <title>Impresión de Reportes</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                h1 { text-align: center; color: #1e3a8a; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background-color: #f1f5f9; font-weight: bold; }
                .estado { font-weight: bold; }
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
        // td[1]=Ticket, td[2]=Eco, td[3]=Fecha, td[4]=Estado, td[9]=Ciudad, td[11]=Costo, td[12]=Proveedor
        let c = tr.cells;
        html += `
            <tr>
                <td>${c[1].innerText}</td>
                <td>${c[2].innerText}</td>
                <td>${c[3].innerText}</td>
                <td class="estado">${c[4].innerText}</td>
                <td>${c[9].innerText}</td>
                <td>${c[11].innerText}</td>
                <td>${c[12].innerText}</td>
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
    
    let csvContent = "\\uFEFF"; // BOM for UTF-8 in Excel
    
    // Headers (skip checkbox)
    let ths = trs[0].querySelectorAll('th');
    let headerRow = [];
    for(let i=1; i<ths.length; i++) {
        headerRow.push(`"${ths[i].innerText.replace(/"/g, '""')}"`);
    }
    csvContent += headerRow.join(",") + "\\r\\n";
    
    // Data
    let targetRows = rows.length > 0 ? rows : Array.from(trs).slice(1).filter(tr => tr.style.display !== 'none' && tr.cells.length > 1);
    
    if(targetRows.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }
    
    targetRows.forEach(tr => {
        let rowData = [];
        let tds = tr.querySelectorAll('td');
        for(let i=1; i<tds.length; i++) {
            let text = tds[i].innerText.replace(/"/g, '""');
            // Remove newlines
            text = text.replace(/\\r?\\n|\\r/g, ' ');
            rowData.push(`"${text}"`);
        }
        csvContent += rowData.join(",") + "\\r\\n";
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
"""

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\seccion_reportes.js", "w", encoding="utf-8") as f:
    f.write(js_content)
