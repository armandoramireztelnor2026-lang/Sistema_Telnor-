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

        const resRep = await fetch('/api/reportes/lista');
        const dataRep = await resRep.json();
        reportesGlobal = dataRep.reportes || [];

        const tbody = document.getElementById('tabla-facturas');
        const tbodyFinales = document.getElementById('tabla-facturas-finales');
        const tbodyDocContables = document.getElementById('tabla-doc-contables');
        const tbodyArchivo = document.getElementById('tabla-archivo');
        const rolUsuario = document.getElementById('rol-actual').value;

        if (tbody) tbody.innerHTML = '';
        if (tbodyFinales) tbodyFinales.innerHTML = '';
        if (tbodyDocContables) tbodyDocContables.innerHTML = '';
        if (tbodyArchivo) tbodyArchivo.innerHTML = '';

        if (facturasGlobal.length === 0) {
            if (tbody) tbody.innerHTML = `<tr><td colspan="${rolUsuario === 'administracion' ? '8' : '7'}" style="text-align:center;">No hay cotizaciones registradas</td></tr>`;
            if (tbodyFinales) tbodyFinales.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay facturas registradas</td></tr>`;
        }
        else {
            let countCotizaciones = 0;
            let countFacturas = 0;
            let countDocContables = 0;
            let countArchivo = 0;

            facturasGlobal.forEach(f => {

                let precioFormatArch = parseFloat(f.precio_estimado || f.precio || 0).toLocaleString('en-US');

                if (f.estado === 'Archivado') {
                    if (tbodyArchivo && rolUsuario === 'administracion') {
                        let btnVerExp = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">
                            <button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0; width:100%;" onclick="abrirDetalles('${f.id}')">Ver Detalles del Ticket</button>
                            <button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#40916c; border:none; margin:0; width:100%;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_doc50}')">📄 Ver Documento Contable</button>
                            <button class="btn-danger-sm" style="width:100%; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar</button>
                        </div>`;
                        let idReporteAsociado = obtenerIdReporte(f) || 'N/A';
                        tbodyArchivo.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idReporteAsociado}</span></td><td><strong>${f.numero_doc50}</strong></td><td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.unidad}</td><td><strong>${f.proveedor}</strong></td><td>$${precioFormatArch} MXN</td><td>${btnVerExp}</td></tr>`;
                        countArchivo++;
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
                        btnAccion += `<button class="btn-success" onclick="abrirRevisionAdmin('${f.id}')" style="width:100%; margin:0;">Aprobar y Asignar Orden</button>`;
                    } else {
                        btnAccion += `<button class="btn-info" onclick="abrirDetalles('${f.id}')" style="width:100%; margin:0;">Ver Detalles</button>`;
                    }

                    if (confirmadaTotal && entregadoTexto !== 'Sí') {
                        btnAccion += `<button class="btn-info" onclick="abrirModalValidacion('${f.id}', '${f.unidad.replace('8090-', '')}')" style="background:#0284c7; width:100%; margin:0; border:none;">🔑 Validar PIN Chofer</button>`;
                    } else if (!confirmadaTotal) {
                        btnAccion += `<button disabled class="btn-info" style="background:#475569; color:#94a3b8; border:none; width:100%; margin:0; cursor:not-allowed;">🔒 Esperando Confirmación</button>`;
                    }

                    let btnEditar = !apAdmin
                        ? `<button disabled class="btn-info" style="background:#78350f; color:#d6d3d1; flex:1; margin:0; cursor:not-allowed; border:none;" title="Bloqueado: Primero debes asignar una orden">🔒 Editar</button>`
                        : `<button class="btn-info" style="background:#f59e0b; flex:1; margin:0;" onclick="abrirModalEditarAdmin('${f.id}')">Editar</button>`;

                    btnAccion += `<div style="display:flex; gap:5px;">${btnEditar}<button class="btn-danger-sm" style="flex:1; margin:0;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar</button></div>`;

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
                            btnAccion += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#40916c; border:none; margin-top:5px; width:100%;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_fiscal || f.factura_pdf}')">📄 Ver Factura Subida</button>`;
                        }
                    }
                    btnAccion += `</div>`;
                }

                let ciaExtra = f.compania ? ` | Cia: <strong style="color:white;">${f.compania}</strong>` : ``;
                let infoExtra = `<br><small style="color:#a3b1c6;">Ticket: ${obtenerIdReporte(f) || 'S/T'} | Orden: <strong style="color:#f59e0b;">${f.numero_orden || 'Pendiente'}</strong>${ciaExtra}</small>`;
                let tdTitulo = `<td>${f.titulo}${infoExtra}</td>`;

                if ((rolUsuario === 'proveedores' || rolUsuario === 'administracion') && entregadoTexto === 'Sí') {
                    if (tbodyFinales) {
                        let badgeFolio = f.factura_folio ? `<span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span>` : `<span style="color:#ef4444; font-weight:bold;">Pendiente</span>`;
                        let btnAdminExtra = '';
                        let estadoFiscalBadge = '';

                        if (rolUsuario === 'administracion') {
                            btnAdminExtra = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">`;
                            btnAdminExtra += `<button class="btn-info" onclick="abrirDetalles('${f.id}')" style="width:100%; margin:0;">Ver Detalles</button>`;

                            
                            let valFiscal = f.validacion_fiscal || 'Pendiente';
                            
                            if (valFiscal === 'Aprobada') {
                                if (rolUsuario === 'administracion') {
                                    if (tbodyDocContables) {
                                        let btnDoc = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">
                                            <button class="btn-info" style="width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>
                                            <button class="btn-success" style="width:100%; margin:0;" onclick="abrirModalDocContable('${f.id}')">Subir Documento Final</button>
                                            <button class="btn-danger-sm" style="width:100%; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar</button>
                                        </div>`;
                                        tbodyDocContables.innerHTML += `<tr><td><span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></td><td>${f.fecha}</td><td><strong>${f.proveedor}</strong></td><td>${f.unidad}</td><td>${f.titulo}</td><td>$${precioBonito} MXN</td><td>${btnDoc}</td></tr>`;
                                        countDocContables++;
                                    }
                                    return; // Ocultar de la bandeja Facturas de administracion
                                }
                            }

                            if (f.factura_folio) {

                                if (valFiscal === 'Pendiente') {
                                    estadoFiscalBadge = `<span style="background:#b45309; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Pendiente Validación</span>`;
                                    btnAdminExtra += `<button class="btn-success" style="width:100%; margin:0;" onclick="abrirModalValidacionFiscal('${f.id}', '${f.factura_folio}', '${f.pdf_fiscal || f.factura_pdf}', '${f.unidad}')">Revisar y Validar</button>`;
                                } else if (valFiscal === 'Aprobada') {
                                    estadoFiscalBadge = `<span style="background:#2d6a4f; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Factura Aprobada</span>`;
                                    btnAdminExtra += `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#40916c; border:none; margin:0; width:100%;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_fiscal || f.factura_pdf}')">📄 Ver Factura PDF</button>`;
                                    btnAdminExtra += `<button class="btn-info" style="background:#f59e0b; width:100%; margin:0;" onclick="abrirModalEditarAdmin('${f.id}')">Editar Datos</button>`;
                                } else {
                                    estadoFiscalBadge = `<span style="background:#ef4444; color:white; padding:4px 8px; border-radius:12px; font-size:0.85em; white-space:nowrap;">Rechazada</span>`;
                                }
                            } else {
                                estadoFiscalBadge = `<span style="color:#b45309; font-weight:bold;">Esperando Factura</span>`;
                                btnAdminExtra += `<span style="color:#b45309; font-size:0.85em;">Esperando subida de proveedor</span>`;
                            }

                            btnAdminExtra += `<button class="btn-danger-sm" style="width:100%; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaDefinitiva('${f.id}')">Eliminar del Sistema</button>`;
                            btnAdminExtra += `</div>`;
                        }

                        let tdProv = rolUsuario === 'administracion' ? `<td><strong>${f.proveedor}</strong></td>` : '';
                        let tdEstadoFiscal = rolUsuario === 'administracion' ? `<td>${estadoFiscalBadge}</td>` : '';
                        let tdEstado = rolUsuario === 'proveedores' ? `<td>${estadoBadge}</td>` : '';
                        let tdEntregadoFinal = rolUsuario === 'administracion' ? `<td>${entregadoBadge}</td>` : '';
                        let acciones = rolUsuario === 'administracion' ? btnAdminExtra : btnAccion;
                        
                        tbodyFinales.innerHTML += `<tr><td>${badgeFolio}</td><td>${f.fecha}</td>${tdProv}<td>${f.unidad}</td>${tdTitulo}<td>$${precioBonito} MXN</td>${tdEstadoFiscal}${tdEstado}${tdEntregadoFinal}<td>${acciones}</td></tr>`;
                        countFacturas++;
                    }
                } else {
                    if (tbody) {
                        let tdEntregado = rolUsuario === 'administracion' ? `<td>${entregadoBadge}</td>` : '';
                        tbody.innerHTML += `<tr><td>${f.fecha}</td>${rolUsuario !== 'proveedores' ? `<td><strong>${f.proveedor}</strong></td>` : ''}<td>${f.unidad}</td>${tdTitulo}<td>$${precioBonito} MXN</td><td>${estadoBadge}</td>${tdEntregado}<td>${btnAccion}</td></tr>`;
                        countCotizaciones++;
                    }
                }
            });

            
            if (tbody && countCotizaciones === 0) tbody.innerHTML = `<tr><td colspan="${rolUsuario === 'administracion' ? '8' : '7'}" style="text-align:center;">No hay cotizaciones registradas</td></tr>`;
            if (tbodyFinales && countFacturas === 0) tbodyFinales.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay facturas registradas</td></tr>`;
            if (tbodyDocContables && countDocContables === 0) tbodyDocContables.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay documentos contables pendientes</td></tr>`;
            if (tbodyArchivo && countArchivo === 0) tbodyArchivo.innerHTML = `<tr><td colspan="6" style="text-align:center;">No hay registros archivados</td></tr>`;
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
            <div class="modal-box">
                <button class="btn-close-modal" onclick="cerrarModal('modal-subir-factura-dinamico')">×</button>
                <h3 class="modal-header" style="color: #10b981;">🧾 Subir Factura Contable (Final)</h3>
                <p style="color: #a3b1c6; margin-bottom: 15px; font-size: 14px;">Ingresa tu folio fiscal y sube el PDF oficial de tu factura para que Finanzas procese el pago.</p>
                <form id="form-subir-factura" onsubmit="event.preventDefault(); procesarSubidaFactura();">
                    <input type="hidden" id="hidden-factura-final-id" name="id_factura">
                    <div class="input-group full-width">
                        <label>Folio Fiscal (Ej. F-1029)</label>
                        <input type="text" id="input-folio-fiscal" name="folio" required>
                    </div>
                    <div class="input-group full-width" style="margin-top:15px;">
                        <label>Archivo PDF de la Factura Oficial</label>
                        <input type="file" id="input-pdf-fiscal" name="pdf_factura" accept=".pdf" required style="padding:10px; background:#0b1c30; border:1px solid #1f395a; border-radius:8px; color:white; width:100%;">
                    </div>
                    <div class="modal-actions" style="margin-top: 25px;">
                        <button type="button" class="btn-danger" onclick="cerrarModal('modal-subir-factura-dinamico')">Cancelar</button>
                        <button type="submit" class="btn-success-modal" style="width:100%; background:#10b981;">Confirmar y Enviar Factura</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('hidden-factura-final-id').value = idFactura;
    document.getElementById('form-subir-factura').reset();
    modal.style.display = 'flex';
}

function procesarSubidaFactura() {
    if (!confirm("¿Estás seguro de anexar este documento fiscal al expediente?")) return;
    mostrarLoaderDinamico("Subiendo documento contable...", "Enlazando al expediente de la unidad 📧");
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
            if (tipo === 'usuario') { if(typeof cargarPendientes === 'function') cargarPendientes(); }
            else if (tipo === 'reporte') { if(typeof cargarReportesAdmin === 'function') cargarReportesAdmin(); else cargarFacturas(); }
            else { if(typeof cargarFacturasAdmin === 'function') cargarFacturasAdmin(); else cargarFacturas(); }
        }
    })
    .catch(err => {
        ocultarLoaderDinamico();
        console.error("Error al procesar rechazo:", err);
    });
}

function eliminarFacturaDefinitiva(idFactura) { abrirModalRechazo(idFactura, 'factura'); }
function rechazarFactura(inputIdModal) { let id_fac = document.getElementById(inputIdModal).value; abrirModalRechazo(id_fac, 'factura'); }
function eliminarReporteDefinitivo(idReporte) { abrirModalRechazo(idReporte, 'reporte'); }

function abrirModalEditarAdmin(idFactura) {
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if (!f) return;
    document.getElementById('edit_id_factura').value = f.id; document.getElementById('edit_unidad').value = f.unidad.replace('8090-', ''); document.getElementById('edit_responsable').value = f.responsable; document.getElementById('edit_telefono').value = f.telefono; document.getElementById('edit_fecha').value = f.fecha; document.getElementById('edit_titulo').value = f.titulo;
    document.getElementById('edit_retro').value = limpiarRetro(f.retro);
    document.getElementById('edit_diagnostico').value = f.diagnostico || ''; document.getElementById('edit_trabajo_realizar').value = f.trabajo_realizar || ''; document.getElementById('edit_mantenimiento').value = f.mantenimiento; document.getElementById('edit_numero_orden').value = f.numero_orden || '';
    let inputPrecio = document.getElementById('edit_precio'); inputPrecio.value = f.precio; formatearEnInput(inputPrecio);
    dtCotizacionEdicion = new DataTransfer(); dtEvidenciaEdicion = new DataTransfer();
    document.getElementById('edit-preview-cotizacion-nuevas').innerHTML = ''; document.getElementById('edit-preview-evidencia-nuevas').innerHTML = '';
    imagenesGuardadasCotizacion = [...f.fotos_cotizacion]; imagenesGuardadasEvidencia = [...f.fotos_evidencia];
    renderizarImagenesGuardadas(); document.getElementById('modal-editar-admin').style.display = 'flex';
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
    document.getElementById('form-nueva-factura').reset(); dtCotizacion = new DataTransfer(); dtEvidencia = new DataTransfer(); document.getElementById('preview-cotizacion').innerHTML = ''; document.getElementById('preview-evidencia').innerHTML = '';
    if (document.getElementById('hidden_numero_reporte')) document.getElementById('hidden_numero_reporte').value = '';
    if (document.getElementById('etiqueta-reporte-vinculado')) document.getElementById('etiqueta-reporte-vinculado').style.display = 'none';
    document.getElementById('modal-nueva-factura').style.display = 'flex';
}

function previsualizarFactura() {
    if (dtCotizacion.files.length === 0 || dtEvidencia.files.length === 0) { alert("Por favor, asegúrate de subir al menos una cotización y una evidencia."); return; }

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
                if (document.getElementById('prev-rep-firma-container')) {
                    document.getElementById('prev-rep-firma-container').style.display = 'block';
                    document.getElementById('prev-rep-firma-img').src = r.firma_chofer;
                }
            } else {
                if (document.getElementById('prev-rep-firma-container')) {
                    document.getElementById('prev-rep-firma-container').style.display = 'none';
                }
            }
        }
    } else {
        if (document.getElementById('pdf-seccion-reporte')) document.getElementById('pdf-seccion-reporte').style.display = 'none';
    }

    document.getElementById('prev-unidad').innerText = "8090-" + document.querySelector('input[name="unidad"]').value; document.getElementById('prev-responsable').innerText = document.querySelector('input[name="responsable"]').value; document.getElementById('prev-telefono').innerText = document.querySelector('input[name="telefono"]').value; document.getElementById('prev-fecha').innerText = document.querySelector('input[name="fecha"]').value; document.getElementById('prev-titulo').innerText = document.querySelector('input[name="titulo"]').value; document.getElementById('prev-retro').innerText = document.querySelector('textarea[name="retro"]').value; document.getElementById('prev-diagnostico').innerText = document.querySelector('textarea[name="diagnostico"]').value; document.getElementById('prev-trabajo-realizar').innerText = document.querySelector('textarea[name="trabajo_realizar"]').value; document.getElementById('prev-mantenimiento').innerText = document.querySelector('select[name="mantenimiento"]').value;
    let precioIngresado = document.querySelector('input[name="precio"]').value; document.getElementById('prev-precio').innerText = formatearMoneda(precioIngresado.replace(/[^0-9.]/g, ''));

    const contCotizacion = document.getElementById('prev-cotizaciones-container'); const contEvidencia = document.getElementById('prev-evidencias-container');
    contCotizacion.innerHTML = ''; contEvidencia.innerHTML = '';
    const renderizarAnexo = (archivos, etiqueta, contenedor) => { Array.from(archivos).forEach(file => { const divInfo = document.createElement('div'); divInfo.className = 'pdf-image-container'; if (file.type.startsWith('image/')) { divInfo.innerHTML = `<img src="${URL.createObjectURL(file)}" class="pdf-anexo-img"><p class="pdf-anexo-label">${etiqueta}: ${file.name}</p>`; } else if (file.name.endsWith('.pdf')) { divInfo.innerHTML = `<iframe src="${URL.createObjectURL(file)}" style="width:100%; height:150px; border:1px solid #1f395a; border-radius:5px; margin-bottom:5px;"></iframe><p class="pdf-anexo-label">${etiqueta} (PDF Adjunto): ${file.name}</p>`; } contenedor.appendChild(divInfo); }); };
    renderizarAnexo(dtCotizacion.files, 'Cotización', contCotizacion); renderizarAnexo(dtEvidencia.files, 'Evidencia del Trabajo', contEvidencia);

    document.getElementById('modal-nueva-factura').style.display = 'none'; document.getElementById('modal-previsualizacion-factura').style.display = 'flex';
}

function volverAEditar() { document.getElementById('modal-previsualizacion-factura').style.display = 'none'; document.getElementById('modal-nueva-factura').style.display = 'flex'; }

function generarHtmlDetalles(f, modo, precioBonito) {
    let ordenTexto = f.numero_orden || '<span style="color:#ef4444;">Pendiente de Administración</span>';
    let htmlReporte = '';
    let idReporte = obtenerIdReporte(f);

    if (idReporte) {
        let r = reportesGlobal.find(x => String(x.id) === String(idReporte));
        if (r) {
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "<span style='color:#a3b1c6; font-style:italic;'>No proporcionado</span>";
            let ciudadStatus = r.ciudad || "No especificada";
            let copeStatus = r.cope || "No especificado";

            htmlReporte = `
                <div style="margin-bottom: 20px; border: 2px dashed #f59e0b; padding: 15px; border-radius: 8px; background-color: #0b1c30;">
                    <div style="color: #f59e0b; border-bottom: 1px solid #f59e0b; padding-bottom: 5px; margin-bottom: 10px; font-weight: bold; font-size:1.1em;">■ SECCIÓN 1: REPORTE DE INCIDENCIA (ORIGEN)</div>
                    <div class="form-grid" style="grid-template-columns: 1fr 1fr;">
                        <div class="modal-info-line"><strong>Ticket No.:</strong> <span style="color:#f59e0b; font-weight:bold;">${r.id}</span></div>
                        <div class="modal-info-line"><strong>Fecha Reporte:</strong> ${r.fecha}</div>
                        <div class="modal-info-line"><strong>Unidad:</strong> 8090-${r.unidad}</div>
                        ${r.compania ? `<div class="modal-info-line"><strong>Compañía:</strong> <span style="color:#10b981; font-weight:bold;">${r.compania}</span></div>` : ''}
                        ${f.numero_cotizacion_asignacion ? `<div class="modal-info-line"><strong>No. de Solicitud de Pedido:</strong> <span>${f.numero_cotizacion_asignacion}</span></div>` : ''}
                        ${f.pdf_cotizacion_asignacion ? `<div class="modal-info-line"><strong>PDF de Solicitud de Pedido:</strong> <a href="/static/facturas_archivos/${f.pdf_cotizacion_asignacion}" target="_blank" style="color:#ef4444; font-weight:bold; text-decoration:none;">📄 Ver Documento</a></div>` : ''}
                        <div class="modal-info-line"><strong>Marca/Modelo:</strong> ${r.marca} ${r.modelo}</div>
                        <div class="modal-info-line"><strong>Tipo Mantenimiento:</strong> ${r.mantenimiento}</div>
                        <div class="modal-info-line"><strong>Kilometraje:</strong> ${r.kilometraje} km</div>
                        <div class="modal-info-line"><strong>Ciudad / Ubicación:</strong> <span style="color:#0ea5e9; font-weight:bold;">${ciudadStatus} - ${copeStatus}</span></div>
                        <div class="modal-info-line"><strong>Empleado (Chofer):</strong> ${r.empleado}</div>
                        <div class="modal-info-line"><strong>Depto:</strong> ${r.departamento}</div>
                        <div class="modal-info-line"><strong>Celular:</strong> ${r.celular}</div>
                        <div class="modal-info-line"><strong>Correo:</strong> ${emailStatus}</div>
                        <div class="modal-info-line full-width"><strong>Falla Reportada:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#112641; border-left:3px solid #f59e0b; border-radius:5px;">${r.falla}</div></div>
                        ${r.firma_chofer ? `
                        <div class="modal-info-line full-width" style="border-bottom: 1px solid #1f395a; padding-bottom: 5px; margin-top: 15px; margin-bottom: 5px; color: #10b981;"><strong>✍ FIRMA DEL OPERADOR / CHOFER</strong></div>
                        <div class="modal-info-line full-width" style="text-align: center;">
                            <img src="${r.firma_chofer}" alt="Firma del Chofer" style="background: white; border-radius: 8px; max-width: 300px; border: 2px solid #1f395a; padding: 5px;">
                        </div>` : ''}
                    </div>
                </div>
            `;
        }
    }

    let facturaFinalHtml = '';
    if (f.factura_folio && f.factura_pdf) {
        facturaFinalHtml = `
            <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #10b981; border-radius:8px;">
                <div style="color: #10b981; font-weight: bold; font-size:1.1em; margin-bottom:10px;">■ SECCIÓN 3: CIERRE CONTABLE (FACTURA FISCAL)</div>
                <div class="modal-info-line" style="font-size:16px;"><strong>Folio Fiscal Emitido:</strong> <span style="color:#10b981; font-weight:bold;">${f.factura_folio}</span></div>
                <div style="margin-top:15px;">
                    <button type="button" class="btn-success-modal" style="background:#10b981; border:none; padding:10px 20px; border-radius:8px; color:white; font-weight:bold; cursor:pointer;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.factura_pdf}')">📥 Ver PDF Oficial</button>
                </div>
            </div>
        `;
    }

    let docContableHtml = '';
    if (f.numero_doc50 && f.pdf_doc50) {
        docContableHtml = `
            <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #eab308; border-radius:8px;">
                <div style="color: #eab308; font-weight: bold; font-size:1.1em; margin-bottom:10px;">■ SECCIÓN 4: DOCUMENTO CONTABLE Y ARCHIVADO</div>
                <div class="modal-info-line" style="font-size:16px;"><strong>Número de Documento:</strong> <span style="color:#eab308; font-weight:bold;">${f.numero_doc50}</span></div>
                <div style="margin-top:15px;">
                    <button type="button" class="btn-success-modal" style="background:#eab308; border:none; padding:10px 20px; border-radius:8px; color:#111; font-weight:bold; cursor:pointer;" onclick="abrirVisorPDF('/static/facturas_archivos/${f.pdf_doc50}')">📥 Ver Documento Contable</button>
                </div>
            </div>
        `;
    }

    return `
        ${htmlReporte}
        <div style="margin-top:20px; padding:15px; background:#0b1c30; border:2px dashed #0284c7; border-radius:8px;">
            <div style="color: #0284c7; font-weight: bold; font-size:1.1em; margin-bottom:10px;">■ SECCIÓN 2: DIAGNÓSTICO Y COTIZACIÓN (TALLER)</div>
            <div class="form-grid" style="grid-template-columns: 1fr 1fr;">
                ${modo === 'lectura' ? `<div class="modal-info-line"><strong>Núm. Orden:</strong> ${ordenTexto}</div>` : ''}
                <div class="modal-info-line"><strong>Proveedor:</strong> ${f.proveedor}</div>
                <div class="modal-info-line"><strong>Fecha Ingreso:</strong> ${f.fecha}</div>
                <div class="modal-info-line"><strong>Unidad:</strong> ${f.unidad}</div>
                ${f.compania ? `<div class="modal-info-line"><strong>Compañía:</strong> <span style="color:#10b981; font-weight:bold;">${f.compania}</span></div>` : ''}
                <div class="modal-info-line"><strong>Responsable:</strong> ${f.responsable}</div>
                <div class="modal-info-line"><strong>Mantenimiento:</strong> ${f.mantenimiento}</div>
                <div class="modal-info-line"><strong>Precio s/IVA:</strong> $${precioBonito}</div>
                <div class="modal-info-line full-width"><strong>Título:</strong> ${f.titulo}</div>
                <div class="modal-info-line full-width"><strong>Retro:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${limpiarRetro(f.retro)}</div></div>
                <div class="modal-info-line full-width"><strong>Diagnóstico de Mecánico:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${f.diagnostico || 'Sin especificar'}</div></div>
                <div class="modal-info-line full-width"><strong>Descripción del Trabajo a Realizar:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${f.trabajo_realizar || 'Sin especificar'}</div></div>
            </div>
            <div style="margin-top:15px;">
                <strong>Cotizaciones (${f.fotos_cotizacion.length} archivos):</strong><br>
                <div style="display:flex; gap:10px; overflow-x:auto; padding:10px 0;">
                    ${f.fotos_cotizacion.map(foto => (foto.endsWith('.pdf') ? `<button type="button" style="background:#0284c7; color:white; border:none; border-radius:5px; padding:10px 15px; cursor:pointer; font-weight:bold; font-size: 0.9em; display:flex; align-items:center; gap:5px;" onclick="abrirVisorPDF('/static/facturas_archivos/${foto}')">📄 Ver PDF Cotización</button>` : `<img src="/static/facturas_archivos/${foto}" style="height:70px; border-radius:5px; border:2px solid #0284c7; cursor:zoom-in;" onclick="abrirLightbox('/static/facturas_archivos/${foto}')">`)).join('')}
                </div>
                <strong>Evidencias (${f.fotos_evidencia.length} archivos):</strong><br>
                <div style="display:flex; gap:10px; overflow-x:auto; padding:10px 0;">
                    ${f.fotos_evidencia.map(foto => `<img src="/static/facturas_archivos/${foto}" style="height:70px; border-radius:5px; border:2px solid #40916c; cursor:zoom-in;" onclick="abrirLightbox('/static/facturas_archivos/${foto}')">`).join('')}
                </div>
            </div>
        </div>
        ${facturaFinalHtml}
        ${docContableHtml}
    `;
}

function abrirRevisionAdmin(idFactura) { 
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); 
    if (!f) return; 
    document.getElementById('rev-id-admin').value = f.id; 
    document.getElementById('revision-contenido-admin').innerHTML = generarHtmlDetalles(f, 'edicion', formatearMoneda(f.precio)); 
    document.getElementById('input-num-orden').value = ''; 
    document.getElementById('num-cotizacion-admin').value = '';
    document.getElementById('pdf-cotizacion-admin').value = '';
    validarOrden(); 
    document.getElementById('modal-revision-admin').style.display = 'flex'; 
}

function validarOrden() { 
    let inputNumOrden = document.getElementById('input-num-orden').value.trim(); 
    let inputCotizacion = document.getElementById('num-cotizacion-admin').value.trim();
    let pdfCotizacion = document.getElementById('pdf-cotizacion-admin').files[0];
    let btn = document.getElementById('btn-confirmar-admin'); 
    let previewContainer = document.getElementById('preview-cotizacion-admin-container');
    
    if (pdfCotizacion && pdfCotizacion.type === 'application/pdf') {
        previewContainer.style.display = 'block';
        previewContainer.innerHTML = `<iframe src="${URL.createObjectURL(pdfCotizacion)}" style="width:100%; height:200px; border:1px solid #1f395a; border-radius:5px;"></iframe>`;
    } else {
        if (previewContainer) {
            previewContainer.style.display = 'none';
            previewContainer.innerHTML = '';
        }
    }
    
    if (inputNumOrden.length > 0 && inputCotizacion.length > 0 && pdfCotizacion) { 
        btn.disabled = false; btn.style.opacity = '1'; btn.style.cursor = 'pointer'; 
    } else { 
        btn.disabled = true; btn.style.opacity = '0.5'; btn.style.cursor = 'not-allowed'; 
    } 
}

function confirmarFacturaAdmin() {
    let num_orden = document.getElementById('input-num-orden').value.trim();
    let num_cotizacion = document.getElementById('num-cotizacion-admin').value.trim();
    let pdf_cotizacion = document.getElementById('pdf-cotizacion-admin').files[0];
    let id_fac = document.getElementById('rev-id-admin').value;
    
    if (!confirm(`¿Asignar la orden ${num_orden}?`)) return;

    mostrarLoaderDinamico("Validando orden...", "Generando código oficial ⏳");

    let formData = new FormData();
    formData.append('id', id_fac);
    formData.append('numero_orden', num_orden);
    formData.append('numero_cotizacion', num_cotizacion);
    formData.append('pdf_cotizacion', pdf_cotizacion);

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

    document.getElementById('prev-unidad').innerText = f.unidad; document.getElementById('prev-responsable').innerText = f.responsable; document.getElementById('prev-telefono').innerText = f.telefono; document.getElementById('prev-fecha').innerText = f.fecha; document.getElementById('prev-titulo').innerText = f.titulo;
    document.getElementById('prev-retro').innerText = limpiarRetro(f.retro);
    document.getElementById('prev-diagnostico').innerText = f.diagnostico || 'Sin especificar'; document.getElementById('prev-trabajo-realizar').innerText = f.trabajo_realizar || 'Sin especificar'; document.getElementById('prev-mantenimiento').innerText = f.mantenimiento; document.getElementById('prev-precio').innerText = formatearMoneda(f.precio);

    const contCotizacion = document.getElementById('prev-cotizaciones-container'); const contEvidencia = document.getElementById('prev-evidencias-container');
    contCotizacion.innerHTML = ''; contEvidencia.innerHTML = '';
    f.fotos_cotizacion.forEach(foto => { let ruta = `/static/facturas_archivos/${foto}`; if (foto.endsWith('.pdf')) { contCotizacion.innerHTML += `<div class="pdf-image-container"><div style="font-size:40px; color:#ef4444; margin-bottom:10px;">📄</div><p class="pdf-anexo-label">Cotización PDF: ${foto}</p></div>`; } else { contCotizacion.innerHTML += `<div class="pdf-image-container"><img src="${ruta}" class="pdf-anexo-img"><p class="pdf-anexo-label">Cotización: ${foto}</p></div>`; } });
    f.fotos_evidencia.forEach(foto => { let ruta = `/static/facturas_archivos/${foto}`; contEvidencia.innerHTML += `<div class="pdf-image-container"><img src="${ruta}" class="pdf-anexo-img"><p class="pdf-anexo-label">Evidencia: ${foto}</p></div>`; });

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
    document.getElementById('input_nuevo_mantenimiento').value = reporteSeleccionado.mantenimiento;
    document.getElementById('input_nueva_retro').value = `REPORTE ORIGINAL DEL CHOFER: ${reporteSeleccionado.falla}`;
}

function enviarFacturaDefinitiva() {
    if (!confirm("⚠️ ¿Estás seguro de enviar esta cotización a revisión?")) return;
    let inputPrecio = document.querySelector('input[name="precio"]'); inputPrecio.value = inputPrecio.value.replace(/[^0-9.]/g, '');
    let formData = new FormData(document.getElementById('form-nueva-factura'));

    let numRep = '';
    if (document.getElementById('hidden_numero_reporte')) numRep = document.getElementById('hidden_numero_reporte').value;
    if (numRep && numRep !== "") {
        let retroUsuario = formData.get('retro');
        formData.set('retro', `[TICKET:${numRep}]\n${retroUsuario}`);
    }

    mostrarLoaderDinamico("Enviando cotización a revisión...", "Notificando a Automotriz 📧");

    fetch('/api/facturas/nueva', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') { document.getElementById('modal-previsualizacion-factura').style.display = 'none'; document.getElementById('modal-ver-reporte-prov').style.display = 'none'; cargarFacturas(); if (document.getElementById('vista-reportes-prov') && document.getElementById('vista-reportes-prov').style.display !== 'none') { cargarReportesProv(); } }
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });
}

function abrirModalDoc50(id) {
    document.getElementById('hidden-doc50-id').value = id;
    document.getElementById('input-num-doc50').value = '';
    document.getElementById('pdf-doc50').value = '';
    document.getElementById('modal-doc50').style.display = 'flex';
}

function subirDoc50() {
    let id = document.getElementById('hidden-doc50-id').value;
    let numDoc50 = document.getElementById('input-num-doc50').value.trim();
    let fileInput = document.getElementById('pdf-doc50');
    
    if (!numDoc50) { alert("Por favor, ingrese el número del Documento Contable."); return; }
    if (fileInput.files.length === 0) { alert("Por favor, seleccione el PDF del Documento Contable."); return; }

    let formData = new FormData();
    formData.append('id', id);
    formData.append('numero_doc50', numDoc50);
    formData.append('pdf', fileInput.files[0]);

    mostrarLoaderDinamico("Subiendo Documento Contable...", "Finalizando proceso ⏳");
    fetch('/api/facturas/doc50', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        if (data.status === 'success') {
            document.getElementById('modal-doc50').style.display = 'none';
            cargarFacturas();
        }
    })
    .catch(err => {
        ocultarLoaderDinamico();
        console.error("Error al subir Doc Contable:", err);
    });
}

function abrirModalValidacionFiscal(id, folio, pdf, unidad) {
    document.getElementById('val-factura-id').value = id;
    document.getElementById('val-folio-text').innerText = folio;
    document.getElementById('val-unidad-text').innerText = unidad;
    document.getElementById('val-pdf-frame').src = '/static/facturas_archivos/' + pdf;

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
    document.getElementById('input-numero-doc-contable').value = '';
    document.getElementById('input-pdf-doc-contable').value = '';
    document.getElementById('nombre-pdf-doc-contable').textContent = 'Ningún archivo seleccionado';
    document.getElementById('modal-doc-contable').style.display = 'flex';
}

function subirDocContable() {
    const id = document.getElementById('hidden-doc-contable-id').value;
    const numero = document.getElementById('input-numero-doc-contable').value;
    const archivo = document.getElementById('input-pdf-doc-contable').files[0];

    if (!numero || !archivo) {
        alert("Por favor ingrese el número y seleccione el archivo PDF.");
        return;
    }

    const formData = new FormData();
    formData.append('id', id);
    formData.append('numero_doc50', numero);
    formData.append('pdf', archivo);

    mostrarLoaderDinamico("Guardando Documento Contable...", "Finalizando y Archivando Ticket 🗃️");

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
