// static/seccion_reportes.js

document.addEventListener('DOMContentLoaded', () => {
    // Inicialización si es necesaria
});

const ESTADOS_OFICIALES_SISTEMA = [
    "Pendiente / Asig. Taller",
    "Pendiente de Cotización",
    "Correcciones/Taller",
    "Esperando / Aprob. Cotizacion (Supervisor)",
    "Esperando / Aprob. Cotizacion (Admin)",
    "Esperando / Aprob. Cotizacion (Corp)",
    "En Reparación (Taller)",
    "Validación / Pin (Chofer)",
    "Esperando Facturación (Taller)",
    "Esperando Rev/Factura",
    "Esperando Num. Contable",
    "Finalizado / Histórico",
    "Incosteable"
];

function normalizarCadenaReportes(str) {
    if (!str) return '';
    return str.toString()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .trim()
        .toLowerCase();
}

function poblarFiltroEstadosReportes(estadosServidor, listaTickets) {
    const selectEstado = document.getElementById('filtro-estado-reportes');
    if (!selectEstado) return;

    let valorActual = selectEstado.value;
    let conjuntoEstados = new Set(ESTADOS_OFICIALES_SISTEMA);

    if (Array.isArray(estadosServidor)) {
        estadosServidor.forEach(e => {
            if (e && typeof e === 'string') conjuntoEstados.add(e.trim());
        });
    }

    if (Array.isArray(listaTickets)) {
        listaTickets.forEach(t => {
            let st = t.estado_calculado || t.estado;
            if (st && typeof st === 'string' && st !== 'Eliminado' && st !== 'Rechazado') {
                conjuntoEstados.add(st.trim());
            }
        });
    }

    selectEstado.innerHTML = '<option value="">Todos los Estados</option>';
    Array.from(conjuntoEstados).sort().forEach(estado => {
        let opt = document.createElement('option');
        opt.value = estado;
        opt.textContent = estado;
        if (estado === valorActual) opt.selected = true;
        selectEstado.appendChild(opt);
    });
}

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

        // Filtrar tickets eliminados y evitar duplicados
        let idsProcesados = new Set();
        listaCombinada = listaCombinada.filter(t => {
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

        // Poblar las opciones del selector de estados asegurando todos los estados del sistema y de la BD
        poblarFiltroEstadosReportes(data.estados_disponibles, reportesCombinadosGlobal);

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
        let fechaTicketBase = reporteOrig.fecha || f.fecha || pendienteHTML;
        let fechaTicket = fechaTicketBase;
        let fechaISO = '';
        
        // Agregar hora si es posible y extraer fecha ISO (YYYY-MM-DD)
        if (fechaTicket !== pendienteHTML) {
            let ts = reporteOrig.timestamp || f.timestamp;
            if (ts) {
                let dt = new Date(ts);
                if (!isNaN(dt)) {
                    let yyyy = dt.getFullYear();
                    let mm = String(dt.getMonth() + 1).padStart(2, '0');
                    let dd = String(dt.getDate()).padStart(2, '0');
                    let hh = String(dt.getHours()).padStart(2, '0');
                    let min = String(dt.getMinutes()).padStart(2, '0');
                    fechaTicket = `${yyyy}-${mm}-${dd} ${hh}:${min}`;
                    fechaISO = `${yyyy}-${mm}-${dd}`;
                }
            }
            if (!fechaISO && typeof fechaTicketBase === 'string' && fechaTicketBase.length >= 10) {
                fechaISO = fechaTicketBase.substring(0, 10);
            }
        }

        // CALCULO DE TIEMPO DEL TICKET
        // Inicio: fecha del reporte. Fin: fecha_cierre si existe, si no => ahora
        let tiempoTicket = pendienteHTML;
        let tsBase = reporteOrig.timestamp || f.timestamp;
        if (tsBase || fechaTicketBase !== pendienteHTML) {
            let ft1 = tsBase ? new Date(tsBase) : new Date(fechaTicketBase + "T00:00:00");
            let ft2 = f.fecha_cierre ? new Date(f.fecha_cierre) : new Date();
            if (!isNaN(ft1) && !isNaN(ft2) && ft2 >= ft1) {
                let diffMsT = ft2 - ft1;
                let diffDaysT = Math.floor(diffMsT / (1000 * 60 * 60 * 24));
                let diffHoursT = Math.floor((diffMsT % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let diffMinutesT = Math.floor((diffMsT % (1000 * 60 * 60)) / (1000 * 60));
                let sufijo = f.fecha_cierre ? '' : ' ⏱️';
                tiempoTicket = `${diffDaysT}d ${diffHoursT}h ${diffMinutesT}m${sufijo}`;
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
        } else if (f.estado === 'Rechazado_Con_Recomendaciones') {
            estado = "Correcciones/Taller";
        } else if (f.estado === 'Archivado' || f.estado === 'Archivado_Final') {
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
        let fechaEntrada = pendienteHTML;
        if (!f.is_unassigned) {
            if (f.timestamp_aprobacion) {
                let dt = new Date(f.timestamp_aprobacion);
                if (!isNaN(dt)) {
                    let yyyy = dt.getFullYear();
                    let mm = String(dt.getMonth() + 1).padStart(2, '0');
                    let dd = String(dt.getDate()).padStart(2, '0');
                    let hh = String(dt.getHours()).padStart(2, '0');
                    let min = String(dt.getMinutes()).padStart(2, '0');
                    fechaEntrada = `${yyyy}-${mm}-${dd} ${hh}:${min}`;
                } else {
                    fechaEntrada = f.timestamp_aprobacion;
                }
            } else {
                fechaEntrada = `<span style="color:#f59e0b; font-size: 0.9em; font-weight:bold;">Esperando Aprobación</span>`;
            }
        }

        let fechaSalida = f.fecha_cierre || pendienteHTML;
        let tiempoTaller = pendienteHTML;
        // CALCULO DE TIEMPO EN TALLER
        // Inicio: timestamp_aprobacion (cuando el supervisor aprobó la cotización). Fin: fecha_cierre si existe, si no => ahora
        f.dias_taller = 0;
        if (!f.is_unassigned && (f.aprobado_admin || f.aprobado_corp)) {
            let fechaInicioTaller = f.timestamp_aprobacion || f.timestamp || f.fecha; 
            if (fechaInicioTaller) {
                let f1 = new Date(fechaInicioTaller);
                if (isNaN(f1)) f1 = new Date(fechaInicioTaller + "T00:00:00");
                let f2 = f.fecha_cierre ? new Date(f.fecha_cierre) : new Date();
                if (!isNaN(f1) && !isNaN(f2) && f2 >= f1) {
                    let diffMs = f2 - f1;
                    let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    f.dias_taller = diffDays;
                    let diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    let sufijo = f.fecha_cierre ? '' : ' ⏱️';
                    tiempoTaller = `${diffDays}d ${diffHours}h ${diffMinutes}m${sufijo}`;
                }
            }
        } else if (!f.is_unassigned) {
            tiempoTaller = `<span style="color:#f59e0b; font-size: 0.9em;">Esperando Aprobación</span>`;
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
        
        let valRetrabajo = f.retrabajo || f.es_retrabajo || '-';
        let valNumRetrabajo = f.num_retrabajo || f.numero_retrabajo || '-';
        
        let numCotizaciones = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones.length : 1;
        let costoTotalRow = 0;
        let isRowPendOC = false;
        let isRowPendDoc50 = false;

        for (let idx = 0; idx < numCotizaciones; idx++) {
            let cot = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones[idx] : null;
            let bStyle = (idx < numCotizaciones - 1) ? 'border-bottom:1px solid #334155; margin-bottom:8px; padding-bottom:8px;' : '';
            let label = numCotizaciones > 1 ? `<strong style="color:#a3b1c6; font-size:0.8em; display:block;">Opción ${idx+1}:</strong>` : '';

            // Retro
            let retroRaw = cot ? (cot.retro || pendienteHTML) : (f.retro || pendienteHTML);
            let tempDiv = document.createElement('div'); tempDiv.innerHTML = retroRaw; let retroText = tempDiv.textContent || tempDiv.innerText || pendienteHTML;
            retroText = retroText.replace(/\[TICKET:.*?\]\s*(REPORTE ORIGINAL DEL CHOFER:\s*)?/i, '').trim();
            if (retroText === 'Pendiente' || retroText === '') retroText = pendienteHTML;
            htmlRetro += `<div style="${bStyle}">${label}${retroText}</div>`;

            // Costo
            let costoNum = cot ? parseFloat(cot.precio || 0) : (f.precio ? parseFloat(f.precio) : 0);
            let costoStr = costoNum > 0 ? costoNum.toLocaleString('en-US') : '0.00';
            htmlCosto += `<div style="${bStyle}">${label}$${costoStr}</div>`;
            costoTotalRow += costoNum;
            
            // Num Pedido
            let nPedido = cot ? (cot.numero_cotizacion_asignacion || pendienteHTML) : (f.numero_cotizacion_asignacion || pendienteHTML);
            htmlNumPedido += `<div style="${bStyle}">${label}${nPedido}</div>`;
            if(nPedido === pendienteHTML) isRowPendOC = true;

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
            if(nContable === pendienteHTML) isRowPendDoc50 = true;
        }

        if (isRowPendOC) pendientesOC++;
        if (isRowPendDoc50) pendientesDoc50++;

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
        let cleanCope = cope === pendienteHTML ? 'pendiente' : cope.toLowerCase().replace(/<[^>]*>?/gm, '');
        let cleanEco = numEco === pendienteHTML ? 'pendiente' : numEco.replace(/<[^>]*>?/gm, '');

        // Set row info for filtering
        let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
        let rowHtml = `
            <tr data-ticket="${ticket}" data-eco="${cleanEco}" data-prov="${cleanProv}" data-ciudad="${cleanCiudad}" data-cope="${cleanCope}" data-estado="${estado}" data-fecha="${fechaISO}" data-costo="${ticketGasto}" data-pend-doc50="${isRowPendDoc50 ? '1' : '0'}" data-pend-oc="${isRowPendOC ? '1' : '0'}" data-reactivado="${f.reactivado_desde_caras ? '1' : '0'}">
                <td style="vertical-align:top; padding-top:15px;"><input type="checkbox" class="chk-reporte" value="${ticket}"></td>
                <td style="vertical-align:top; padding-top:15px;"><span style="color:#0ea5e9; font-weight:bold;">${ticket}</span>${badgeCaras}</td>
                <td style="vertical-align:top; padding-top:15px;">${numEco}</td>
                <td style="vertical-align:top; padding-top:15px;">${fechaTicket}</td>
                <td style="vertical-align:top; padding-top:15px;">${tiempoTicket}</td>
                <td style="vertical-align:top; padding-top:15px;">${f.fecha_cierre || pendienteHTML}</td>
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
                <td style="vertical-align:top; padding-top:15px;">${valRetrabajo}</td>
                <td style="vertical-align:top; padding-top:15px;">${valNumRetrabajo}</td>
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
    let elTexto = document.getElementById('filtro-texto-reportes');
    let elEstado = document.getElementById('filtro-estado-reportes');
    let elProv = document.getElementById('filtro-proveedor-reportes');
    let elCiudad = document.getElementById('filtro-ciudad-reportes');
    let elFecha = document.getElementById('filtro-fecha-reportes');

    let texto = elTexto ? normalizarCadenaReportes(elTexto.value) : '';
    let estado = elEstado ? elEstado.value.trim() : '';
    let estadoNorm = normalizarCadenaReportes(estado);
    let prov = elProv ? normalizarCadenaReportes(elProv.value) : '';
    let ciudad = elCiudad ? normalizarCadenaReportes(elCiudad.value) : '';
    let fecha = elFecha ? elFecha.value.trim() : '';

    let tbody = document.getElementById('tabla-seccion-reportes');
    if (!tbody) return;
    let trs = tbody.getElementsByTagName('tr');
    
    let totalGasto = 0;
    let pendientesDoc50 = 0;
    let pendientesOC = 0;
    let filasVisibles = 0;
    
    for(let i=0; i<trs.length; i++) {
        let tr = trs[i];
        // Omitir fila de mensaje o sin datos
        if (tr.id === 'fila-sin-resultados-reportes') continue;
        if (tr.cells.length <= 1) continue;
        
        let match = true;
        
        // 1. Filtro Texto General (Ticket, Eco, o contenido textual)
        if (texto) {
            let trText = normalizarCadenaReportes(tr.innerText);
            let trTicket = normalizarCadenaReportes(tr.getAttribute('data-ticket') || '');
            let trEco = normalizarCadenaReportes(tr.getAttribute('data-eco') || '');
            if (!trText.includes(texto) && !trTicket.includes(texto) && !trEco.includes(texto)) {
                match = false;
            }
        }
        
        // 2. Filtro Estado (exacto o normalizado con el valor del estado)
        if (match && estado) {
            let trEstado = (tr.getAttribute('data-estado') || '').trim();
            let trEstadoNorm = normalizarCadenaReportes(trEstado);
            if (trEstadoNorm !== estadoNorm) {
                match = false;
            }
        }
        
        // 3. Filtro Proveedor
        if (match && prov) {
            let trProv = normalizarCadenaReportes(tr.getAttribute('data-prov') || '');
            let cellProv = normalizarCadenaReportes(tr.cells[15] ? tr.cells[15].innerText : '');
            if (!trProv.includes(prov) && !cellProv.includes(prov)) {
                match = false;
            }
        }
        
        // 4. Filtro Ciudad Base / COPE
        if (match && ciudad) {
            let trCiudad = normalizarCadenaReportes(tr.getAttribute('data-ciudad') || '');
            let trCope = normalizarCadenaReportes(tr.getAttribute('data-cope') || '');
            let cellCiudad = normalizarCadenaReportes(tr.cells[12] ? tr.cells[12].innerText : '');
            let cellCope = normalizarCadenaReportes(tr.cells[11] ? tr.cells[11].innerText : '');
            if (!trCiudad.includes(ciudad) && !trCope.includes(ciudad) && !cellCiudad.includes(ciudad) && !cellCope.includes(ciudad)) {
                match = false;
            }
        }

        // 5. Filtro Fecha (ej. Estado + Fecha)
        if (match && fecha) {
            let trFecha = (tr.getAttribute('data-fecha') || '').trim();
            let cellFecha = (tr.cells[3] ? tr.cells[3].innerText : '').trim();
            if (!trFecha.startsWith(fecha) && !trFecha.includes(fecha) && !cellFecha.startsWith(fecha) && !cellFecha.includes(fecha)) {
                match = false;
            }
        }

        // 6. Filtro Reactivadas de Cotizaciones Caras (botón toggle)
        if (match && window.filtroReactivadasCarasActivo) {
            let esReactivado = tr.getAttribute('data-reactivado') === '1';
            if (!esReactivado) {
                match = false;
            }
        }
        
        // Aplicar estado de visibilidad y clase de filtro para paginación
        if (match) {
            tr.classList.remove('oculto-por-filtro');
            tr.style.display = '';
            
            // Recalcular métricas y KPIs solo sobre registros coincidentes
            let costo = parseFloat(tr.getAttribute('data-costo') || 0);
            if (!isNaN(costo)) totalGasto += costo;
            
            if (tr.getAttribute('data-pend-doc50') === '1') pendientesDoc50++;
            if (tr.getAttribute('data-pend-oc') === '1') pendientesOC++;
            
            filasVisibles++;
        } else {
            tr.classList.add('oculto-por-filtro');
            tr.style.display = 'none';
        }
    }
    
    // Actualizar todos los indicadores KPI con los datos filtrados
    actualizarKPIs(totalGasto, pendientesDoc50, pendientesOC);

    // Mensaje visual si no hay resultados coincidentes
    let filaSinResultados = document.getElementById('fila-sin-resultados-reportes');
    if (filasVisibles === 0) {
        if (!filaSinResultados) {
            filaSinResultados = document.createElement('tr');
            filaSinResultados.id = 'fila-sin-resultados-reportes';
            filaSinResultados.innerHTML = `<td colspan="30" style="text-align: center; color: #a3b1c6; padding: 25px; font-weight: bold; background: #0f172a;">🔍 No se encontraron tickets con los filtros seleccionados.</td>`;
            tbody.appendChild(filaSinResultados);
        } else {
            filaSinResultados.style.display = '';
        }
    } else if (filaSinResultados) {
        filaSinResultados.style.display = 'none';
    }

    // Reajustar la paginación según las filas que quedaron visibles
    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
}

window.filtroReactivadasCarasActivo = false;

function toggleFiltroReactivadas() {
    window.filtroReactivadasCarasActivo = !window.filtroReactivadasCarasActivo;
    let btn = document.getElementById('btn-filtro-reactivadas');
    if (btn) {
        if (window.filtroReactivadasCarasActivo) {
            btn.style.background = '#f59e0b';
            btn.style.color = '#0f172a';
            btn.style.borderColor = '#d97706';
            btn.style.boxShadow = '0 0 10px rgba(245, 158, 11, 0.4)';
            btn.innerHTML = '<span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras';
        } else {
            btn.style.background = '#334155';
            btn.style.color = '#cbd5e1';
            btn.style.borderColor = '#475569';
            btn.style.boxShadow = 'none';
            btn.innerHTML = '<span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras';
        }
    }
    aplicarFiltrosReportes();
}

function limpiarFiltrosReportes() {
    let elTexto = document.getElementById('filtro-texto-reportes');
    let elEstado = document.getElementById('filtro-estado-reportes');
    let elProv = document.getElementById('filtro-proveedor-reportes');
    let elCiudad = document.getElementById('filtro-ciudad-reportes');
    let elFecha = document.getElementById('filtro-fecha-reportes');

    if (elTexto) elTexto.value = '';
    if (elEstado) elEstado.value = '';
    if (elProv) elProv.value = '';
    if (elCiudad) elCiudad.value = '';
    if (elFecha) elFecha.value = '';

    window.filtroReactivadasCarasActivo = false;
    let btn = document.getElementById('btn-filtro-reactivadas');
    if (btn) {
        btn.style.background = '#334155';
        btn.style.color = '#cbd5e1';
        btn.style.borderColor = '#475569';
        btn.style.boxShadow = 'none';
        btn.innerHTML = '<span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras';
    }

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
        // td[1]=Ticket, td[2]=Eco, td[3]=Fecha, td[6]=Estado, td[12]=Ciudad, td[14]=Costo, td[15]=Proveedor
        let c = tr.cells;
        html += `
            <tr>
                <td>${c[1] ? c[1].innerText : ''}</td>
                <td>${c[2] ? c[2].innerText : ''}</td>
                <td>${c[3] ? c[3].innerText : ''}</td>
                <td class="estado">${c[6] ? c[6].innerText : ''}</td>
                <td>${c[12] ? c[12].innerText : ''}</td>
                <td>${c[14] ? c[14].innerText : ''}</td>
                <td>${c[15] ? c[15].innerText : ''}</td>
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
