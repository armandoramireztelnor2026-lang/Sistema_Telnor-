// =========================================================
// ARCHIVO: static/facturas_principal.js
// PROPÓSITO: Lógica principal, conexiones al servidor (Fetch) y vistas
// =========================================================

let listaProveedoresParaAsignar = [];
let facturasGlobal = [];
let reportesGlobal = [];
let reporteSeleccionado = null;

document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById('tabla-facturas')) cargarFacturas();
});

document.addEventListener('click', function (e) {
    const buscador = document.getElementById('buscador-proveedor');
    const lista = document.getElementById('lista-proveedores-flotante');
    if (buscador && lista) {
        if (!buscador.contains(e.target) && !lista.contains(e.target)) {
            lista.style.display = 'none';
        }
    }
});

function obtenerIdReporte(f) {
    if (!f) return null;
    if (f.numero_reporte && f.numero_reporte !== "") return String(f.numero_reporte);
    if (f.retro && f.retro.includes('[TICKET:')) {
        let match = f.retro.match(/\[TICKET:(.*?)\]/);
        if (match && match[1]) return String(match[1]);
    }
    return null;
}
function limpiarRetro(retro) {
    if (!retro) return "";
    return retro.replace(/\[TICKET:.*?\]\n?/, '').trim();
}

async function cargarFacturas() {
    try {
        const resFac = await fetch('/api/facturas/lista');
        const dataFac = await resFac.json();
        facturasGlobal = dataFac.facturas || [];

        // POLYFILL para múltiples cotizaciones (el título global ya no existe)
        facturasGlobal.forEach(f => {
            if (!f.titulo && f.cotizaciones && f.cotizaciones.length > 0) {
                f.titulo = f.cotizaciones.length > 1 ? f.cotizaciones[0].titulo + " (+" + (f.cotizaciones.length - 1) + " más)" : f.cotizaciones[0].titulo;
                f.mantenimiento = f.cotizaciones[0].mantenimiento;
            }
        });

        const resRep = await fetch('/api/reportes/lista');
        const dataRep = await resRep.json();
        reportesGlobal = dataRep.reportes || [];

        const tbody = document.getElementById('tabla-facturas');
        const tbodyFinales = document.getElementById('tabla-facturas-finales');
        const tbodyDocContables = document.getElementById('tabla-doc-contables');
        const tbodyArchivo = document.getElementById('tabla-archivo');
        const tbodyArchivoProv = document.getElementById('tabla-archivo-prov');
        const tbodyArchivoCorp = document.getElementById('tabla-archivo-corp');
        const rolUsuario = document.getElementById('rol-actual').value;
        const nombreProveedorActual = document.getElementById('nombre-proveedor-actual') ? document.getElementById('nombre-proveedor-actual').value : '';

        if (tbody) tbody.innerHTML = '';
        if (tbodyFinales) tbodyFinales.innerHTML = '';
        if (tbodyDocContables) tbodyDocContables.innerHTML = '';
        if (tbodyArchivo) tbodyArchivo.innerHTML = '';
        let tbodyArchivoCancelado = document.getElementById('tabla-archivo-cancelado');
        if (tbodyArchivoCancelado) tbodyArchivoCancelado.innerHTML = '';
        if (tbodyArchivoProv) tbodyArchivoProv.innerHTML = '';
        if (tbodyArchivoCorp) tbodyArchivoCorp.innerHTML = '';

        if (facturasGlobal.length === 0) {
            if (tbody) tbody.innerHTML = `<tr><td colspan="${rolUsuario === 'administracion' ? '8' : '7'}" style="text-align:center;">No hay cotizaciones registradas</td></tr>`;
            if (tbodyFinales) tbodyFinales.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay facturas registradas</td></tr>`;
        }
        else {
            let countCotizaciones = 0;
            let countFacturas = 0;
            let countDocContables = 0;
            let countArchivo = 0;
            let countArchivoProv = 0;
            let countArchivoCorp = 0;

            facturasGlobal.forEach(f => {

                let tituloCompleto = f.titulo || 'Sin Título';
                if (f.cotizaciones && f.cotizaciones.length > 1) {
                    tituloCompleto = f.cotizaciones.map((c, i) => `Cot ${i + 1}: ${c.titulo || 'Sin Título'}`).join('<br>');
                }

                let precioFormatArch = parseFloat(f.precio_estimado || f.precio || 0).toLocaleString('en-US');

                if (f.estado === 'Cancelado_Cotizacion_Cara') {
                    if (tbodyArchivoCancelado && rolUsuario === 'administracion') {
                        let btnVerExp = `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0; width:100%; background:#0284c7; border:none; color:white;" onclick="abrirDetalles('${f.id}')">Ver Detalles del Ticket</button>`;
                        let idRep = obtenerIdReporte(f) || 'N/A';
                        let btnEliminar = `<button class="btn-danger" style="font-size:0.8em; padding:8px 10px; margin:0; width:100%; background:#ef4444; border:none; color:white; border-radius:4px; margin-top:5px; cursor:pointer;" onclick="eliminarFacturaSilenciosa('${f.id}')">Eliminar</button>`;
                        tbodyArchivoCancelado.innerHTML += `<tr><td><span style="color:#ef4444; font-weight:bold;">${idRep}</span></td><td>${f.unidad}</td><td><strong>${f.proveedor}</strong></td><td><span style="color:#ef4444; font-weight:bold;">Cancelado por Cotización Cara</span></td><td><div style="display:flex; flex-direction:column; gap:5px;">${btnVerExp}${btnEliminar}</div></td></tr>`;
                    }
                    return; // skip active trays
                }

                if (f.estado === 'Archivado' || (rolUsuario === 'proveedores' && f.validacion_fiscal === 'Aprobada')) {
                    if (f.estado === 'Archivado' && tbodyArchivo && rolUsuario === 'administracion') {
                        let btnVerExp = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">
                            <button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#0284c7; border:none; color:white; margin:0; width:100%;" onclick="abrirDetalles('${f.id}')">Ver Detalles del Ticket</button>
                            <div class="dropdown-container" style="position:relative;">
                                <button class="btn-dropdown-toggle btn-info" style="font-size:0.8em; padding:8px 10px; background:#f59e0b; border:none; color:#111; margin:0; width:100%;" onclick="toggleDropdownFixed(event, this)">✏️ Editar Sección ▼</button>
                                <div class="dropdown-menu-fixed">
                                    <button onclick="abrirModalEditarAdmin('${f.id}', 1)">1. Reporte de Incidencia</button>
                                    <button onclick="abrirModalEditarAdmin('${f.id}', 2)">2. Diagnóstico y Cotización</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'orden')">3. Orden de Pedido</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'factura')">4. Factura Fiscal</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'doc_contable')">5. Documento Contable</button>
                                </div>
                            </div>
                            <button class="btn-danger-sm" style="width:100%; background:#ef4444; border:none; color:white; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaSilenciosa('${f.id}')">Eliminar</button>
                        </div>`;
                        let idReporteAsociado = obtenerIdReporte(f) || 'N/A';
                        tbodyArchivo.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idReporteAsociado}</span></td><td><strong>${f.numero_doc50}</strong></td><td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.unidad}</td><td><strong>${f.proveedor}</strong></td><td>$${precioFormatArch} MXN</td><td>${btnVerExp}</td></tr>`;
                        countArchivo++;
                    }

                    if (tbodyArchivoProv && rolUsuario === 'proveedores' && f.proveedor === nombreProveedorActual) {
                        let idRepArchProv = obtenerIdReporte(f) || 'S/T';
                        let btnVerExp = `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoProv.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idRepArchProv}</span></td><td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.unidad}</td><td><strong>${tituloCompleto}</strong></td><td>$${precioFormatArch} MXN</td><td>${btnVerExp}</td></tr>`;
                        countArchivoProv++;
                    }

                    if (tbodyArchivoCorp && rolUsuario === 'corporativos') {
                        let idRepArchCorp = obtenerIdReporte(f) || 'S/T';
                        let btnVerExp = `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoCorp.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idRepArchCorp}</span></td><td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.unidad}</td><td><strong>${f.proveedor}</strong></td><td><strong>${tituloCompleto}</strong></td><td>$${precioFormatArch} MXN</td><td>${btnVerExp}</td></tr>`;
                        countArchivoCorp++;
                    }
                    return; // Skip rendering in active trays
                }

                let apAdmin = f.aprobado_admin !== undefined ? f.aprobado_admin : (f.estado === 'Confirmada');
                let apCorp = f.aprobado_corp !== undefined ? f.aprobado_corp : (f.estado === 'Confirmada');
                let confirmadaTotal = (apAdmin && apCorp);
                let badgeColor, textoEstado;

                if (f.estado_custom && f.estado_custom !== "") { textoEstado = f.estado_custom; badgeColor = confirmadaTotal ? '#2d6a4f' : '#b45309'; }
                else if (confirmadaTotal) { badgeColor = '#2d6a4f'; textoEstado = 'Aprobada (Con Orden)'; }
                else { badgeColor = '#b45309'; let p = []; if (!apAdmin) p.push('Admin'); if (!apCorp) p.push('Corp'); textoEstado = 'Pendiente: ' + p.join(' y '); }
                let estadoBadge = `<span style="background:${badgeColor}; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">${textoEstado}</span>`;

                let entregadoTexto = f.entregado || 'No';
                let entregadoBadge = entregadoTexto === 'Sí'
                    ? `<span style="color:#40916c; font-weight:bold;">Sí ✅</span>`
                    : `<span style="color:#ef4444; font-weight:bold;">No ❌</span>`;

                let precioBonito = formatearMoneda(f.precio);
                let btnAccion = '';

                if (rolUsuario === 'administracion') {
                    btnAccion = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">`;

                    if (!apAdmin) {
                        btnAccion += `<button class="btn-success" onclick="abrirRevisionAdmin('${f.id}')" style="display:block; width:100%; margin:0;">Aprobar y Asignar Orden</button>`;
                    } else {
                        btnAccion += `<button class="btn-info" onclick="abrirDetalles('${f.id}')" style="display:block; width:100%; margin:0;">Ver Detalles</button>`;
                    }

                    if (confirmadaTotal && entregadoTexto !== 'Sí') {
                        btnAccion += `<button class="btn-info" onclick="abrirModalValidacion('${f.id}', '${f.unidad.replace('8090-', '')}')" style="background:#0284c7; width:100%; margin:0; border:none;">🔑 Validar PIN Chofer</button>`;
                    } else if (!confirmadaTotal) {
                        btnAccion += `<button disabled class="btn-info" style="background:#475569; color:#94a3b8; border:none; width:100%; margin:0; cursor:not-allowed;">🔒 Esperando Confirmación</button>`;
                    }

                    btnAccion += `<div style="display:flex; gap:5px;"><button class="btn-danger-sm" style="flex:1; margin:0;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar</button></div>`;

                    btnAccion += `</div>`;
                } else if (rolUsuario === 'corporativos') {
                    if (!apCorp) btnAccion = `<button class="btn-success" onclick="abrirRevisionCorp('${f.id}')">Revisar Gasto Mayor</button>`;
                    else btnAccion = `<button class="btn-info" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                } else {
                    btnAccion = `<div style="display:flex; flex-direction:column; gap:5px; align-items:flex-start;">
                        <span style="font-size:0.9em; font-weight:bold; color:#a3b1c6;">${f.numero_orden ? 'Orden Oficial: <span style="color:#f59e0b;">' + f.numero_orden + '</span>' : 'En revisión...'}</span>
                        <button class="btn-info" style="font-size:0.8em; padding:6px 10px;" onclick="abrirDetalles('${f.id}')">Ver Detalles (PDF)</button>`;

                    if (confirmadaTotal && entregadoTexto !== 'Sí') {
                        if (!f.codigo_liberacion) {
                            btnAccion += `<button class="btn-success-modal" style="font-size:0.8em; padding:8px 10px; background:#10b981; border:none; margin-top:5px; width:100%;" onclick="marcarUnidadLista('${f.id}')">✔️ Marcar Unidad Lista</button>`;
                        } else {
                            btnAccion += `<span style="color:#0ea5e9; font-size:0.85em; font-weight:bold; margin-top:5px;">⌛ Esperando al chofer... (PIN enviado)</span>`;
                        }
                    } else if (confirmadaTotal && entregadoTexto === 'Sí') {
                        if (!f.factura_folio) {
                            btnAccion += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#0284c7; border:none; margin-top:5px; width:100%;" onclick="abrirModalSubirFactura('${f.id}')">🧾 Subir Factura Final (PDF)</button>`;
                        } else {
                            if (f.cotizaciones && f.cotizaciones.length > 1) {
                                btnAccion += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#40916c; border:none; margin-top:5px; width:100%;" onclick="abrirModalVerFacturasSubidas('${f.id}')">📄 Ver Facturas Subidas</button>`;
                            } else {
                                btnAccion += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#40916c; border:none; margin-top:5px; width:100%;" onclick="abrirModalVerFacturasSubidas('${f.id}')">📄 Ver Factura Subida</button>`;
                            }
                        }
                    }
                    btnAccion += `</div>`;
                }

                let ciaExtra = f.compania ? ` | Cia: <strong style="color:white;">${f.compania}</strong>` : ``;
                let infoExtra = `<br><small style="color:#a3b1c6;">Ticket: ${obtenerIdReporte(f) || 'S/T'} | Orden: <strong style="color:#f59e0b;">${f.numero_orden || 'Pendiente'}</strong>${ciaExtra}</small>`;
                let tdTitulo = `<td>${tituloCompleto}${infoExtra}</td>`;

                let indStr = '';
                if (f.cotizaciones && f.cotizaciones.length > 1) {
                    indStr = f.cotizaciones.map((c, i) => `Cot ${i + 1}: $${parseFloat(c.precio || 0).toLocaleString('en-US')}`).join('<br>');
                } else {
                    indStr = `$${parseFloat(f.precio || 0).toLocaleString('en-US')}`;
                }
                let tdPrecioInd = `<td><small style="color:#a3b1c6;">${indStr}</small></td>`;

                let idRepForTable = obtenerIdReporte(f) || 'S/T';
                let tdTicket = `<td><span style="color:#0ea5e9; font-weight:bold;">${idRepForTable}</span></td>`;

                if ((rolUsuario === 'proveedores' || rolUsuario === 'administracion') && entregadoTexto === 'Sí') {
                    if (tbodyFinales) {
                        let foliosArr = [];
                        let f_cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [f];
                        f_cots.forEach((c, idx) => {
                            if (c.factura_folio) foliosArr.push(f_cots.length > 1 ? `Cot ${idx + 1}: ${c.factura_folio}` : c.factura_folio);
                        });
                        let badgeFolio = foliosArr.length > 0
                            ? `<span style="color:#10b981; font-weight:bold;">${foliosArr.join('<br>')}</span>`
                            : `<span style="color:#ef4444; font-weight:bold;">Pendiente</span>`;
                        let btnAdminExtra = '';
                        let estadoFiscalBadge = '';

                        if (rolUsuario === 'administracion') {
                            btnAdminExtra = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">`;
                            btnAdminExtra += `<button class="btn-info" onclick="abrirDetalles('${f.id}')" style="display:block; width:100%; margin:0;">Ver Detalles</button>`;


                            let valFiscal = f.validacion_fiscal || 'Pendiente';

                            if (valFiscal === 'Aprobada') {
                                if (rolUsuario === 'administracion') {
                                    if (tbodyDocContables) {
                                        let btnDoc = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">
                                            <button class="btn-info" style="display:block; width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>
                                            <button class="btn-success" style="display:block; width:100%; margin:0;" onclick="abrirModalDocContable('${f.id}')">Ingresar Número de Doc. Contable</button>
                                            <button class="btn-danger-sm" style="display:block; width:100%; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar</button>
                                        </div>`;
                                        tbodyDocContables.innerHTML += `<tr>${tdTicket}<td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.fecha}</td><td><strong>${f.proveedor}</strong></td><td>${f.unidad}</td><td>${tituloCompleto}</td>${tdPrecioInd}<td><strong>$${precioBonito} MXN</strong></td><td>${btnDoc}</td></tr>`;
                                        countDocContables++;
                                    }
                                    return; // Ocultar de la bandeja Facturas de administracion
                                }
                            }

                            if (f.factura_folio) {

                                if (valFiscal === 'Pendiente') {
                                    estadoFiscalBadge = `<span style="background:#b45309; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Pendiente Validación</span>`;
                                    btnAdminExtra += `<button class="btn-success" style="display:block; width:100%; margin:0;" onclick="abrirModalValidacionFiscal('${f.id}', '${f.factura_folio}', '${f.pdf_fiscal || f.factura_pdf}', '${f.unidad}')">Revisar y Validar</button>`;
                                } else if (valFiscal === 'Aprobada') {
                                    estadoFiscalBadge = `<span style="background:#2d6a4f; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Factura Aprobada</span>`;
                                    btnAdminExtra += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#ef4444; border:none; margin:0; width:100%;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_fiscal || f.factura_pdf}')">📄 Ver Factura PDF</button>`;
                                } else {
                                    estadoFiscalBadge = `<span style="background:#ef4444; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Rechazada</span>`;
                                }
                            } else {
                                estadoFiscalBadge = `<span style="color:#b45309; font-weight:bold;">Esperando Factura</span>`;
                                btnAdminExtra += `<span style="color:#b45309; font-size:0.85em;">Esperando subida de proveedor</span>`;
                            }

                            btnAdminExtra += `<button class="btn-danger-sm" style="display:block; width:100%; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaSilenciosa('${f.id}')">Eliminar del Sistema</button>`;
                            btnAdminExtra += `</div>`;
                        }

                        let tdProv = rolUsuario === 'administracion' ? `<td><strong>${f.proveedor}</strong></td>` : '';
                        let tdEstadoFiscal = rolUsuario === 'administracion' ? `<td>${estadoFiscalBadge}</td>` : '';
                        let tdEstado = rolUsuario === 'proveedores' ? `<td>${estadoBadge}</td>` : '';
                        let tdEntregadoFinal = rolUsuario === 'administracion' ? `<td>${entregadoBadge}</td>` : '';
                        let acciones = rolUsuario === 'administracion' ? btnAdminExtra : btnAccion;

                        tbodyFinales.innerHTML += `<tr>${tdTicket}<td>${badgeFolio}</td><td>${f.fecha}</td>${tdProv}<td>${f.unidad}</td>${tdTitulo}${tdPrecioInd}<td><strong>$${precioBonito} MXN</strong></td>${tdEstadoFiscal}${tdEstado}${tdEntregadoFinal}<td>${acciones}</td></tr>`;
                        countFacturas++;
                    }
                } else {
                    if (tbody) {
                        let tdEntregado = rolUsuario === 'administracion' ? `<td>${entregadoBadge}</td>` : '';
                        tbody.innerHTML += `<tr>${tdTicket}<td>${f.fecha}</td>${rolUsuario !== 'proveedores' ? `<td><strong>${f.proveedor}</strong></td>` : ''}<td>${f.unidad}</td>${tdTitulo}${tdPrecioInd}<td><strong>$${precioBonito} MXN</strong></td><td>${estadoBadge}</td>${tdEntregado}<td>${btnAccion}</td></tr>`;
                        countCotizaciones++;
                    }
                }
            });


            if (tbody && countCotizaciones === 0) tbody.innerHTML = `<tr><td colspan="${rolUsuario === 'administracion' ? '8' : '7'}" style="text-align:center;">No hay cotizaciones registradas</td></tr>`;
            if (tbodyFinales && countFacturas === 0) tbodyFinales.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay facturas registradas</td></tr>`;
            if (tbodyDocContables && countDocContables === 0) tbodyDocContables.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay documentos contables pendientes</td></tr>`;
            if (tbodyArchivo && countArchivo === 0) tbodyArchivo.innerHTML = `<tr><td colspan="6" style="text-align:center;">No hay registros archivados</td></tr>`;
            if (tbodyArchivoCorp && countArchivoCorp === 0) tbodyArchivoCorp.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay registros archivados</td></tr>`;
        }
    } catch (err) { console.error("Error al cargar datos globales", err); }
}

function marcarUnidadLista(idFactura) {
    if (!confirm("¿¿Confirmas que la reparación terminóó?\n\nAl aceptar, se enviaráá un correo automático al chofer con su PIN para que pase a recoger la unidad en este momento.")) return;
    mostrarLoaderDinamico("Generando código PIN...", "Notificando al chofer 📧");

    fetch('/api/facturas/marcar_lista', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: idFactura })
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirModalSubirFactura(idFactura) {
    let modal = document.getElementById('modal-subir-factura-dinamico');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-subir-factura-dinamico';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-box large">
                <button class="btn-close-modal" onclick="cerrarModal('modal-subir-factura-dinamico')">×</button>
                <h3 class="modal-header" style="color: #10b981;">🧾 Subir Factura Contable (Final)</h3>
                <p style="color: #a3b1c6; margin-bottom: 15px; font-size: 14px;">Ingresa el folio fiscal y el PDF para cada cotización.</p>
                <form id="form-subir-factura" onsubmit="event.preventDefault(); procesarSubidaFactura();">
                    <input type="hidden" id="hidden-factura-final-id" name="id_factura">
                    <div id="subir-factura-container"></div>
                    <div class="modal-actions" style="margin-top: 25px;">
                        <button type="button" class="btn-danger" onclick="cerrarModal('modal-subir-factura-dinamico')">Cancelar</button>
                        <button type="submit" class="btn-success-modal" style="display:block; width:100%; background:#10b981;">Confirmar y Enviar</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
    }

    const f = facturasGlobal.find(x => String(x.id) === String(idFactura));
    let container = document.getElementById('subir-factura-container');
    container.innerHTML = '';

    let cots = f && f.cotizaciones ? f.cotizaciones : [{ precio: f ? f.precio : 0 }];

    cots.forEach((cot, idx) => {
        container.innerHTML += `
            <div style="margin-bottom:15px; padding:15px; background:#0b1c30; border:1px dashed #10b981; border-radius:8px;">
                <h4 style="color:#10b981; margin-bottom:10px;">Cotización ${idx + 1}: ${cot.titulo || 'Sin Título'} (Orden: ${cot.numero_orden || 'N/A'})</h4>
                <div class="input-group full-width">
                    <label>Folio Fiscal (Ej. F-1029)</label>
                    <input type="text" name="folio[]" required style="width:100%; padding:10px; border-radius:8px;">
                </div>
                <div class="input-group full-width" style="margin-top:15px;">
                    <label>Archivo PDF de la Factura Oficial</label>
                    <input type="file" name="pdf_factura[]" accept=".pdf" required onchange="previsualizarPDFLocal(this)" style="padding:10px; background:#112641; border:1px solid #1f395a; border-radius:8px; color:white; width:100%;">
                    <div class="pdf-preview-container" style="margin-top: 15px; display: none;">
                        <iframe src="" width="100%" height="400px" style="border: 1px solid #10b981; border-radius: 8px;"></iframe>
                    </div>
                </div>
            </div>
        `;
    });

    document.getElementById('hidden-factura-final-id').value = idFactura;
    modal.style.display = 'flex';
}

function previsualizarPDFLocal(input) {
    let previewContainer = input.nextElementSibling;
    if (previewContainer && previewContainer.classList.contains('pdf-preview-container')) {
        let iframe = previewContainer.querySelector('iframe');
        if (input.files && input.files[0]) {
            let file = input.files[0];
            if (file.type === "application/pdf") {
                let fileUrl = URL.createObjectURL(file);
                iframe.src = fileUrl;
                previewContainer.style.display = 'block';
            } else {
                alert("Por favor selecciona un archivo PDF válido.");
                input.value = "";
                iframe.src = '';
                previewContainer.style.display = 'none';
            }
        } else {
            iframe.src = '';
            previewContainer.style.display = 'none';
        }
    }
}

function abrirModalVerFacturasSubidas(idFactura) {
    let modal = document.getElementById('modal-ver-facturas-prov');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-ver-facturas-prov';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-box large" style="max-width: 1200px; width: 90vw;">
                <button class="btn-close-modal" onclick="cerrarModal('modal-ver-facturas-prov')">×</button>
                <h3 class="modal-header" style="color: #40916c;">📄 Facturas Fiscales Subidas</h3>
                <div style="background: #081422; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #1f395a; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #a3b1c6; font-size: 1.1em;">Folio(s): <strong id="ver-prov-folio-text" style="color: #10b981; font-size: 1.2em;"></strong></span>
                    <span style="color: #a3b1c6; font-size: 1.1em;">Unidad: <strong id="ver-prov-unidad-text" style="color: white;"></strong></span>
                </div>
                <div id="ver-prov-nav-facturas" style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;"></div>
                <div style="margin-bottom: 20px; height: 60vh; min-height: 400px; border: 2px solid #1f395a; border-radius: 8px; overflow: hidden; background: white;">
                    <iframe id="ver-prov-pdf-frame" src="" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
                <div class="modal-actions" style="margin-top: 15px;">
                    <button type="button" class="btn-danger" style="width:100%; margin:0;" onclick="cerrarModal('modal-ver-facturas-prov')">Cerrar Visor</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    const f = facturasGlobal.find(x => String(x.id) === String(idFactura));
    if (!f) return;

    document.getElementById('ver-prov-unidad-text').innerText = f.unidad;
    let cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [f];
    let allFacturas = cots.filter(c => c.factura_folio || c.factura_pdf || c.pdf_fiscal);

    let folioText = "";
    if (f.cotizaciones && f.cotizaciones.length > 1) {
        folioText = allFacturas.map((c, i) => `Cot ${i + 1}: ${c.factura_folio || 'N/A'}`).join(' | ');
    } else {
        folioText = f.factura_folio || 'N/A';
    }
    document.getElementById('ver-prov-folio-text').innerText = folioText;

    let navContainer = document.getElementById('ver-prov-nav-facturas');
    navContainer.innerHTML = '';

    if (allFacturas.length > 0) {
        let firstPdf = allFacturas[0].factura_pdf || allFacturas[0].pdf_fiscal || f.factura_pdf || f.pdf_fiscal;
        document.getElementById('ver-prov-pdf-frame').src = '/static/facturas_archivos/' + firstPdf;

        if (allFacturas.length > 1) {
            navContainer.innerHTML = allFacturas.map((c, i) =>
                `<button type="button" style="background:#10b981; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.85em;" onclick="document.getElementById('ver-prov-pdf-frame').src='/static/facturas_archivos/${c.factura_pdf || c.pdf_fiscal}'">📄 Cotización ${i + 1}: ${c.factura_folio || 'N/A'}</button>`
            ).join('');
        }
    } else {
        document.getElementById('ver-prov-pdf-frame').src = '';
    }

    modal.style.display = 'flex';
}

function procesarSubidaFactura() {
    if (!confirm("¿Estás seguro de anexar este documento fiscal al expediente?")) return;
    mostrarLoaderDinamico("Subiendo documento contable...", "Enlazando al expediente de la unidad 🗂️");
    let formData = new FormData(document.getElementById('form-subir-factura'));
    fetch('/api/facturas/subir_factura_final', {
        method: 'POST',
        body: formData
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') {
            cerrarModal('modal-subir-factura-dinamico');
            cargarFacturas();
        }
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirModalRechazo(idItem, tipo) {
    // Esconder otros modales si están abiertos
    let modAdmin = document.getElementById('modal-revision-admin');
    if (modAdmin) modAdmin.style.display = 'none';
    let modCorp = document.getElementById('modal-revision-corp');
    if (modCorp) modCorp.style.display = 'none';
    let modFiscal = document.getElementById('modal-validacion-fiscal');
    if (modFiscal) modFiscal.style.display = 'none';

    let hiddenId = document.getElementById('hidden-rechazo-id');
    let hiddenTipo = document.getElementById('hidden-rechazo-tipo');
    let inputMotivo = document.getElementById('input-motivo-rechazo');
    let modalMotivo = document.getElementById('modal-motivo-rechazo');

    if (!hiddenId || !hiddenTipo || !inputMotivo || !modalMotivo) {
        alert("Error: El modal de rechazo no se encuentra en esta página.");
        return;
    }

    hiddenId.value = idItem;
    hiddenTipo.value = tipo;
    inputMotivo.value = '';

    modalMotivo.style.display = 'flex';
}

function procesarRechazoConMotivo() {
    let idItem = document.getElementById('hidden-rechazo-id').value;
    let tipo = document.getElementById('hidden-rechazo-tipo').value;
    let motivo = document.getElementById('input-motivo-rechazo').value.trim();

    if (!motivo) {
        alert("Por favor, especifique el motivo del rechazo en el cuadro de texto.");
        return;
    }

    let accionTxt = "RECHAZAR o ELIMINAR este registro";
    if (tipo === 'factura') accionTxt = "RECHAZAR esta cotización";
    if (tipo === 'reporte') accionTxt = "ELIMINAR este reporte";
    if (tipo === 'fiscal') accionTxt = "RECHAZAR esta factura fiscal";
    if (tipo === 'usuario') accionTxt = "RECHAZAR y ELIMINAR este usuario";

    if (!confirm(`¿Estás 100% seguro de ${accionTxt}? Esta acción es irreversible.`)) return;

    document.getElementById('modal-motivo-rechazo').style.display = 'none';
    mostrarLoaderDinamico("Procesando...", "Notificando motivo al usuario \u23F3");

    let url = '';
    if (tipo === 'factura') url = '/api/facturas/rechazar';
    else if (tipo === 'reporte') url = '/api/reportes/eliminar';
    else if (tipo === 'fiscal') url = '/api/facturas/rechazar_fiscal';
    else if (tipo === 'usuario') url = '/api/rechazar';

    let payload = tipo === 'usuario' ? { identificador: idItem, motivo: motivo } : { id: idItem, motivo: motivo };

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            ocultarLoaderDinamico();
            alert(data.message);
            if (data.status === 'success') {
                if (tipo === 'usuario') { if (typeof cargarPendientes === 'function') cargarPendientes(); }
                else if (tipo === 'reporte') { if (typeof cargarReportesAdmin === 'function') cargarReportesAdmin(); else cargarFacturas(); }
                else { if (typeof cargarFacturasAdmin === 'function') cargarFacturasAdmin(); else cargarFacturas(); }
            }
        })
        .catch(err => {
            ocultarLoaderDinamico();
            console.error("Error al procesar rechazo:", err);
        });
}

function eliminarFacturaDefinitiva(idFactura) { abrirModalRechazo(idFactura, 'factura'); }

function eliminarFacturaSilenciosa(idFactura) {
    if (!confirm("¿Estás 100% seguro de ELIMINAR este registro de forma permanente del sistema? No se pedirá motivo ni se notificará al chofer.")) return;

    fetch('/api/facturas/eliminar_silencioso', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: idFactura })
    }).then(r => r.json()).then(d => {
        if (d.status === 'success') {
            alert("Registro eliminado exitosamente.");
            document.getElementById('modal-detalles-general').style.display = 'none';
            cargarSistemaCompleto();
        } else {
            alert("Error: " + d.message);
        }
    });
}
function rechazarFactura(inputIdModal) { let id_fac = document.getElementById(inputIdModal).value; abrirModalRechazo(id_fac, 'factura'); }
function eliminarReporteDefinitivo(idReporte) { abrirModalRechazo(idReporte, 'reporte'); }

function abrirModalEditarAdmin(idFactura, seccionId = null) {
    try {
        const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if (!f) return;
        document.getElementById('edit_id_factura').value = f.id;
        document.getElementById('edit_unidad').value = f.unidad.replace('8090-', '');
        document.getElementById('edit_responsable').value = f.responsable;
        document.getElementById('edit_telefono').value = f.telefono;
        document.getElementById('edit_fecha').value = f.fecha;
        document.getElementById('edit_titulo').value = f.titulo;

        if (f.reporte_inicial) {
            let r = f.reporte_inicial;
            if (document.getElementById('edit_kilometraje')) document.getElementById('edit_kilometraje').value = r.kilometraje || '';
            if (document.getElementById('edit_marca')) document.getElementById('edit_marca').value = r.marca || '';
            if (document.getElementById('edit_modelo')) document.getElementById('edit_modelo').value = r.modelo || '';
            if (document.getElementById('edit_email')) document.getElementById('edit_email').value = r.email || '';
            if (document.getElementById('edit_ciudad')) document.getElementById('edit_ciudad').value = r.ciudad || '';
            if (document.getElementById('edit_cope')) document.getElementById('edit_cope').value = r.cope || '';
            if (document.getElementById('edit_departamento')) document.getElementById('edit_departamento').value = r.departamento || '';
            if (document.getElementById('img-firma-operador') && r.firma_chofer) {
                document.getElementById('container-firma').style.display = 'block';
                document.getElementById('img-firma-operador').src = r.firma_chofer;
            } else if (document.getElementById('container-firma')) {
                document.getElementById('container-firma').style.display = 'none';
            }
        } else {
            if (document.getElementById('edit_kilometraje')) document.getElementById('edit_kilometraje').value = '';
            if (document.getElementById('edit_marca')) document.getElementById('edit_marca').value = '';
            if (document.getElementById('edit_modelo')) document.getElementById('edit_modelo').value = '';
            if (document.getElementById('edit_email')) document.getElementById('edit_email').value = '';
            if (document.getElementById('edit_ciudad')) document.getElementById('edit_ciudad').value = '';
            if (document.getElementById('edit_cope')) document.getElementById('edit_cope').value = '';
            if (document.getElementById('edit_departamento')) document.getElementById('edit_departamento').value = '';
            if (document.getElementById('container-firma')) document.getElementById('container-firma').style.display = 'none';
        }
        document.getElementById('edit_retro').value = limpiarRetro(f.retro);
        document.getElementById('edit_diagnostico').value = f.diagnostico || ''; document.getElementById('edit_trabajo_realizar').value = f.trabajo_realizar || ''; document.getElementById('edit_mantenimiento').value = f.mantenimiento; document.getElementById('edit_numero_orden').value = f.numero_orden || '';
        let inputPrecio = document.getElementById('edit_precio'); inputPrecio.value = f.precio; formatearEnInput(inputPrecio);
        dtCotizacionEdicion = new DataTransfer(); dtEvidenciaEdicion = new DataTransfer();
        document.getElementById('edit-preview-cotizacion-nuevas').innerHTML = ''; document.getElementById('edit-preview-evidencia-nuevas').innerHTML = '';
        imagenesGuardadasCotizacion = [...f.fotos_cotizacion]; imagenesGuardadasEvidencia = [...f.fotos_evidencia];
        renderizarImagenesGuardadas();
        // Mostrar/ocultar campos segun la seccion
        const formGroups = document.querySelectorAll('#form-editar-admin .input-group');
        formGroups.forEach(group => {
            let groupSec = group.getAttribute('data-seccion');
            if (seccionId === null) {
                group.style.display = 'block'; // Mostrar todo si no hay seccion especificada
            } else if (groupSec) {
                let sectionsArray = String(groupSec).split(' ');
                group.style.display = sectionsArray.includes(String(seccionId)) ? 'block' : 'none';
            }
        });

        // Cambiar texto de etiquetas dinámicamente según la sección (UX enhancement)
        let lblResponsable = document.getElementById('label_edit_responsable');
        let lblTitulo = document.getElementById('label_edit_titulo');
        let lblRetro = document.getElementById('label_edit_retro');

        if (lblResponsable) {
            if (seccionId === 1) lblResponsable.textContent = "Nombre del Empleado (Completo)";
            else if (seccionId === 2) lblResponsable.textContent = "Responsable en Turno";
        }
        if (lblTitulo) {
            if (seccionId === 1) lblTitulo.textContent = "Título del Reporte";
            else if (seccionId === 2) lblTitulo.textContent = "Título de la Factura";
        }
        if (lblRetro) {
            if (seccionId === 1) lblRetro.textContent = "Descripción Detallada del Problema (Retro)";
            else if (seccionId === 2) lblRetro.textContent = "Retro (Problema/Situación)";
        }

        document.getElementById('modal-editar-admin').style.display = 'flex';

    } catch (err) { alert("Error in Modal Admin: " + err.message); console.error(err); }
}

function actualizarFacturaAdmin() {
    if (!confirm("¿¿Confirmas la actualización de datos? (Si el precio es >= $10,001 se enviaráá al corporativo).")) return;
    let inputPrecio = document.getElementById('edit_precio'); inputPrecio.value = inputPrecio.value.replace(/[^0-9.]/g, '');
    let formData = new FormData(document.getElementById('form-editar-admin'));

    let idFac = document.getElementById('edit_id_factura').value;
    let f = facturasGlobal.find(x => String(x.id) === String(idFac));
    if (f) {
        let idRep = obtenerIdReporte(f);
        if (idRep) {
            let retroLimpio = formData.get('retro');
            formData.set('retro', `[TICKET:${idRep}]\n${retroLimpio}`);
        }
    }

    formData.append('cotizaciones_guardadas', JSON.stringify(imagenesGuardadasCotizacion)); formData.append('evidencias_guardadas', JSON.stringify(imagenesGuardadasEvidencia));
    fetch('/api/facturas/editar', { method: 'POST', body: formData }).then(res => res.json()).then(data => { alert(data.message); if (data.status === 'success') { document.getElementById('modal-editar-admin').style.display = 'none'; cargarFacturas(); } });
}

function abrirModalNuevaFactura() {
    document.getElementById('form-nueva-factura').reset();

    const container = document.getElementById('lista-cotizaciones');
    if (container) {
        container.innerHTML = '';
        agregarCotizacionFila();
    }

    if (document.getElementById('hidden_numero_reporte')) document.getElementById('hidden_numero_reporte').value = '';
    if (document.getElementById('etiqueta-reporte-vinculado')) document.getElementById('etiqueta-reporte-vinculado').style.display = 'none';
    document.getElementById('modal-nueva-factura').style.display = 'flex';
}

function previsualizarFactura() {
    let container = document.getElementById('lista-cotizaciones');
    if (!container || container.children.length === 0) {
        alert("Debe agregar al menos una cotización."); return;
    }

    let precios = document.querySelectorAll('input[name="precio[]"]');
    let total = 0;
    precios.forEach(p => {
        let val = parseFloat(p.value.replace(/[^0-9.]/g, ''));
        if (!isNaN(val)) total += val;
    });

    // Generar vista previa dinámica (Sección 2 entera es dinámica)
    let seccion2HTML = `<div style="margin-bottom: 20px; border: 2px dashed #0284c7; padding: 15px; border-radius: 8px; background-color: #fafafa;">`;
    seccion2HTML += `<div class="pdf-section-title" style="color: #0284c7; border-bottom: 1px solid #0284c7; padding-bottom: 5px; margin-bottom: 10px;">■ SECCIÓN 2: DIAGNÓSTICO Y FACTURACIÓN (TALLER)</div>`;
    seccion2HTML += `<div class="pdf-line"><strong>Unidad:</strong> 8090-${document.querySelector('input[name="unidad"]').value}</div>`;
    seccion2HTML += `<div class="pdf-line"><strong>Responsable:</strong> ${document.querySelector('input[name="responsable"]').value}</div>`;
    seccion2HTML += `<div class="pdf-line"><strong>Teléfono:</strong> ${document.querySelector('input[name="telefono"]').value}</div>`;
    seccion2HTML += `<div class="pdf-line" style="margin-bottom:15px;"><strong>Fecha Taller:</strong> ${document.querySelector('input[name="fecha"]').value}</div>`;

    const filas = container.children;
    for (let i = 0; i < filas.length; i++) {
        let fila = filas[i];
        let t = fila.querySelector('input[name="titulo[]"]').value;
        let m = fila.querySelector('select[name="mantenimiento[]"]').value;
        let r = fila.querySelector('textarea[name="retro[]"]').value;
        let d = fila.querySelector('textarea[name="diagnostico[]"]').value;
        let tr = fila.querySelector('textarea[name="trabajo_realizar[]"]').value;
        let p = fila.querySelector('input[name="precio[]"]').value;
        let pdf = fila.querySelector('input[name="pdf_cotizacion[]"]');
        let fotos = fila.querySelector(`input[name="fotos_evidencia_${i}[]"]`);

        seccion2HTML += `<div style="margin-top:20px; padding-top:15px; border-top:1px dashed #0284c7;">`;
        seccion2HTML += `<h4 style="color:#0284c7; margin-bottom:10px;">Cotización ${i + 1}: ${t}</h4>`;
        seccion2HTML += `<div class="pdf-line"><strong>Mantenimiento:</strong> ${m}</div>`;
        seccion2HTML += `<div class="pdf-line"><strong>Precio Cotizado (Sin IVA):</strong> <span style="color:#000000;">${p}</span></div>`;
        seccion2HTML += `<div class="pdf-line"><strong>Retro:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#f9f9f9; border-left:3px solid #0284c7; color:#333;">${r}</div></div>`;
        seccion2HTML += `<div class="pdf-line"><strong>Diagnóstico:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#f9f9f9; border-left:3px solid #0284c7; color:#333;">${d}</div></div>`;
        seccion2HTML += `<div class="pdf-line"><strong>Trabajo a Realizar:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#f9f9f9; border-left:3px solid #0284c7; color:#333;">${tr}</div></div>`;

        // Evidencias
        let hasPdf = pdf.files && pdf.files.length > 0 ? pdf.files[0].name : "No";
        seccion2HTML += `<div class="pdf-line" style="margin-top:10px;"><strong>PDF/Foto Cotización adjunta:</strong> ${hasPdf}</div>`;

        let numEvid = fotos.files ? fotos.files.length : 0;
        if (numEvid > 0) {
            seccion2HTML += `<div class="pdf-line" style="margin-top:10px;"><strong>Fotos de Evidencia adjuntas:</strong></div>`;
            seccion2HTML += `<div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:5px;">`;
            for (let j = 0; j < numEvid; j++) {
                let url = URL.createObjectURL(fotos.files[j]);
                seccion2HTML += `<img src="${url}" style="width:120px; height:120px; object-fit:cover; border-radius:8px; border:1px solid #0284c7;">`;
            }
            seccion2HTML += `</div>`;
        } else {
            seccion2HTML += `<div class="pdf-line" style="margin-top:10px;"><strong>Fotos de Evidencia adjuntas:</strong> 0 fotos</div>`;
        }
        seccion2HTML += `</div>`;
    }

    seccion2HTML += `</div>`; // Cerrar el div principal de la seccion 2

    // Injectar en el PDF modal
    let wrapper = document.getElementById('prev-pdf-sec2-wrapper');
    if (!wrapper) {
        // Encontraremos la seccion 2 y la reemplazaremos por un div wrapper
        let container = document.querySelector('#hoja-factura-pdf > div:nth-child(3)'); // la seccion 2 anterior
        if (container) {
            container.innerHTML = `<div id="prev-pdf-sec2-wrapper">${seccion2HTML}</div>`;
        }
    } else {
        wrapper.innerHTML = seccion2HTML;
    }

    let numReporte = '';
    if (document.getElementById('hidden_numero_reporte')) numReporte = document.getElementById('hidden_numero_reporte').value;
    if (numReporte && numReporte !== "" && document.getElementById('pdf-seccion-reporte')) {
        let r = reportesGlobal.find(x => String(x.id) === String(numReporte)) || reporteSeleccionado;
        if (r) {
            document.getElementById('pdf-seccion-reporte').style.display = 'block';
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "No proporcionado";
            document.getElementById('prev-rep-ticket').innerText = r.id;
            document.getElementById('prev-rep-fecha').innerText = r.fecha;
            document.getElementById('prev-rep-unidad').innerText = "8090-" + r.unidad;
            document.getElementById('prev-rep-marca').innerText = r.marca + " " + r.modelo;
            document.getElementById('prev-rep-mantenimiento').innerText = r.mantenimiento;
            document.getElementById('prev-rep-empleado').innerText = r.empleado;
            document.getElementById('prev-rep-celular').innerText = r.celular;
            document.getElementById('prev-rep-email').innerText = emailStatus;
            document.getElementById('prev-rep-depto').innerText = r.departamento;
            document.getElementById('prev-rep-km').innerText = r.kilometraje;
            document.getElementById('prev-rep-falla').innerText = r.falla;

            if (r.firma_chofer && document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'block';
                document.getElementById('prev-rep-firma-img').src = r.firma_chofer;
            } else if (document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'none';
            }
        }
    } else {
        if (document.getElementById('pdf-seccion-reporte')) document.getElementById('pdf-seccion-reporte').style.display = 'none';
    }

    document.getElementById('modal-nueva-factura').style.display = 'none';
    document.getElementById('modal-previsualizacion-factura').style.display = 'flex';
}

function volverAEditar() { document.getElementById('modal-previsualizacion-factura').style.display = 'none'; document.getElementById('modal-nueva-factura').style.display = 'flex'; }

function generarHtmlDetalles(f, modo, precioBonito) {
    let rolUsuario = document.getElementById('rol-actual') ? document.getElementById('rol-actual').value : '';
    let htmlReporte = '';

    // Buscar id de reporte en retro principal O en retro de la primera cotizacion
    let idReporte = obtenerIdReporte(f);
    if (!idReporte && f.cotizaciones && f.cotizaciones.length > 0) {
        let firstRetro = f.cotizaciones[0].retro || '';
        if (firstRetro.includes('[TICKET:')) {
            let match = firstRetro.match(/\[TICKET:(.*?)\]/);
            if (match && match[1]) idReporte = String(match[1]);
        }
    }

    // SECCION 1: REPORTE DE INCIDENCIA
    if (idReporte) {
        let r = reportesGlobal.find(x => String(x.id) === String(idReporte));
        if (r) {
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "<span style='color:#a3b1c6; font-style:italic;'>No proporcionado</span>";
            let ciudadStatus = r.ciudad || "No especificada";
            let copeStatus = r.cope || "No especificado";

            htmlReporte = `
                <div style="margin-bottom: 20px; border: 2px dashed #0284c7; padding: 15px; border-radius: 8px; background-color: #0b1c30;">
                    <div style="color: #0284c7; border-bottom: 1px solid #0284c7; padding-bottom: 5px; margin-bottom: 10px; font-weight: bold; font-size:1.1em;">&#9632; SECCI&Oacute;N 1: REPORTE DE INCIDENCIA (ORIGEN)</div>
                    <div class="form-grid" style="grid-template-columns: 1fr 1fr;">
                        <div class="modal-info-line"><strong>Ticket No.:</strong> <span style="color:#0284c7; font-weight:bold;">${r.id}</span></div>
                        <div class="modal-info-line"><strong>Fecha Reporte:</strong> ${r.fecha}</div>
                        <div class="modal-info-line"><strong>Unidad:</strong> 8090-${r.unidad}</div>
                        ${r.compania ? `<div class="modal-info-line"><strong>Compa&ntilde;&iacute;a:</strong> <span style="color:#10b981; font-weight:bold;">${r.compania}</span></div>` : ''}
                        <div class="modal-info-line"><strong>Marca/Modelo:</strong> ${r.marca} ${r.modelo}</div>
                        <div class="modal-info-line"><strong>Tipo Mantenimiento:</strong> ${r.mantenimiento}</div>
                        <div class="modal-info-line"><strong>Kilometraje:</strong> ${r.kilometraje} km</div>
                        <div class="modal-info-line"><strong>Ciudad / Ubicaci&oacute;n:</strong> <span style="color:#0ea5e9; font-weight:bold;">${ciudadStatus} - ${copeStatus}</span></div>
                        <div class="modal-info-line"><strong>Empleado (Chofer):</strong> ${r.empleado}</div>
                        <div class="modal-info-line"><strong>Depto:</strong> ${r.departamento}</div>
                        <div class="modal-info-line"><strong>Celular:</strong> ${r.celular}</div>
                        <div class="modal-info-line"><strong>Correo:</strong> ${emailStatus}</div>
                        <div class="modal-info-line full-width"><strong>Falla Reportada:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#112641; border-left:3px solid #0284c7; border-radius:5px;">${r.falla}</div></div>
                        ${r.firma_chofer ? `
                        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-top: 15px; margin-bottom: 5px; color: #0284c7;"><strong>&#9997; FIRMA DEL OPERADOR / CHOFER</strong></div>
                        <div class="modal-info-line full-width" style="text-align: center;">
                            <img src="${r.firma_chofer}" alt="Firma del Chofer" style="background: white; border-radius: 8px; max-width: 300px; border: 2px solid #1f395a; padding: 5px;">
                        </div>` : ''}
                    </div>
                </div>
            `;
        }
    }

    let cots = f.cotizaciones || [];
    if (cots.length === 0) {
        cots = [{
            titulo: f.titulo || 'Global',
            mantenimiento: f.mantenimiento || 'General',
            retro: f.retro || '',
            diagnostico: f.diagnostico || '',
            trabajo_realizar: f.trabajo_realizar || '',
            precio: parseFloat(f.precio),
            pdf_cotizacion: f.fotos_cotizacion && f.fotos_cotizacion.length > 0 ? f.fotos_cotizacion[0] : null,
            fotos_evidencia: f.fotos_evidencia || [],
            numero_orden: f.numero_orden,
            numero_cotizacion_asignacion: f.numero_cotizacion_asignacion,
            pdf_orden: f.pdf_cotizacion_asignacion,
            factura_folio: f.factura_folio,
            pdf_fiscal: f.factura_pdf,
            xml_file: f.xml_file,
            numero_doc50: f.numero_doc50,
            pdf_doc50: f.pdf_doc50
        }];
    }

    let multiCot = cots.length > 1;

    let cotizacionesBlocksHtml = cots.map((c, i) => {

        // SECCION 2
        let tituloSec2 = multiCot ? `&#9632; SECCI&Oacute;N 2: DIAGN&Oacute;STICO Y COTIZACI&Oacute;N ${i + 1} (TALLER)` : '&#9632; SECCI&Oacute;N 2: DIAGN&Oacute;STICO Y COTIZACI&Oacute;N (TALLER)';
        let sec2Html = `
        <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #ef4444; border-radius:8px;">
            <div style="color: #ef4444; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloSec2}</div>
            <div class="form-grid" style="grid-template-columns: 1fr 1fr;">
                <div class="modal-info-line"><strong>Proveedor:</strong> ${f.proveedor}</div>
                <div class="modal-info-line"><strong>Fecha Ingreso:</strong> ${f.fecha}</div>
                <div class="modal-info-line"><strong>Unidad:</strong> ${f.unidad}</div>
                ${f.compania ? `<div class="modal-info-line"><strong>Compa&ntilde;&iacute;a:</strong> <span style="color:#10b981; font-weight:bold;">${f.compania}</span></div>` : ''}
                <div class="modal-info-line"><strong>Responsable:</strong> ${f.responsable}</div>
                <div class="modal-info-line"><strong>Mantenimiento:</strong> ${c.mantenimiento || 'General'}</div>
                <div class="modal-info-line"><strong>Precio s/IVA:</strong> $${formatearMoneda(c.precio)}</div>
                <div class="modal-info-line full-width"><strong>T&iacute;tulo:</strong> ${c.titulo || 'Sin T&iacute;tulo'}</div>
                <div class="modal-info-line full-width"><strong>Retro:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${limpiarRetro(c.retro || 'Sin retro')}</div></div>
                <div class="modal-info-line full-width"><strong>Diagn&oacute;stico de Mec&aacute;nico:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${c.diagnostico || 'Sin especificar'}</div></div>
                <div class="modal-info-line full-width"><strong>Descripci&oacute;n del Trabajo a Realizar:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${c.trabajo_realizar || 'Sin especificar'}</div></div>
            </div>
            <div style="margin-top:15px;">
                <strong>Cotización (archivo):</strong><br>
                <div style="display:flex; flex-direction:column; gap:10px; padding:10px 0;">
                    ${c.pdf_cotizacion ? (c.pdf_cotizacion.endsWith('.pdf') ? `<iframe src="/static/facturas_archivos/${c.pdf_cotizacion}" width="100%" height="400px" style="border:1px solid #1f395a; border-radius:8px; background:#fff;"></iframe>` : `<img src="/static/facturas_archivos/${c.pdf_cotizacion}" style="max-width:100%; max-height:400px; border-radius:5px; border:2px solid #eab308; cursor:zoom-in; object-fit:contain;" onclick="abrirLightbox('/static/facturas_archivos/${c.pdf_cotizacion}')">`) : '<span style="color:#9ca3af; font-style:italic;">Sin archivo</span>'}
                </div>
                <strong>Evidencias Fotogr&aacute;ficas:</strong><br>
                <div style="display:flex; gap:10px; overflow-x:auto; padding:10px 0;">
                    ${(c.fotos_evidencia || []).map(foto => `<img src="/static/facturas_archivos/${foto}" style="height:70px; border-radius:5px; border:2px solid #eab308; cursor:zoom-in;" onclick="abrirLightbox('/static/facturas_archivos/${foto}')">`).join('')}
                    ${!(c.fotos_evidencia && c.fotos_evidencia.length > 0) ? '<span style="color:#9ca3af; font-style:italic;">Sin evidencias adjuntas.</span>' : ''}
                </div>
            </div>
        </div>
        `;

        // SECCION 3
        let sec3Html = '';
        let numOrd = c.numero_orden;
        let numCot = c.numero_cotizacion_asignacion;
        let pdfOrd = c.pdf_orden || c.pdf_cotizacion_asignacion;
        if (modo === 'lectura' && (numOrd || pdfOrd)) {
            let tituloSec3 = multiCot ? `&#9632; SECCI&Oacute;N 3: ORDEN DE PEDIDO ${i + 1} (ADMINISTRACI&Oacute;N)` : '&#9632; SECCI&Oacute;N 3: ORDEN DE PEDIDO (ADMINISTRACI&Oacute;N)';
            sec3Html = `
            <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #374151; border-radius:8px;">
                <div style="color: #9ca3af; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloSec3}</div>
                <div class="modal-info-line" style="font-size:16px;"><strong>N&uacute;m. Orden de Trabajo:</strong> <span style="color:#9ca3af; font-weight:bold;">${numOrd || 'Pendiente'}</span></div>
                ${numCot ? `<div class="modal-info-line" style="font-size:16px; margin-top:10px;"><strong>No. de Solicitud de Pedido:</strong> <span style="color:#9ca3af; font-weight:bold;">${numCot}</span></div>` : ''}
                ${pdfOrd ? `<div style="margin-top:15px;"><button type="button" class="btn-success-modal" style="background:#000000; border:1px solid #374151; padding:10px 20px; border-radius:8px; color:#ffffff; font-weight:bold; cursor:pointer;" onclick="abrirVisorPDF('/static/facturas_archivos/${pdfOrd}')">&#128196; Ver Solicitud de Pedido / Orden</button></div>` : ''}
            </div>
            `;
        }

        // SECCION 4
        let sec4Html = '';
        let fFolio = c.factura_folio;
        let pdfFiscal = c.pdf_fiscal || c.factura_pdf;
        let xmlFile = c.xml_file;
        if (fFolio || pdfFiscal) {
            let tituloSec4 = multiCot ? `&#9632; SECCI&Oacute;N 4: CIERRE CONTABLE ${i + 1} (FACTURA FISCAL)` : '&#9632; SECCI&Oacute;N 4: CIERRE CONTABLE (FACTURA FISCAL)';
            sec4Html = `
            <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #10b981; border-radius:8px;">
                <div style="color: #10b981; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloSec4}</div>
                <div class="modal-info-line" style="font-size:16px;"><strong>Folio Fiscal Emitido:</strong> <span style="color:#10b981; font-weight:bold;">${fFolio || 'Pendiente'}</span></div>
                <div style="margin-top:15px; display:flex; gap:10px;">
                    ${pdfFiscal ? `<button type="button" class="btn-success-modal" style="background:#10b981; border:none; padding:10px 20px; border-radius:8px; color:white; font-weight:bold; cursor:pointer;" onclick="abrirVisorPDF('/static/facturas_archivos/${pdfFiscal}')">&#128196; Ver PDF Oficial</button>` : ''}
                    ${xmlFile ? `<button type="button" class="btn-success-modal" style="background:#10b981; border:none; padding:10px 20px; border-radius:8px; color:white; font-weight:bold; cursor:pointer;" onclick="descargarArchivo('/static/facturas_archivos/${xmlFile}')">&#128190; Descargar XML</button>` : ''}
                </div>
            </div>
            `;
        }

        // SECCION 5
        let sec5Html = '';
        let numDoc50 = c.numero_doc50;
        let pdfDoc50 = c.pdf_doc50;
        if (rolUsuario !== 'proveedores' && (numDoc50 || pdfDoc50)) {
            let tituloSec5 = multiCot ? `&#9632; SECCI&Oacute;N 5: N&Uacute;MERO DE DOCUMENTO CONTABLE ${i + 1} Y ARCHIVADO` : '&#9632; SECCI&Oacute;N 5: N&Uacute;MERO DE DOCUMENTO CONTABLE Y ARCHIVADO';
            sec5Html = `
            <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #eab308; border-radius:8px;">
                <div style="color: #eab308; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloSec5}</div>
                <div class="modal-info-line" style="font-size:16px;"><strong>N&uacute;mero de Documento:</strong> <span style="color:#eab308; font-weight:bold;">${numDoc50 || 'Pendiente'}</span></div>
                <div style="margin-top:15px;">
                    ${pdfDoc50 ? `<button type="button" class="btn-success-modal" style="background:#ef4444; border:none; padding:10px 20px; border-radius:8px; color:#ffffff; font-weight:bold; cursor:pointer;" onclick="abrirVisorPDF('/static/facturas_archivos/${pdfDoc50}')">&#128196; Ver Documento Contable</button>` : ''}
                </div>
            </div>
            `;
        }

        return `${sec2Html}${sec3Html}${sec4Html}${sec5Html}`;
    }).join('');

    return `
        ${htmlReporte}
        ${cotizacionesBlocksHtml}
    `;
}

function abrirRevisionAdmin(idFactura) {
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura));
    if (!f) return;
    document.getElementById('rev-id-admin').value = f.id;
    document.getElementById('revision-contenido-admin').innerHTML = generarHtmlDetalles(f, 'edicion', formatearMoneda(f.precio));

    let container = document.getElementById('revision-inputs-admin-container');
    if (container) {
        let inputsHtml = '';
        let cots = f.cotizaciones || [{ precio: f.precio }];
        cots.forEach((cot, idx) => {
            inputsHtml += `
                <div class="cotizacion-admin-row" data-idx="${idx}" style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #1f395a;">
                    <h4 style="color:#0ea5e9; margin-bottom:10px;">Cotización ${idx + 1}: ${cot.titulo || 'Sin Título'} ($${formatearMoneda(cot.precio)})</h4>
                    
                    <label style="color:#40916c; font-weight:bold; display:block; margin-bottom:5px;">Asignar Número de Orden</label>
                    <input type="text" class="input-num-orden-multi" placeholder="Escribe el número de orden..." oninput="validarOrden()" style="width: 100%; padding: 10px; border-radius: 8px; margin-bottom:10px;">
                    
                    <label style="color:#40916c; font-weight:bold; display:block; margin-bottom:5px;">Solicitud de Pedido</label>
                    <input type="text" class="input-cotizacion-admin-multi" placeholder="Escriba el número aquí..." oninput="validarOrden()" style="width: 100%; padding: 10px; background: #0b1c30; color: white; border: 1px solid #1f395a; border-radius: 8px; margin-bottom:10px;">
                    
                    <label style="color:#0ea5e9; font-weight:600; margin-bottom:5px; display:block;">Subir PDF de Orden de Pedido:</label>
                    <input type="file" class="input-pdf-admin-multi" accept=".pdf" onchange="previsualizarPDFOrden(this, ${idx})" style="width: 100%; padding: 10px; background: #0b1c30; color: white; border: 1px solid #1f395a; border-radius: 8px;">
                    <div id="preview-pdf-orden-${idx}" style="margin-top:10px; display:none;">
                        <iframe id="iframe-pdf-orden-${idx}" width="100%" height="400px" style="border:1px solid #1f395a; border-radius:8px; background:#fff;"></iframe>
                    </div>
                </div>
            `;
        });
        container.innerHTML = inputsHtml;
    }

    validarOrden();
    document.getElementById('modal-revision-admin').style.display = 'flex';
}

function previsualizarPDFOrden(input, idx) {
    let previewDiv = document.getElementById(`preview-pdf-orden-${idx}`);
    let iframe = document.getElementById(`iframe-pdf-orden-${idx}`);
    if (input.files && input.files[0] && input.files[0].type === "application/pdf") {
        let url = URL.createObjectURL(input.files[0]);
        iframe.src = url;
        previewDiv.style.display = 'block';
    } else {
        iframe.src = '';
        previewDiv.style.display = 'none';
    }
    validarOrden();
}

function validarOrden() {
    let btn = document.getElementById('btn-confirmar-admin');
    let rows = document.querySelectorAll('.cotizacion-admin-row');

    if (rows.length === 0) return;

    let allValid = true;
    rows.forEach(row => {
        let numOrd = row.querySelector('.input-num-orden-multi').value.trim();
        let numCot = row.querySelector('.input-cotizacion-admin-multi').value.trim();
        let pdf = row.querySelector('.input-pdf-admin-multi').files[0];
        if (numOrd.length === 0 || numCot.length === 0 || !pdf) {
            allValid = false;
        }
    });

    if (allValid) {
        btn.disabled = false; btn.style.opacity = '1'; btn.style.cursor = 'pointer';
    } else {
        btn.disabled = true; btn.style.opacity = '0.5'; btn.style.cursor = 'not-allowed';
    }
}

function confirmarFacturaAdmin() {
    let id_fac = document.getElementById('rev-id-admin').value;
    let rows = document.querySelectorAll('.cotizacion-admin-row');

    if (rows.length === 0) return;
    if (!confirm(`¿Asignar las órdenes para todas las cotizaciones de este ticket?`)) return;

    mostrarLoaderDinamico("Validando órdenes...", "Generando código oficial ⏳");

    let formData = new FormData();
    formData.append('id', id_fac);

    rows.forEach((row, idx) => {
        formData.append('numero_orden[]', row.querySelector('.input-num-orden-multi').value.trim());
        formData.append('numero_cotizacion[]', row.querySelector('.input-cotizacion-admin-multi').value.trim());
        let pdf = row.querySelector('.input-pdf-admin-multi').files[0];
        if (pdf) {
            formData.append('pdf_orden[]', pdf);
        } else {
            formData.append('pdf_orden[]', new Blob([]), "vacio.pdf"); // Empty blob to keep arrays synced
        }
    });

    fetch('/api/facturas/confirmar_admin', {
        method: 'POST',
        body: formData
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        document.getElementById('modal-revision-admin').style.display = 'none';
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirRevisionCorp(idFactura) { const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if (!f) return; document.getElementById('rev-id-corp').value = f.id; document.getElementById('revision-contenido-corp').innerHTML = generarHtmlDetalles(f, 'lectura', formatearMoneda(f.precio)); document.getElementById('modal-revision-corp').style.display = 'flex'; }

function confirmarFacturaCorp() {
    let id_fac = document.getElementById('rev-id-corp').value;
    if (!confirm(`¿¿Aprobar financieramente esta factura mayor?`)) return;

    mostrarLoaderDinamico("Aprobando factura mayor...", "Generando código oficial 📧");

    fetch('/api/facturas/confirmar_corp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id_fac })
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        document.getElementById('modal-revision-corp').style.display = 'none';
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirModalRechazoCorp(inputId) {
    let id_fac = document.getElementById(inputId).value;
    const f = facturasGlobal.find(x => String(x.id) === String(id_fac)); 
    if (!f) return;
    
    document.getElementById('modal-revision-corp').style.display = 'none'; 
    document.getElementById('rechazo-corp-id').value = f.id;
    
    let html = `<div style="color: #94a3b8; margin-bottom:15px; font-size:14px;">Ingresa el precio recomendado para cada cotización (opcional) y el motivo general del rechazo.</div>`;
    
    f.cotizaciones.forEach((c, idx) => {
        let precioActual = formatearMoneda(c.precio);
        let titulo = c.titulo || 'Sin Título';
        html += `
        <div style="margin-bottom:15px; padding:15px; background:#1e293b; border:1px solid #334155; border-radius:8px;">
            <div style="font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Cotización ${idx + 1}: ${titulo}</div>
            <div style="font-size:13px; color:#94a3b8; margin-bottom:10px;">Precio cotizado: <span style="font-weight:bold; color:#f59e0b;">${precioActual}</span></div>
            <label style="display:block; font-size:13px; color:#cbd5e1; margin-bottom:5px;">Precio Recomendado ($):</label>
            <input type="number" class="input-precio-rec-corp" data-idx="${idx}" placeholder="Ej. 1500" style="width:100%; padding:8px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;">
        </div>
        `;
    });
    
    html += `
    <div style="margin-top:20px;">
        <label style="display:block; font-size:14px; font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Motivo General del Rechazo: <span style="color:#ef4444;">*</span></label>
        <textarea id="rechazo-corp-motivo" rows="4" placeholder="Escribe aquí el motivo del rechazo y las observaciones generales..." style="width:100%; padding:10px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;"></textarea>
    </div>
    `;
    
    document.getElementById('contenido-rechazo-corp').innerHTML = html;
    document.getElementById('modal-rechazo-corp-dinamico').style.display = 'flex';
}

function enviarRechazoCorp() {
    let id_fac = document.getElementById('rechazo-corp-id').value;
    let motivo = document.getElementById('rechazo-corp-motivo').value.trim();
    if (!motivo) { alert("Debes escribir el motivo general del rechazo."); return; }
    
    let preciosRec = [];
    document.querySelectorAll('.input-precio-rec-corp').forEach(input => {
        preciosRec.push({
            idx: input.getAttribute('data-idx'),
            precio_recomendado: input.value.trim()
        });
    });
    
    if (!confirm("¿Estás seguro de rechazar el gasto y enviar las recomendaciones? El ticket será eliminado de tu bandeja.")) return;
    
    mostrarLoaderDinamico("Procesando rechazo...", "Enviando notificaciones 📧");
    
    fetch('/api/facturas/rechazar_corp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: id_fac,
            motivo: motivo,
            precios_recomendados: preciosRec
        })
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        document.getElementById('modal-rechazo-corp-dinamico').style.display = 'none';
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirDetalles(idFactura) {
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if (!f) return;
    document.getElementById('detalles-contenido').innerHTML = generarHtmlDetalles(f, 'lectura', formatearMoneda(f.precio));
    document.getElementById('btn-descargar-pdf').onclick = () => generarPDFSilencioso(f.id);
    document.getElementById('modal-detalles-general').style.display = 'flex';
}

function generarPDFSilencioso(idFactura) {
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if (!f) return;
    let idReporte = obtenerIdReporte(f);

    if (idReporte && document.getElementById('pdf-seccion-reporte')) {
        let r = reportesGlobal.find(x => String(x.id) === String(idReporte));
        if (r) {
            document.getElementById('pdf-seccion-reporte').style.display = 'block';
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "No proporcionado";
            document.getElementById('prev-rep-ticket').innerText = r.id;
            document.getElementById('prev-rep-fecha').innerText = r.fecha;
            document.getElementById('prev-rep-unidad').innerText = "8090-" + r.unidad;
            document.getElementById('prev-rep-marca').innerText = r.marca + " " + r.modelo;
            document.getElementById('prev-rep-mantenimiento').innerText = r.mantenimiento;
            document.getElementById('prev-rep-empleado').innerText = r.empleado;
            document.getElementById('prev-rep-celular').innerText = r.celular;
            document.getElementById('prev-rep-email').innerText = emailStatus;
            document.getElementById('prev-rep-depto').innerText = r.departamento;
            document.getElementById('prev-rep-km').innerText = r.kilometraje;

            let ciudadStatus = r.ciudad || "No especificada";
            let copeStatus = r.cope || "No especificado";
            if (document.getElementById('prev-rep-ciudad')) {
                document.getElementById('prev-rep-ciudad').innerText = `${ciudadStatus} - ${copeStatus}`;
            }

            if (r.numero_cotizacion_asignacion && document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'block';
                document.getElementById('prev-rep-cotizacion').innerText = r.numero_cotizacion_asignacion;
            } else if (document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'none';
            }

            document.getElementById('prev-rep-falla').innerText = r.falla;

            if (r.firma_chofer) {
                document.getElementById('prev-rep-firma-container').style.display = 'block';
                document.getElementById('prev-rep-firma-img').src = r.firma_chofer;
            } else {
                if (document.getElementById('prev-rep-firma-container')) {
                    document.getElementById('prev-rep-firma-container').style.display = 'none';
                }
            }
        }
    } else if (document.getElementById('pdf-seccion-reporte')) {
        document.getElementById('pdf-seccion-reporte').style.display = 'none';
    }

    let cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [{
        titulo: f.titulo, retro: f.retro, diagnostico: f.diagnostico, trabajo_realizar: f.trabajo_realizar,
        mantenimiento: f.mantenimiento, precio: f.precio, pdf_cotizacion: f.pdf_cotizacion || (f.fotos_cotizacion && f.fotos_cotizacion.length > 0 ? f.fotos_cotizacion[0] : null), fotos_evidencia: f.fotos_evidencia || []
    }];

    let cotDinamicas = document.getElementById('pdf-cotizaciones-dinamicas');
    if (cotDinamicas) {
        cotDinamicas.innerHTML = '';
        let multiCot = cots.length > 1;
        cots.forEach((c, idx) => {
            let tituloGlobalText = multiCot ? `■ SECCIÓN 2: DIAGNÓSTICO Y COTIZACIÓN ${idx + 1}` : '■ SECCIÓN 2: DIAGNÓSTICO Y COTIZACIÓN';

            let evHTML = '';
            if (c.fotos_evidencia && c.fotos_evidencia.length > 0) {
                c.fotos_evidencia.forEach(foto => {
                    evHTML += `<div class="pdf-image-container"><img src="/static/facturas_archivos/${foto}" class="pdf-anexo-img"><p class="pdf-anexo-label" style="word-break: break-all;">Evidencia: ${foto}</p></div>`;
                });
            } else {
                evHTML = `<div style="color:#9ca3af; font-style:italic;">Sin evidencias</div>`;
            }

            let cotHTML = '';
            let fotoCot = c.pdf_cotizacion;
            if (fotoCot) {
                if (fotoCot.endsWith('.pdf')) {
                    cotHTML = `<div class="pdf-image-container"><div style="font-size:40px; color:#ef4444; margin-bottom:10px;">📄</div><p class="pdf-anexo-label" style="word-break: break-all;">Cotización PDF: ${fotoCot}</p></div>`;
                } else {
                    cotHTML = `<div class="pdf-image-container"><img src="/static/facturas_archivos/${fotoCot}" class="pdf-anexo-img"><p class="pdf-anexo-label" style="word-break: break-all;">Cotización: ${fotoCot}</p></div>`;
                }
            } else {
                cotHTML = `<div style="color:#9ca3af; font-style:italic;">Sin documento</div>`;
            }

            cotDinamicas.innerHTML += `
            <div style="margin-bottom: 20px; border: 2px dashed #0284c7; padding: 15px; border-radius: 8px; background-color: #fafafa; page-break-inside: avoid;">
                <div class="pdf-section-title" style="color: #0284c7; border-bottom: 1px solid #0284c7; padding-bottom: 5px;">${tituloGlobalText}</div>
                <div class="pdf-line"><strong>Unidad:</strong> <span>${f.unidad}</span></div>
                <div class="pdf-line"><strong>Responsable:</strong> <span>${f.responsable}</span></div>
                <div class="pdf-line"><strong>Teléfono:</strong> <span>${f.telefono}</span></div>
                <div class="pdf-line"><strong>Fecha:</strong> <span>${f.fecha}</span></div>
                <div class="pdf-line"><strong>Tipo de Mantenimiento:</strong> <span>${c.mantenimiento || 'General'}</span></div>
                <div class="pdf-line" style="margin-bottom: 15px;"><strong>Precio (Sin IVA):</strong> <span>${formatearMoneda(c.precio)}</span></div>
                
                <div class="pdf-section-title" style="color: #0284c7;">■ DETALLES DEL TRABAJO</div>
                <div class="pdf-line"><strong>Título:</strong> <span class="texto-largo">${c.titulo || 'Sin Título'}</span></div>
                <div class="pdf-line"><strong>Retro:</strong> <div class="texto-largo" style="margin-top: 5px; padding: 10px; background: #f9f9f9; border-left: 3px solid #0284c7;">${limpiarRetro(c.retro || 'Sin retro')}</div></div>
                <div class="pdf-line"><strong>Diagnóstico de Mecánico:</strong> <div class="texto-largo" style="margin-top: 5px; padding: 10px; background: #f9f9f9; border-left: 3px solid #0284c7;">${c.diagnostico || 'Sin especificar'}</div></div>
                <div class="pdf-line" style="margin-bottom: 15px;"><strong>Descripción del Trabajo a Realizar:</strong> <div class="texto-largo" style="margin-top: 5px; padding: 10px; background: #f9f9f9; border-left: 3px solid #0284c7;">${c.trabajo_realizar || 'Sin especificar'}</div></div>
                
                <div class="pdf-section-title" style="color: #0284c7;">■ DOCUMENTOS DE COTIZACIÓN</div>
                <div style="display: flex; flex-direction: column; align-items: center; margin-top: 15px; margin-bottom: 15px;">${cotHTML}</div>
                
                <div class="pdf-section-title" style="color: #0284c7;">■ ANEXO FOTOGRÁFICO (EVIDENCIAS)</div>
                <div style="display: flex; flex-direction: column; align-items: center; margin-top: 15px;">${evHTML}</div>
            </div>
            `;
        });

        let adminSeccionHTML = '';
        let hasAdminData = false;
        cots.forEach((c, idx) => {
            let numOrd = c.numero_orden;
            let numCot = c.numero_cotizacion_asignacion;
            let pdfOrd = c.pdf_orden || c.pdf_cotizacion_asignacion;
            
            if (numOrd || pdfOrd) {
                hasAdminData = true;
                let tituloAdmin = multiCot ? `ORDEN DE PEDIDO ${idx + 1}` : 'ORDEN DE PEDIDO';
                adminSeccionHTML += `
                <div style="margin-top:15px; border-top: 1px dashed #374151; padding-top:10px;">
                    <div style="color: #374151; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloAdmin}</div>
                    <div class="pdf-line"><strong>N&uacute;m. Orden de Trabajo:</strong> <span>${numOrd || 'Pendiente'}</span></div>
                    ${numCot ? `<div class="pdf-line"><strong>No. de Solicitud de Pedido:</strong> <span>${numCot}</span></div>` : ''}
                    <div class="pdf-line"><strong>PDF Orden de Pedido:</strong> <span style="word-break: break-all;">${pdfOrd || 'Sin documento'}</span></div>
                </div>
                `;
            }
        });

        if (hasAdminData) {
            cotDinamicas.innerHTML += `
            <div style="margin-bottom: 20px; border: 2px dashed #374151; padding: 15px; border-radius: 8px; background-color: #f3f4f6; page-break-inside: avoid;">
                <div class="pdf-section-title" style="color: #374151; border-bottom: 1px solid #374151; padding-bottom: 5px;">■ SECCIÓN 3: ÓRDENES DE PEDIDO (ADMINISTRACIÓN)</div>
                ${adminSeccionHTML}
            </div>
            `;
        }

        // SECCION 4: FACTURA FISCAL
        let fiscalSeccionHTML = '';
        let hasFiscalData = false;
        cots.forEach((c, idx) => {
            let fFolio = c.factura_folio;
            let pdfFiscal = c.pdf_fiscal || c.factura_pdf;
            let xmlFile = c.xml_file;
            
            if (fFolio || pdfFiscal) {
                hasFiscalData = true;
                let tituloFiscal = multiCot ? `FACTURA FISCAL ${idx + 1}` : 'FACTURA FISCAL';
                fiscalSeccionHTML += `
                <div style="margin-top:15px; border-top: 1px dashed #10b981; padding-top:10px;">
                    <div style="color: #10b981; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloFiscal}</div>
                    <div class="pdf-line"><strong>Folio Fiscal Emitido:</strong> <span>${fFolio || 'Pendiente'}</span></div>
                    <div class="pdf-line"><strong>PDF Oficial:</strong> <span style="word-break: break-all;">${pdfFiscal || 'Sin documento'}</span></div>
                    ${xmlFile ? `<div class="pdf-line"><strong>XML:</strong> <span style="word-break: break-all;">${xmlFile}</span></div>` : ''}
                </div>
                `;
            }
        });

        if (hasFiscalData) {
            cotDinamicas.innerHTML += `
            <div style="margin-bottom: 20px; border: 2px dashed #10b981; padding: 15px; border-radius: 8px; background-color: #ecfdf5; page-break-inside: avoid;">
                <div class="pdf-section-title" style="color: #10b981; border-bottom: 1px solid #10b981; padding-bottom: 5px;">■ SECCIÓN 4: CIERRE CONTABLE (FACTURA FISCAL)</div>
                ${fiscalSeccionHTML}
            </div>
            `;
        }

        // SECCION 5: DOC CONTABLE
        let doc50SeccionHTML = '';
        let hasDoc50Data = false;
        cots.forEach((c, idx) => {
            let numDoc50 = c.numero_doc50;
            let pdfDoc50 = c.pdf_doc50;
            
            if (numDoc50) {
                hasDoc50Data = true;
                let tituloDoc = multiCot ? `DOCUMENTO CONTABLE ${idx + 1}` : 'DOCUMENTO CONTABLE';
                doc50SeccionHTML += `
                <div style="margin-top:15px; border-top: 1px dashed #eab308; padding-top:10px;">
                    <div style="color: #eab308; font-weight: bold; font-size:1.1em; margin-bottom:10px;">${tituloDoc}</div>
                    <div class="pdf-line"><strong>N&uacute;mero de Documento:</strong> <span>${numDoc50 || 'Pendiente'}</span></div>
                </div>
                `;
            }
        });

        if (hasDoc50Data) {
            cotDinamicas.innerHTML += `
            <div style="margin-bottom: 20px; border: 2px dashed #eab308; padding: 15px; border-radius: 8px; background-color: #fefce8; page-break-inside: avoid;">
                <div class="pdf-section-title" style="color: #eab308; border-bottom: 1px solid #eab308; padding-bottom: 5px;">■ SECCIÓN 5: NÚMERO DE DOCUMENTO CONTABLE Y ARCHIVADO</div>
                ${doc50SeccionHTML}
            </div>
            `;
        }
    }

    const overlay = document.createElement('div'); overlay.style.position = 'fixed'; overlay.style.top = '0'; overlay.style.left = '0'; overlay.style.width = '100vw'; overlay.style.height = '100vh'; overlay.style.backgroundColor = 'rgba(11, 28, 48, 0.95)'; overlay.style.zIndex = '999999'; overlay.style.display = 'flex'; overlay.style.flexDirection = 'column'; overlay.style.alignItems = 'center'; overlay.style.overflowY = 'auto'; overlay.style.padding = '40px 0';
    const titleText = document.createElement('h2'); titleText.innerText = "Vista Previa del Documento Oficial"; titleText.style.color = '#40916c'; titleText.style.marginBottom = '20px'; titleText.style.fontFamily = "'Poppins', sans-serif"; overlay.appendChild(titleText);
    const elementoOriginal = document.getElementById('hoja-factura-pdf'); let clon = elementoOriginal.cloneNode(true); clon.id = "clon-pdf-visible"; clon.style.display = 'block'; overlay.appendChild(clon);
    const btnContainer = document.createElement('div'); btnContainer.style.display = 'flex'; btnContainer.style.gap = '20px'; btnContainer.style.marginTop = '25px'; btnContainer.style.marginBottom = '40px';
    const btnCancelar = document.createElement('button'); btnCancelar.innerText = "Cancelar"; btnCancelar.className = "btn-danger"; btnCancelar.style.padding = '12px 24px'; btnCancelar.onclick = () => { document.body.removeChild(overlay); };
    const btnDescargar = document.createElement('button'); btnDescargar.innerText = "Confirmar y Descargar PDF"; btnDescargar.className = "btn-success-modal"; btnDescargar.style.padding = '12px 24px'; btnDescargar.onclick = () => {
        btnDescargar.innerText = "Generando PDF..."; btnDescargar.disabled = true; btnDescargar.style.opacity = '0.7';
        const opciones = { margin: 0.4, filename: `Factura_${f.unidad}_${f.fecha}.pdf`, image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } };
        html2pdf().set(opciones).from(clon).save().then(() => { document.body.removeChild(overlay); });
    };
    btnContainer.appendChild(btnCancelar); btnContainer.appendChild(btnDescargar); overlay.appendChild(btnContainer); document.body.appendChild(overlay);
}

function generarHtmlReporteEnriquecido(r) {
    let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "<span style='color:#a3b1c6; font-style:italic;'>No proporcionado</span>";
    let ciudadStatus = r.ciudad || "No especificada";
    let copeStatus = r.cope || "No especificado";

    return `
    <div class="form-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 20px; text-align: left;">
        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-bottom: 5px; color: #40916c;"><strong>■ DATOS TÉCNICOS DEL VEHÍCULO</strong></div>
        <div class="modal-info-line"><strong>Ticket No.:</strong> <span style="color:#f59e0b; font-weight:bold; font-size:1.1em;">${r.id}</span></div>
        <div class="modal-info-line"><strong>Fecha del Reporte:</strong> ${r.fecha}</div>
        <div class="modal-info-line"><strong>Unidad:</strong> 8090-${r.unidad}</div>
        ${r.compania ? `<div class="modal-info-line"><strong>Compañía:</strong> <span style="color:#10b981; font-weight:bold;">${r.compania}</span></div>` : ''}
        ${r.numero_cotizacion_asignacion ? `<div class="modal-info-line"><strong>No. de Solicitud de Pedido:</strong> <span>${r.numero_cotizacion_asignacion}</span></div>` : ''}
        ${r.pdf_cotizacion_asignacion ? `<div class="modal-info-line"><strong>PDF de Solicitud de Pedido:</strong> <a href="/static/facturas_archivos/${r.pdf_cotizacion_asignacion}" target="_blank" style="color:#ef4444; font-weight:bold; text-decoration:none;">📄 Ver Documento</a></div>` : ''}
        <div class="modal-info-line"><strong>Kilometraje:</strong> ${r.kilometraje} km</div>
        <div class="modal-info-line"><strong>Marca y Modelo:</strong> ${r.marca} ${r.modelo}</div>
        <div class="modal-info-line"><strong>Tipo Mantenimiento:</strong> ${r.mantenimiento}</div>
        <div class="modal-info-line"><strong>Ciudad / Ubicación:</strong> <span style="color:#0ea5e9; font-weight:bold;">${ciudadStatus} - ${copeStatus}</span></div>
        
        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-top: 15px; margin-bottom: 5px; color: #0284c7;"><strong>■ INFORMACIÓN DE CONTACTO DEL OPERADOR</strong></div>
        <div class="modal-info-line"><strong>Nombre Completo:</strong> ${r.empleado}</div>
        <div class="modal-info-line"><strong>Departamento:</strong> ${r.departamento}</div>
        <div class="modal-info-line"><strong>Celular:</strong> ${r.celular}</div>
        <div class="modal-info-line"><strong>Correo Electrónico:</strong> ${emailStatus}</div>
        
        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-top: 15px; margin-bottom: 5px; color: #f59e0b;"><strong>■ DESCRIPCIÓN DEL INCIDENTE</strong></div>
        <div class="modal-info-line full-width"><div class="texto-largo" style="margin-top:5px; padding:15px; background:#1b4332; border-radius:5px; font-style: italic;">"${r.falla}"</div></div>
        
        ${r.firma_chofer ? `
        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-top: 15px; margin-bottom: 5px; color: #10b981;"><strong>■ ✍ FIRMA DEL OPERADOR / CHOFER</strong></div>
        <div class="modal-info-line full-width" style="text-align: center;">
            <img src="${r.firma_chofer}" alt="Firma del Chofer" style="background: white; border-radius: 8px; max-width: 300px; border: 2px solid #1f395a; padding: 5px;">
        </div>` : ''}
    </div>`;
}

async function cargarReportesAdmin() {
    try {
        const resFac = await fetch('/api/facturas/lista');
        const dataFac = await resFac.json();
        facturasGlobal = dataFac.facturas || [];

        // POLYFILL para múltiples cotizaciones (el título global ya no existe)
        facturasGlobal.forEach(f => {
            if (!f.titulo && f.cotizaciones && f.cotizaciones.length > 0) {
                f.titulo = f.cotizaciones.length > 1 ? f.cotizaciones[0].titulo + " (+" + (f.cotizaciones.length - 1) + " más)" : f.cotizaciones[0].titulo;
                f.mantenimiento = f.cotizaciones[0].mantenimiento;
            }
        });

        const resRep = await fetch('/api/reportes/lista');
        const dataRep = await resRep.json();
        let todosReportes = dataRep.reportes || [];

        const tbody = document.getElementById('tabla-reportes'); if (!tbody) return;
        tbody.innerHTML = '';

        let reportesNoFacturados = todosReportes.filter(r => {
            let yaFacturado = facturasGlobal.some(f => obtenerIdReporte(f) === String(r.id));
            return !yaFacturado;
        });

        reportesGlobal = todosReportes;

        if (reportesNoFacturados.length === 0) { tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No hay reportes ni tickets de mantenimiento pendientes</td></tr>'; return; }

        reportesNoFacturados.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        reportesNoFacturados.forEach(r => {
            let badgeColor = r.estado === 'Pendiente de Revisión' ? '#b45309' : '#2d6a4f';
            let estadoBadge = `<span style="background:${badgeColor}; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">${r.estado}</span>`;
            let btnAsignar = r.estado === 'Pendiente de Revisión' ? `<button class="btn-success" onclick="abrirAsignacionReporte('${r.id}')">Asignar a Taller</button>` : `<button class="btn-info" onclick="abrirAsignacionReporte('${r.id}')">Ver Asignación</button>`;
            let btnAccion = `<div style="display:flex; gap:5px;">${btnAsignar}<button class="btn-danger-sm" onclick="eliminarReporteDefinitivo('${r.id}')">Eliminar</button></div>`;

            let ciaBadge = r.compania ? `Cia: <strong>${r.compania}</strong> | ` : ``;
            let tdUnidadChofer = `<td>8090-${r.unidad}<br><small style="color:#a3b1c6;">${ciaBadge}Op: ${r.empleado}</small></td>`;

            tbody.innerHTML += `<tr><td><strong>${r.id}</strong></td><td>${r.fecha}</td>${tdUnidadChofer}<td>${r.falla.substring(0, 30)}...</td><td>${r.mantenimiento}</td><td>${estadoBadge}</td><td>${btnAccion}</td></tr>`;
        });
    } catch (err) { console.error(err); }
}

function renderizarListaFlotante(proveedores) {
    const contenedor = document.getElementById('lista-proveedores-flotante');
    if (!contenedor) return;
    contenedor.innerHTML = '';
    if (proveedores.length === 0) {
        contenedor.innerHTML = '<div class="lista-flotante-item" style="color:#a3b1c6; cursor:default;">No hay coincidencias con tu búsqueda</div>';
        return;
    }
    proveedores.forEach(p => {
        const nombre = p.datos_perfil.nombre_proveedor;
        const encargado = p.datos_perfil.encargado;
        const div = document.createElement('div');
        div.className = 'lista-flotante-item';
        div.innerHTML = `<strong>${nombre}</strong> <span style="font-size:12px; color:#a3b1c6;">(Encargado: ${encargado})</span>`;
        div.onclick = function () {
            document.getElementById('buscador-proveedor').value = nombre;
            document.getElementById('proveedor-seleccionado-val').value = nombre;
            contenedor.style.display = 'none';
        };
        contenedor.appendChild(div);
    });
}

function mostrarTodosLosProveedores() {
    const buscador = document.getElementById('buscador-proveedor');
    if (buscador && buscador.disabled) return;
    renderizarListaFlotante(listaProveedoresParaAsignar);
    const lista = document.getElementById('lista-proveedores-flotante');
    if (lista) lista.style.display = 'block';
}

function filtrarProveedoresEnAsignacion() {
    const textoBuscado = document.getElementById('buscador-proveedor').value.toLowerCase();
    document.getElementById('proveedor-seleccionado-val').value = '';
    const filtrados = listaProveedoresParaAsignar.filter(p => p.datos_perfil.nombre_proveedor.toLowerCase().includes(textoBuscado));
    renderizarListaFlotante(filtrados);
    const lista = document.getElementById('lista-proveedores-flotante');
    if (lista) lista.style.display = 'block';
}

function abrirAsignacionReporte(idReporte) {
    const r = reportesGlobal.find(x => String(x.id) === String(idReporte)); if (!r) return; document.getElementById('asignar-reporte-id').value = r.id;

    document.getElementById('contenido-reporte-admin').innerHTML = generarHtmlReporteEnriquecido(r);

    const buscador = document.getElementById('buscador-proveedor');
    const hiddenProv = document.getElementById('proveedor-seleccionado-val');
    const listaFlotante = document.getElementById('lista-proveedores-flotante');

    if (buscador) buscador.value = '';
    if (hiddenProv) hiddenProv.value = '';
    if (listaFlotante) listaFlotante.style.display = 'none';

    fetch('/api/accesos').then(res => res.json()).then(data => {
        // --- INYECCIÓN DEL FILTRO GEOGRÁFICO PARA SUPERVISORES ---
        let subrolActualElement = document.getElementById('subrol-actual');
        let ciudadActualElement = document.getElementById('ciudad-actual');
        let subrolActual = subrolActualElement ? subrolActualElement.value : '';
        let miCiudad = ciudadActualElement ? ciudadActualElement.value : '';

        listaProveedoresParaAsignar = (data.usuarios || []).filter(u => {
            if (u.rol !== 'proveedores') return false;
            if (subrolActual === 'Supervisor' && u.datos_perfil.ciudad !== miCiudad) return false;
            return true;
        });
        // ---------------------------------------------------------

        if (r.asignado_a && r.asignado_a !== "") {
            if (buscador) { buscador.value = r.asignado_a; buscador.disabled = true; }
            document.querySelector('#modal-asignar-reporte .btn-success-modal').style.display = 'none';
        }
        else {
            if (buscador) buscador.disabled = false;
            document.querySelector('#modal-asignar-reporte .btn-success-modal').style.display = 'block';
            renderizarListaFlotante(listaProveedoresParaAsignar);
        }
    });
    document.getElementById('modal-asignar-reporte').style.display = 'flex';
}

function asignarReporteAProveedor() {
    const idReporte = document.getElementById('asignar-reporte-id').value;
    const proveedor = document.getElementById('proveedor-seleccionado-val').value;
    const compania = document.getElementById('select-compania').value;

    if (!proveedor) { alert('⚠️ Por favor selecciona un taller del buscador primero.'); return; }
    if (!compania) { alert('⚠️ Por favor selecciona a qué compañía pertenece (RUMN o Telnor).'); return; }

    if (!confirm(`¿Está seguro de asignar el reporte de falla al taller:\n${proveedor}\n\nCompañía: ${compania}`)) return;

    mostrarLoaderDinamico("Asignando al Taller...", "Enviando correo al proveedor 📧");

    fetch('/api/reportes/asignar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: idReporte, proveedor: proveedor, compania: compania })
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') { cerrarModal('modal-asignar-reporte'); cargarReportesAdmin(); }
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

async function cargarReportesProv() {
    try {
        const resFac = await fetch('/api/facturas/lista');
        const dataFacturas = await resFac.json();
        facturasGlobal = dataFacturas.facturas || [];

        const resRep = await fetch('/api/reportes/lista');
        const data = await resRep.json();

        let todosReportes = data.reportes || [];
        const provActualElement = document.querySelector('.sidebar-name');
        const provActual = provActualElement ? provActualElement.innerText.trim() : '';

        let reportesPendientes = todosReportes.filter(r => {
            let esMio = r.asignado_a === provActual;
            let yaFacturado = facturasGlobal.some(f => obtenerIdReporte(f) === String(r.id));
            return esMio && !yaFacturado;
        });

        reportesGlobal = todosReportes;
        const tbody = document.getElementById('tabla-reportes-prov');
        if (!tbody) return;

        tbody.innerHTML = '';
        if (reportesPendientes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#40916c;">No tienes órdenes de trabajo pendientes por cotizar ✅</td></tr>';
            return;
        }

        reportesPendientes.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        reportesPendientes.forEach(r => {
            let btnAccion = `<button class="btn-info" style="background:#0284c7;" onclick="abrirReporteProv('${r.id}')">Ver Detalle</button>`;
            tbody.innerHTML += `<tr><td><strong>${r.id}</strong></td><td>${r.fecha}</td><td>8090-${r.unidad}</td><td>${r.falla.substring(0, 30)}...</td><td>${r.mantenimiento}</td><td>${btnAccion}</td></tr>`;
        });
    } catch (err) { console.error(err); }
}

function abrirReporteProv(idReporte) {
    const r = reportesGlobal.find(x => String(x.id) === String(idReporte)); if (!r) return;
    reporteSeleccionado = r;
    document.getElementById('contenido-reporte-prov').innerHTML = generarHtmlReporteEnriquecido(r);
    document.getElementById('modal-ver-reporte-prov').style.display = 'flex';
}

function iniciarFacturaDesdeReporte() {
    if (!reporteSeleccionado) return;
    document.getElementById('modal-ver-reporte-prov').style.display = 'none';
    abrirModalNuevaFactura();
    document.getElementById('hidden_numero_reporte').value = reporteSeleccionado.id;
    document.getElementById('etiqueta-reporte-vinculado').style.display = 'block';
    document.getElementById('span-ticket-vinculado').innerText = reporteSeleccionado.id;
    document.getElementById('input_nueva_unidad').value = reporteSeleccionado.unidad;

    // Autocompletar la primera fila dinámica
    setTimeout(() => {
        let mant = document.querySelector('select[name="mantenimiento[]"]');
        if (mant) mant.value = reporteSeleccionado.mantenimiento;
        let retro = document.querySelector('textarea[name="retro[]"]');
        if (retro) retro.value = `REPORTE ORIGINAL DEL CHOFER: ${reporteSeleccionado.falla}`;
    }, 100);
}

function enviarFacturaDefinitiva() {
    if (!confirm("⚠️ ¿Estás seguro de enviar esta cotización a revisión?")) return;

    let precios = document.querySelectorAll('input[name="precio[]"]');
    precios.forEach(p => { p.value = p.value.replace(/[^0-9.]/g, ''); });

    let numRep = '';
    if (document.getElementById('hidden_numero_reporte')) numRep = document.getElementById('hidden_numero_reporte').value;

    if (numRep && numRep !== "") {
        let firstRetro = document.querySelector('textarea[name="retro[]"]');
        if (firstRetro && !firstRetro.value.includes(`[TICKET:${numRep}]`)) {
            firstRetro.value = `[TICKET:${numRep}]\n${firstRetro.value}`;
        }

        let singleRetro = document.querySelector('textarea[name="retro"]');
        if (singleRetro && !singleRetro.value.includes(`[TICKET:${numRep}]`)) {
            singleRetro.value = `[TICKET:${numRep}]\n${singleRetro.value}`;
        }
    }

    let formData = new FormData(document.getElementById('form-nueva-factura'));

    mostrarLoaderDinamico("Enviando cotización a revisión...", "Notificando a Automotriz 📧");

    fetch('/api/facturas/nueva', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') {
            document.getElementById('modal-previsualizacion-factura').style.display = 'none';
            document.getElementById('modal-ver-reporte-prov').style.display = 'none';
            cargarFacturas();
            if (document.getElementById('vista-reportes-prov') && document.getElementById('vista-reportes-prov').style.display !== 'none') {
                cargarReportesProv();
            }
        }
    }).catch(e => {
        ocultarLoaderDinamico();
        alert('Error al enviar factura.');
        console.error(e);
    });
}

function abrirModalDoc50(idFactura) {
    let modal = document.getElementById('modal-doc50-dinamico');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-doc50-dinamico';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-box large">
                <button class="btn-close-modal" onclick="cerrarModal('modal-doc50-dinamico')">×</button>
                <h3 class="modal-header" style="color: #ef4444;">🧾 Subir Documento Contable (Doc 50)</h3>
                <form id="form-subir-doc50" onsubmit="event.preventDefault(); subirDoc50();">
                    <input type="hidden" id="hidden-doc50-factura-id" name="id_factura">
                    <div id="subir-doc50-container"></div>
                    <div class="modal-actions" style="margin-top: 25px;">
                        <button type="button" class="btn-danger" onclick="cerrarModal('modal-doc50-dinamico')">Cancelar</button>
                        <button type="submit" class="btn-success-modal" style="display:block; width:100%; background:#ef4444;">Confirmar Doc 50</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
    }

    const f = facturasGlobal.find(x => String(x.id) === String(idFactura));
    let container = document.getElementById('subir-doc50-container');
    container.innerHTML = '';

    let cots = f && f.cotizaciones ? f.cotizaciones : [{ precio: f ? f.precio : 0 }];

    cots.forEach((cot, idx) => {
        container.innerHTML += `
            <div style="margin-bottom:15px; padding:15px; background:#0b1c30; border:1px dashed #ef4444; border-radius:8px;">
                <h4 style="color:#ef4444; margin-bottom:10px;">Cotización ${idx + 1}: ${cot.titulo || 'Sin Título'} (Factura: ${cot.factura_folio || 'N/A'})</h4>
                <div class="input-group full-width">
                    <label>Número de Documento (Ej. 50001234)</label>
                    <input type="text" name="numero_doc50[]" required style="width:100%; padding:10px; border-radius:8px;">
                </div>
                <div class="input-group full-width" style="margin-top:15px;">
                    <label>Archivo PDF del Doc 50</label>
                    <input type="file" name="pdf_doc50[]" accept=".pdf" required style="padding:10px; background:#112641; border:1px solid #1f395a; border-radius:8px; color:white; width:100%;">
                </div>
            </div>
        `;
    });

    document.getElementById('hidden-doc50-factura-id').value = idFactura;
    modal.style.display = 'flex';
}

function subirDoc50() {
    if (!confirm("¿Guardar el documento contable 50 para este expediente?")) return;
    mostrarLoaderDinamico("Subiendo Doc 50...", "Finalizando expediente 🗂️");
    let formData = new FormData(document.getElementById('form-subir-doc50'));
    fetch('/api/facturas/doc50', {
        method: 'POST',
        body: formData
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') {
            cerrarModal('modal-doc50-dinamico');
            cargarFacturas();
        }
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirModalValidacionFiscal(id, folio, pdf, unidad) {
    document.getElementById('val-factura-id').value = id;
    document.getElementById('val-unidad-text').innerText = unidad;

    const f = facturasGlobal.find(x => String(x.id) === String(id));
    let cots = f && f.cotizaciones ? f.cotizaciones : [];

    // Si hay cotizaciones con facturas, mostrar todas
    let pdfContainer = document.getElementById('val-pdf-frame').parentElement;
    if (cots.length > 1) {
        let allFacturas = cots.filter(c => c.factura_folio || c.factura_pdf);
        if (allFacturas.length > 0) {
            document.getElementById('val-folio-text').innerText = allFacturas.map((c, i) => `Cot ${i + 1}: ${c.factura_folio || 'N/A'}`).join(' | ');
            // Show first PDF in iframe
            let firstPdf = allFacturas[0].factura_pdf || allFacturas[0].pdf_fiscal || pdf;
            document.getElementById('val-pdf-frame').src = '/static/facturas_archivos/' + firstPdf;

            // Add navigation buttons if multiple
            let navContainer = document.getElementById('val-nav-facturas');
            if (!navContainer) {
                navContainer = document.createElement('div');
                navContainer.id = 'val-nav-facturas';
                navContainer.style.cssText = 'display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;';
                pdfContainer.parentElement.insertBefore(navContainer, pdfContainer);
            }
            navContainer.innerHTML = allFacturas.map((c, i) =>
                `<button type="button" style="background:#10b981; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.85em;" onclick="document.getElementById('val-pdf-frame').src='/static/facturas_archivos/${c.factura_pdf || c.pdf_fiscal}'">
                    📄 Cotización ${i + 1}: ${c.factura_folio || 'N/A'}
                </button>`
            ).join('');
        } else {
            document.getElementById('val-folio-text').innerText = folio;
            document.getElementById('val-pdf-frame').src = '/static/facturas_archivos/' + pdf;
        }
    } else {
        document.getElementById('val-folio-text').innerText = folio;
        document.getElementById('val-pdf-frame').src = '/static/facturas_archivos/' + pdf;
        let navContainer = document.getElementById('val-nav-facturas');
        if (navContainer) navContainer.innerHTML = '';
    }

    // Resetear contenedor de rechazo
    document.getElementById('val-rechazo-container').style.display = 'none';
    document.getElementById('val-motivo-rechazo').value = '';

    document.getElementById('modal-validacion-fiscal').style.display = 'flex';
}

function mostrarRechazoFiscal() {
    let id = document.getElementById('val-factura-id').value;
    abrirModalRechazo(id, 'fiscal');
}

function validarFacturaFiscalModal() {
    if (!confirm("¿Estás seguro de que deseas APROBAR esta factura fiscal? Esta acción notificará al proveedor y finalizará el proceso.")) return;

    let id = document.getElementById('val-factura-id').value;
    document.getElementById('modal-validacion-fiscal').style.display = 'none';
    mostrarLoaderDinamico("Validando factura...", "Actualizando registros ⏳");

    fetch('/api/facturas/validar_fiscal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    })
        .then(res => res.json())
        .then(data => {
            ocultarLoaderDinamico();
            alert(data.message);
            if (data.status === 'success') cargarFacturas();
        })
        .catch(err => {
            ocultarLoaderDinamico();
            console.error("Error al validar factura fiscal:", err);
        });
}

// --- FUNCIONES PARA DOCUMENTO CONTABLE Y ARCHIVO ---

function abrirModalDocContable(idFactura) {
    document.getElementById('hidden-doc-contable-id').value = idFactura;

    const f = facturasGlobal.find(x => String(x.id) === String(idFactura));
    let container = document.getElementById('doc-contable-container');
    container.innerHTML = '';

    let cots = f && f.cotizaciones ? f.cotizaciones : [{ precio: f ? f.precio : 0 }];

    cots.forEach((cot, idx) => {
        container.innerHTML += `
            <div style="margin-bottom:15px; padding:15px; background:#0b1c30; border:1px dashed #ef4444; border-radius:8px;">
                <h4 style="color:#ef4444; margin-bottom:10px;">Documento para Cotización ${idx + 1} (Folio Fiscal: ${cot.factura_folio || 'N/A'})</h4>
                <div class="input-group full-width">
                    <label style="color: #e0e6ed; font-weight: 600; display: block; margin-bottom: 8px;">Número de Documento Contable:</label>
                    <input type="text" name="numero_doc50[]" required 
                           style="width: 100%; padding: 12px; background: #112641; border: 1px solid #1f395a; border-radius: 8px; color: white; margin-bottom: 10px;"
                           placeholder="Ej. DC-908123">
                </div>
            </div>
        `;
    });

    document.getElementById('modal-doc-contable').style.display = 'flex';
}

function subirDocContable() {
    const id = document.getElementById('hidden-doc-contable-id').value;
    let nums = document.querySelectorAll('input[name="numero_doc50[]"]');

    // Validar que todos los campos estén completos
    let allValid = true;
    nums.forEach((n) => {
        if (!n.value.trim()) allValid = false;
    });
    if (!allValid) {
        alert("Por favor complete el número de documento contable para cada cotización.");
        return;
    }

    if (!confirm("¿Guardar todos los documentos contables y archivar el ticket?")) return;

    const formData = new FormData();
    formData.append('id_factura', id);
    nums.forEach((n) => {
        formData.append('numero_doc50[]', n.value.trim());
    });

    mostrarLoaderDinamico("Guardando Documentos Contables...", "Finalizando y Archivando Ticket 🗃️");

    fetch('/api/facturas/doc50', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            ocultarLoaderDinamico();
            if (data.status === 'success') {
                alert(data.message);
                cerrarModal('modal-doc-contable');
                cargarFacturas();
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(err => {
            ocultarLoaderDinamico();
            console.error(err);
            alert("Error de conexión.");
        });
}


function abrirVisorPDF(url) {
    if (window.innerWidth <= 768) {
        window.open(url, '_blank');
        return;
    }
    let modal = document.getElementById('global-pdf-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'global-pdf-modal';
        modal.className = 'modal-overlay';
        modal.style.zIndex = '999999';
        modal.innerHTML = `
            <div class="modal-box large" style="max-width: 1000px; width: 95vw; height: 90vh; padding: 0; background: #0b1c30; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #1f395a; border-radius: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #081422; border-bottom: 1px solid #1f395a;">
                    <h3 style="margin: 0; color: white; font-size: 1.2em;">📄 Visor de PDF</h3>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="window.open(document.getElementById('global-pdf-frame').src, '_blank')" style="background: #0284c7; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s;" onmouseover="this.style.background='#0369a1'" onmouseout="this.style.background='#0284c7'">📥 Descargar</button>
                        <button onclick="document.getElementById('global-pdf-modal').style.display='none'; document.getElementById('global-pdf-frame').src='';" style="background: transparent; color: #ef4444; border: 1px solid #ef4444; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: all 0.3s;" onmouseover="this.style.background='#ef4444'; this.style.color='white'" onmouseout="this.style.background='transparent'; this.style.color='#ef4444'">Cerrar</button>
                    </div>
                </div>
                <iframe id="global-pdf-frame" src="" style="flex: 1; width: 100%; border: none; background: white;"></iframe>
            </div>
        `;
        document.body.appendChild(modal);
    }
    document.getElementById('global-pdf-frame').src = url;
    modal.style.display = 'flex';
}

function toggleDropdownFixed(e, btn) {
    e.stopPropagation();
    let menu = btn.nextElementSibling;

    // Si ya esta abierto, lo cerramos
    let isOpen = menu.classList.contains('show') || menu.style.display === 'flex' || menu.style.display === 'block';

    // Cerrar cualquier otro abierto
    document.querySelectorAll('.dropdown-menu-fixed').forEach(m => {
        m.classList.remove('show');
        m.style.display = 'none';
    });

    if (!isOpen) {
        menu.style.display = ''; // Reset inline styles so CSS takes over
        menu.style.top = '';
        menu.style.left = '';
        menu.classList.add('show');
    }
}

// Cerrar el menu si se hace click en otro lado
document.addEventListener('click', function (e) {
    if (!e.target.closest('.dropdown-menu-fixed') && !e.target.closest('.btn-dropdown-toggle')) {
        document.querySelectorAll('.dropdown-menu-fixed').forEach(m => {
            m.classList.remove('show');
            m.style.display = 'none';
        });
    }
});


function abrirModalEdicionSeccion(id, tipo) {
    alert("Esta función ha sido deshabilitada para soportar múltiples cotizaciones por ticket.\n\nPara corregir un documento, por favor rechaza la factura o contacta a soporte si es un documento contable.");
    return;
    try {
        const f = facturasGlobal.find(x => String(x.id) === String(id));
        if (!f) return;

        let fileContainer = document.getElementById('current-file-container');
        let btnViewFile = document.getElementById('btn-view-current-file');

        let existingFile = null;
        let existingNumber = 'Ninguno';
        if (tipo === 'orden') {
            existingFile = f.pdf_cotizacion_asignacion;
            existingNumber = f.numero_orden || f.numero_cotizacion_asignacion || 'Ninguno';
        }
        else if (tipo === 'factura') {
            existingFile = f.factura_pdf || f.pdf_fiscal;
            existingNumber = f.factura_folio || 'Ninguno';
        }
        else if (tipo === 'doc_contable') {
            existingFile = f.pdf_doc50;
            existingNumber = f.numero_doc50 || 'Ninguno';
        }

        if (existingFile || existingNumber !== 'Ninguno') {
            fileContainer.style.display = 'block';
            document.getElementById('current-file-number').textContent = existingNumber;
            if (existingFile) {
                btnViewFile.style.display = 'inline-block';
                btnViewFile.onclick = () => abrirVisorPDF('/static/facturas_archivos/' + existingFile);
            } else {
                btnViewFile.style.display = 'none';
            }
        } else {
            fileContainer.style.display = 'none';
        }

        document.getElementById('edit-sec-id-factura').value = id;
        document.getElementById('edit-sec-tipo').value = tipo;

        let header = document.getElementById('header-editar-seccion');
        let label = document.getElementById('label-edit-sec-numero');

        document.getElementById('edit-sec-numero').value = '';
        document.getElementById('edit-sec-pdf').value = '';
        document.getElementById('nombre-edit-sec-pdf').textContent = 'Ningún archivo seleccionado';
        document.getElementById('preview-edit-sec-container').style.display = 'none';
        document.getElementById('preview-edit-sec-container').innerHTML = '';

        if (tipo === 'orden') {
            header.textContent = 'Editar Orden de Pedido (Sección 3)';
            label.textContent = 'Nuevo Número de Orden/Solicitud:';
        } else if (tipo === 'factura') {
            header.textContent = 'Editar Factura Fiscal (Sección 4)';
            label.textContent = 'Nuevo Folio de Factura:';
        } else if (tipo === 'doc_contable') {
            header.textContent = 'Editar Documento Contable (Sección 5)';
            label.textContent = 'Nuevo Número de Documento Contable:';
        }

        document.getElementById('modal-editar-seccion').style.display = 'flex';
    } catch (err) {
        alert('Error: ' + err.message);
        console.error(err);
    }
}

async function guardarEdicionSeccion() {
    let id = document.getElementById('edit-sec-id-factura').value;
    let tipo = document.getElementById('edit-sec-tipo').value;
    let numero = document.getElementById('edit-sec-numero').value.trim();
    let file = document.getElementById('edit-sec-pdf').files[0];

    if (!numero || !file) {
        alert('Por favor ingresa el número y selecciona un PDF.');
        return;
    }

    let fd = new FormData();
    fd.append('id_factura', id);
    fd.append('seccion', tipo);
    fd.append('identificador', numero);
    fd.append('pdf_file', file);

    try {
        let btn = document.querySelector('#form-editar-seccion .btn-success-modal');
        btn.textContent = 'Guardando...';
        btn.disabled = true;

        let res = await fetch('/api/facturas/editar_seccion_especifica', { method: 'POST', body: fd });
        let data = await res.json();

        if (data.status === 'success') {
            alert('Sección actualizada correctamente.');
            cerrarModal('modal-editar-seccion');
            if (typeof fetchFacturasGlobal === 'function') await fetchFacturasGlobal();
            if (typeof renderTabla === 'function') renderTabla();
            else if (typeof cargarFacturas === 'function') cargarFacturas();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al actualizar la sección.');
    } finally {
        let btn = document.querySelector('#form-editar-seccion .btn-success-modal');
        btn.textContent = 'Guardar Cambios';
        btn.disabled = false;
    }
}

window.switchTabArchivo = function (tabName) {
    let btnNormal = document.getElementById('btn-tab-archivo-normal');
    let btnCancelado = document.getElementById('btn-tab-archivo-cancelado');
    let contNormal = document.getElementById('contenedor-archivo-normal');
    let contCancelado = document.getElementById('contenedor-archivo-cancelado');

    if (tabName === 'normal') {
        btnNormal.style.background = '#0ea5e9';
        btnCancelado.style.background = '#475569';
        contNormal.style.display = 'block';
        contCancelado.style.display = 'none';
    } else {
        btnNormal.style.background = '#475569';
        btnCancelado.style.background = '#ef4444'; // Rojo oscuro para cancelados
        contNormal.style.display = 'none';
        contCancelado.style.display = 'block';
    }
};


function cancelarTicketAdmin() {
    let idFac = document.getElementById('rev-id-admin').value;
    if (!idFac) return;
    document.getElementById('modal-confirmar-cancelacion').style.display = 'flex';
}

function ejecutarCancelacionTicket() {
    let idFac = document.getElementById('rev-id-admin').value;
    if (!idFac) return;

    let fd = new FormData();
    fd.append('id', idFac);

    // Cambiamos el texto del boton mientras carga
    let btn = document.querySelector('#modal-confirmar-cancelacion .btn-danger-modal');
    let textOriginal = btn.textContent;
    btn.textContent = 'Cancelando...';
    btn.disabled = true;

    fetch('/api/facturas/cancelar_cotizacion', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            btn.textContent = textOriginal;
            btn.disabled = false;
            if (d.status === 'success') {
                document.getElementById('modal-confirmar-cancelacion').style.display = 'none';
                document.getElementById('modal-revision-admin').style.display = 'none';

                // Navegar automticamente a la vista de archivo y luego a la pestaa de cancelados
                if (typeof cambiarVistaAdmin === 'function') {
                    cambiarVistaAdmin('archivo');
                    if (typeof switchTabArchivo === 'function') {
                        switchTabArchivo('cancelado');
                    }
                }

                cargarFacturas();
            } else {
                alert(d.message);
            }
        }).catch(e => {
            btn.textContent = textOriginal;
            btn.disabled = false;
            alert("Error de red.");
            console.error(e);
        });
}


function agregarCotizacionFila() {
    const container = document.getElementById('lista-cotizaciones');
    if (!container) return;
    const idx = container.children.length;

    const fila = document.createElement('div');
    fila.className = 'cotizacion-fila';
    fila.style.cssText = 'margin-bottom:20px; padding:15px; border:1px solid #1f395a; border-radius:8px; background:#112641; position:relative;';

    fila.innerHTML = `
        <h5 style="color:#0ea5e9; margin-bottom:15px;">Cotización ${idx + 1}</h5>
        ${idx > 0 ? `<button type="button" onclick="this.parentElement.remove()" style="position:absolute; top:15px; right:15px; background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">Eliminar</button>` : ''}
        
        <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="display:flex; gap:10px;">
                <div style="flex:1;">
                    <label>Título de la Cotización *</label>
                    <input type="text" name="titulo[]" required style="width:100%; padding:10px; border-radius:8px;">
                </div>
                <div style="flex:1;">
                    <label>Tipo de Mantenimiento *</label>
                    <select name="mantenimiento[]" required style="width:100%; padding:10px; border-radius:8px; background:#0b1c30; color:white; border:1px solid #1f395a;">
                        <option value="" disabled selected>Selecciona</option>
                        <option value="Preventivo">Preventivo</option>
                        <option value="Correctivo">Correctivo</option>
                    </select>
                </div>
            </div>
            
            <div>
                <label>Retro (Problema/Situación) *</label>
                <textarea name="retro[]" required style="width:100%; padding:10px; border-radius:8px; background:#0b1c30; color:white; border:1px solid #1f395a; min-height:60px;"></textarea>
            </div>
            
            <div>
                <label>Diagnóstico de Mecánico *</label>
                <textarea name="diagnostico[]" required style="width:100%; padding:10px; border-radius:8px; background:#0b1c30; color:white; border:1px solid #1f395a; min-height:60px;"></textarea>
            </div>
            
            <div>
                <label>Trabajo a Realizar *</label>
                <textarea name="trabajo_realizar[]" required style="width:100%; padding:10px; border-radius:8px; background:#0b1c30; color:white; border:1px solid #1f395a; min-height:60px;"></textarea>
            </div>
            
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="flex:1;">
                    <label>Precio (Sin IVA) MXN *</label>
                    <input type="text" name="precio[]" placeholder="$0.00 MXN" required onblur="formatearEnInput(this)" onfocus="limpiarInput(this)" style="width:100%;">
                </div>
                <div style="flex:1;">
                    <label style="color:#0284c7;">PDF/Foto Cotización *</label>
                    <input type="file" name="pdf_cotizacion[]" accept="image/*,.pdf" required style="width:100%; padding:5px; background:white; color:black; border-radius:5px;" onchange="previsualizarArchivoCotizacion(this, 'preview-pdf-${idx}')">
                    <div id="preview-pdf-${idx}" style="margin-top:8px;"></div>
                </div>
                <div style="flex:1;">
                    <label style="color:#40916c;">Fotos Evidencia (varias)</label>
                    <input type="file" name="fotos_evidencia_${idx}[]" multiple accept="image/*" style="width:100%; padding:5px; background:white; color:black; border-radius:5px;" onchange="previsualizarFotosEvidencia(this, 'preview-ev-${idx}')">
                    <div id="preview-ev-${idx}" style="margin-top:8px; display:flex; flex-wrap:wrap; gap:5px;"></div>
                </div>
            </div>
        </div>
    `;
    container.appendChild(fila);
}

function previsualizarArchivoCotizacion(input, previewId) {
    const previewDiv = document.getElementById(previewId);
    if (!previewDiv) return;
    previewDiv.innerHTML = '';

    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const url = URL.createObjectURL(file);

    previewDiv.style.display = 'inline-block';
    previewDiv.style.position = 'relative';

    let contentHtml = '';
    let isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (isPdf) {
        contentHtml = `
            <button type="button" onclick="abrirVisorArchivoLocal('${previewId}')" 
                style="background:#0284c7; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; font-size:0.85em; display:flex; align-items:center; gap:5px;">
                📄 Ver PDF: ${file.name}
            </button>
        `;
        previewDiv.dataset.fileType = 'pdf';
    } else {
        contentHtml = `
            <img src="${url}" onclick="abrirVisorArchivoLocal('${previewId}')" 
                style="max-width:120px; max-height:80px; border-radius:5px; border:2px solid #0284c7; cursor:pointer; object-fit:cover; display:block;"
                title="Click para ver en grande">
        `;
        previewDiv.dataset.fileType = 'image';
    }

    previewDiv.dataset.fileUrl = url;
    previewDiv.innerHTML = contentHtml;

    const btnEliminar = document.createElement('button');
    btnEliminar.type = 'button';
    btnEliminar.innerHTML = '✖';
    btnEliminar.style.cssText = 'position:absolute; top:-8px; right:-8px; background:#ef4444; color:white; border:none; border-radius:50%; width:20px; height:20px; cursor:pointer; font-size:10px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(0,0,0,0.5); z-index:10;';
    btnEliminar.title = 'Quitar archivo';
    btnEliminar.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation(); // Prevents triggering the image/pdf click if overlapping
        input.value = '';
        previewDiv.innerHTML = '';
        previewDiv.style.display = 'none';
    };
    previewDiv.appendChild(btnEliminar);
    
    // Auto-open if it's a PDF to ensure they see it immediately
    if (isPdf) {
        setTimeout(() => abrirVisorArchivoLocal(previewId), 100);
    }
}

function previsualizarFotosEvidencia(input, previewId) {
    const previewDiv = document.getElementById(previewId);
    if (!previewDiv) return;
    previewDiv.innerHTML = '';

    if (!input.files || input.files.length === 0) return;

    previewDiv.style.display = 'flex';
    previewDiv.style.alignItems = 'flex-start';
    previewDiv.style.flexWrap = 'wrap';
    previewDiv.style.gap = '10px';

    for (let i = 0; i < input.files.length; i++) {
        const file = input.files[i];
        const url = URL.createObjectURL(file);

        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';

        const img = document.createElement('img');
        img.src = url;
        img.style.cssText = 'width:60px; height:60px; border-radius:4px; border:1px solid #40916c; cursor:pointer; object-fit:cover; display:block;';
        img.title = file.name;
        img.onclick = function () {
            const lb = document.getElementById('lightbox-modal');
            const lbImg = document.getElementById('lightbox-img');
            if (lb && lbImg) {
                lbImg.src = url;
                lb.style.display = 'flex';
            }
        };

        const btnEliminar = document.createElement('button');
        btnEliminar.type = 'button';
        btnEliminar.innerHTML = '✖';
        btnEliminar.style.cssText = 'position:absolute; top:-5px; right:-5px; background:#ef4444; color:white; border:none; border-radius:50%; width:20px; height:20px; cursor:pointer; font-size:10px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(0,0,0,0.5);';
        btnEliminar.title = 'Quitar foto';
        btnEliminar.onclick = function (e) {
            e.preventDefault();
            const dt = new DataTransfer();
            for (let j = 0; j < input.files.length; j++) {
                if (file !== input.files[j]) {
                    dt.items.add(input.files[j]);
                }
            }
            input.files = dt.files;
            wrapper.remove();
        };

        wrapper.appendChild(img);
        wrapper.appendChild(btnEliminar);
        previewDiv.appendChild(wrapper);
    }
}

function abrirVisorArchivoLocal(previewId) {
    const previewDiv = document.getElementById(previewId);
    if (!previewDiv) return;

    const url = previewDiv.dataset.fileUrl;
    const tipo = previewDiv.dataset.fileType;

    if (tipo === 'pdf') {
        // Open PDF in a modal with iframe
        let modal = document.getElementById('modal-visor-archivo-local');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modal-visor-archivo-local';
            modal.className = 'modal-overlay';
            modal.style.cssText = 'display:none; z-index:2000;';
            modal.innerHTML = `
                <div class="pdf-modal-box" style="width:95%; max-width:900px; height:90vh; padding:15px; display:flex; flex-direction:column;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h3 style="color:#112641; margin:0;">Vista Previa del Documento</h3>
                        <button onclick="document.getElementById('modal-visor-archivo-local').style.display='none'" 
                            style="background:#ef4444; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">✕ Cerrar</button>
                    </div>
                    <embed id="embed-visor-local" src="" type="application/pdf" style="flex:1; width:100%; border:none; border-radius:8px;"></embed>
                </div>
            `;
            document.body.appendChild(modal);
        }
        document.getElementById('embed-visor-local').src = url;
        modal.style.display = 'flex';
    } else if (tipo === 'image') {
        // Use existing lightbox
        const lb = document.getElementById('lightbox-modal');
        const lbImg = document.getElementById('lightbox-img');
        if (lb && lbImg) {
            lbImg.src = url;
            lb.style.display = 'flex';
        }
    }
}

