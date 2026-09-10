// static/seccion_reportes.js

document.addEventListener('DOMContentLoaded', () => {
    // Escuchar cuando el usuario cambia a la vista de "seccion-reportes"
    // Esto dependerá de cómo se maneje el cambio de vista en el dashboard principal.
    // Una forma es inyectar la carga en la función cambiarVistaAdmin si existe globalmente,
    // o simplemente cargar los datos cuando se muestra la tabla.
});

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
        const tbody = document.getElementById('tabla-seccion-reportes');
        if (!tbody) return;

        tbody.innerHTML = '';

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

        if (listaCombinada.length === 0) {
            tbody.innerHTML = `<tr><td colspan="16" style="text-align: center; color: #a3b1c6; padding: 20px;">No hay información disponible por el momento.</td></tr>`;
            return;
        }

        // Ordenamos del más reciente al más antiguo
        listaCombinada.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        listaCombinada.forEach(f => {
            let ticketIdFunc = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : null;
            let ticket = ticketIdFunc || f.id_reporte || f.id || 'S/T';

            // Buscar el reporte original
            let reporteOrig = (window.reportesGlobal || []).find(r => String(r.id) === ticket) || {};

            let pendienteHTML = '<span style="background:#ef4444; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Pendiente</span>';

            let numEco = f.unidad ? `8090-${f.unidad.replace('8090-', '')}` : pendienteHTML;
            let fechaTicket = f.fecha || reporteOrig.fecha || pendienteHTML;
            let estado = 'N/A'; // Temporalmente N/A hasta que se programe
            let compania = f.compania || pendienteHTML;

            let departamento = f.departamento || f.area || reporteOrig.departamento || pendienteHTML;
            let cope = f.cope || reporteOrig.cope || pendienteHTML;
            let ciudad = f.ciudad || reporteOrig.ciudad || pendienteHTML;

            // Texto nada más para Retro (Problema)
            let retro = f.retro || (f.cotizaciones && f.cotizaciones.length > 0 ? (f.cotizaciones[0].retro || pendienteHTML) : pendienteHTML);
            // Removemos HTML u otros tags si existieran, asegurando solo texto básico:
            let tempDiv = document.createElement('div'); tempDiv.innerHTML = retro; retro = tempDiv.textContent || tempDiv.innerText || pendienteHTML;
            // Remover el bloque de texto "[TICKET:REP-1234] REPORTE ORIGINAL DEL CHOFER: "
            retro = retro.replace(/\[TICKET:.*?\]\s*REPORTE ORIGINAL DEL CHOFER:\s*/i, '').trim();
            if (retro === 'Pendiente' || retro === '') retro = pendienteHTML;

            let costo = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0.00';
            let proveedor = f.proveedor || pendienteHTML;

            let numPedido = f.numero_cotizacion_asignacion || pendienteHTML;
            let btnPdfPedido = f.pdf_cotizacion_asignacion ?
                `<button class="btn-info" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_cotizacion_asignacion}')">📄 Ver PDF</button>` :
                pendienteHTML;

            let numOrden = f.numero_orden || pendienteHTML;

            let numFactura = f.factura_folio || pendienteHTML;
            let btnPdfFactura = (f.pdf_fiscal || f.factura_pdf) ?
                `<button class="btn-success-modal" style="padding:4px 8px; font-size:0.8em; margin:0;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_fiscal || f.factura_pdf}')">📄 Ver PDF</button>` :
                pendienteHTML;

            let numContable = f.numero_doc50 || pendienteHTML;
            // Prepare comments button
            let hasComment = f.comentarios && f.comentarios.trim() !== "";
            let btnColor = hasComment ? "#0284c7" : "#475569";
            let realId = f.is_unassigned ? f.id_reporte : f.id;
            let is_unass = f.is_unassigned ? "true" : "false";

            // Fix encoding for passing string to JS
            let commentSafe = f.comentarios ? f.comentarios.replace(/'/g, "\\'").replace(/"/g, "&quot;").replace(/\n/g, "\\n").replace(/\r/g, "") : "";
            let autorSafe = f.autor_comentario ? f.autor_comentario.replace(/'/g, "\\'").replace(/"/g, "&quot;") : "";
            
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
            if (fechaEntrada !== pendienteHTML && fechaSalida !== pendienteHTML) {
                let f1 = new Date(f.fecha);
                let f2 = new Date(f.fecha_cierre);
                if (!isNaN(f1) && !isNaN(f2)) {
                    let diffDays = Math.ceil(Math.abs(f2 - f1) / (1000 * 60 * 60 * 24));
                    tiempoTaller = diffDays + ' día(s)';
                }
            }

            let isOperando = f.is_unassigned ? true : (f.entregado === 'Sí');
            let statusUnidad = isOperando
                ? '<span style="background:#10b981; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">Operando</span>'
                : '<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-size:0.85em; font-weight:bold; white-space:nowrap;">No Operando</span>';

            tbody.innerHTML += `
                <tr>
                    <td><strong>${ticket}</strong></td>
                    <td>${numEco}</td>
                    <td>${fechaTicket}</td>
                    <td><span style="color:#a3b1c6; font-style:italic;">${estado}</span></td>
                    <td>${statusUnidad}</td>
                    <td>${compania}</td>
                    <td>${departamento}</td>
                    <td>${cope}</td>
                    <td>${ciudad}</td>
                    <td><div style="max-width:200px; white-space:normal; font-size:0.9em; word-wrap: break-word;">${retro}</div></td>
                    <td><strong>$${costo}</strong></td>
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
        });

    } catch (err) {
        console.error("Error cargando la sección de reportes:", err);
    }
}

// ==========================================
// FUNCIONES PARA MODAL DE COMENTARIOS
// ==========================================

function abrirModalComentarios(id, is_unassigned, comentarioActual, autorActual) {
    document.getElementById('comentario-ticket-id').value = id;
    document.getElementById('comentario-is-unassigned').value = is_unassigned;
    
    // Replace html entities back for textarea
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
