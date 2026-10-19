// cotizaciones_10k.js
function esTicketCorporativo(f) {
    if (!f) return false;
    let cia = String(f.compania || '').toLowerCase();
    if (cia.includes('corporativo')) return true;
    let cli = String(f.cliente || '').toLowerCase();
    if (cli.includes('corporativo')) return true;
    let dep = String(f.departamento || '').toLowerCase();
    if (dep.includes('corporativo')) return true;
    if (f.reporte_inicial) {
        let rCia = String(f.reporte_inicial.compania || '').toLowerCase();
        let rCli = String(f.reporte_inicial.cliente || '').toLowerCase();
        let rDep = String(f.reporte_inicial.departamento || '').toLowerCase();
        if (rCia.includes('corporativo') || rCli.includes('corporativo') || rDep.includes('corporativo')) return true;
    }
    let retro = String(f.retro || '').toLowerCase();
    if (retro.includes('corporativo')) return true;
    return false;
}

function verCotizacionesMas10000() {
    cambiarVistaAdmin('cotizaciones-10k');
    cargarCotizaciones10k();
}

let facturas10kGlobal = [];
let cancelacion10kActiva = false;

async function cargarCotizaciones10k() {
    const tbody = document.getElementById('tabla-cotizaciones-10k');
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Cargando cotizaciones...</td></tr>';

    try {
        const response = await fetch('/api/facturas/lista');
        const result = await response.json();

        if (result.facturas) {
            const facturas = result.facturas;
            const pendientes = facturas.filter(f => {
                const p = parseFloat(f.precio_estimado || f.precio || 0);
                let ap10k = f.aprobado_admin_10k !== undefined ? f.aprobado_admin_10k : false;
                let supAsignado = f.aprobado_admin === true;
                let cancelado = f.estado === 'Cancelado_Cotizacion_Cara' || f.estado === 'Archivado' || f.estado === 'Rechazado_Con_Recomendaciones';
                return p >= 10001 && ap10k === false && supAsignado && !cancelado;
            });

            facturas10kGlobal = pendientes;

            if (pendientes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#94a3b8;">No hay cotizaciones pendientes mayores a $10,000.</td></tr>';
                return;
            }

            let subrolActual = document.getElementById('subrol-actual') ? document.getElementById('subrol-actual').value.trim() : '';

            tbody.innerHTML = '';
            pendientes.forEach(f => {
                let pFormat = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';
                let cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [{ precio: f.precio }];
                let indStr = cots.map((c, i) => `Cot ${i + 1}: $${parseFloat(c.precio || 0).toLocaleString('en-US')}`).join('<br>');
                let tdPrecioInd = `<td><small style="color:#a3b1c6;">${indStr}</small></td>`;

                let btnStyle = "width:100% !important; height:38px !important; min-height:38px !important; max-height:38px !important; font-size:12px !important; font-weight:bold !important; padding:0 !important; margin:0 0 5px 0 !important; border-radius:5px !important; box-sizing:border-box !important; display:flex !important; align-items:center !important; justify-content:center !important; text-align:center !important; border:none !important; cursor:pointer !important; line-height:normal !important; color:white !important; transition: opacity 0.2s !important;";

                let hoverStr = `onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'"`;

                let btnVerDetalles = `<button style="${btnStyle} background:#0ea5e9 !important;" ${hoverStr} onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                
                // --- LÓGICA DE SUPLENCIA Y EXCEPCIÓN CORPORATIVA ---
                let esCorp = esTicketCorporativo(f);
                let pNum = parseFloat(f.precio_estimado || f.precio || 0);
                let btnAprobar = '';

                if (subrolActual === 'Supervisor') {
                    // El Supervisor actúa bajo cobertura de ausencia del Administrador
                    if (pNum >= 10001 && esCorp) {
                        // REGLA DE COTIZACIONES (EXCEPCIÓN CORPORATIVA):
                        // Si la cotización es > 10,000 y pertenece a 'Corporativos', la cobertura se deshabilita/oculta
                        btnAprobar = `<button class="btn-cobertura-disabled" disabled style="${btnStyle}" title="Excepción Corporativa: Prohibida suplencia en cotizaciones > $10,000 de Corporativos. Requiere Administrador titular.">🔒 Flujo Estricto Corp (Sin Cobertura)</button>
                        <span class="badge-estricto-corp">Requiere Admin Titular</span>`;
                    } else {
                        btnAprobar = `<button class="btn-cobertura" style="${btnStyle}" ${hoverStr} onclick="accion10k('${f.id}', 'aprobar', true)">🛡️ Asumir Proceso (Aprobar a Corp)</button>`;
                    }
                } else {
                    // Administrador titular (o Jefatura)
                    btnAprobar = `<button style="${btnStyle} background:#10b981 !important;" ${hoverStr} onclick="accion10k('${f.id}', 'aprobar', false)">✔️ Aprobar a Corporativos</button>`;
                }

                let btnCaras = `<button style="${btnStyle} background:#b91c1c !important;" ${hoverStr} onclick="abrirCancelacion10k('${f.id}')">Cancelar Ticket (Cara)</button>`;
                let acciones = `<div style="display:flex; flex-direction:column;">${btnVerDetalles}${btnAprobar}${btnCaras}</div>`;

                let idRepForTable = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : (f.id || 'S/T');
                let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                tbody.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idRepForTable}</span>${badgeCaras}</td><td>${f.fecha}</td><td><strong>${f.proveedor}</strong></td><td>${f.unidad}</td><td>${f.titulo}</td><td><strong>$${pFormat} MXN</strong></td>${tdPrecioInd}<td>${acciones}</td></tr>`;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#ef4444;">Error al cargar datos del servidor.</td></tr>`;
        }
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#ef4444;">Error de conexión.</td></tr>`;
    }
}

function accion10k(id, accion, esSuplencia = false) {
    if (accion === 'aprobar') {
        abrirModalAprobar10k(id, esSuplencia);
    }
}

function abrirModalAprobar10k(id, esSuplencia = false) {
    const f = facturas10kGlobal.find(x => String(x.id) === String(id));
    if (!f) return;

    let cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [{ precio: f.precio, titulo: f.titulo }];
    const fmt = (val) => parseFloat(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    let html = `
        <div style="font-size:13px; color:#94a3b8; margin-bottom:15px; border-bottom:1px solid #1f395a; padding-bottom:10px;">
            Unidad: <strong style="color:#0ea5e9;">${f.unidad || 'S/N'}</strong> &nbsp;|&nbsp; 
            Proveedor: <strong style="color:#e2e8f0;">${f.proveedor || 'N/A'}</strong>
        </div>
    `;

    if (cots.length === 1) {
        let c = cots[0];
        let precio = fmt(c.precio !== undefined ? c.precio : f.precio);
        let titulo = c.titulo || f.titulo || 'General';
        html += `
            <div style="background:#112641; border:1px solid #1f395a; border-radius:8px; padding:15px; margin-bottom:20px;">
                <div style="color:#94a3b8; font-size:13px; margin-bottom:8px;">Cotización: <strong style="color:#e2e8f0;">${titulo}</strong></div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#cbd5e1; font-weight:bold; font-size:14px;">Precio Cotizado (Sin IVA):</span>
                    <span style="color:#10b981; font-weight:bold; font-size:18px;">$${precio} MXN</span>
                </div>
            </div>
        `;
    } else {
        let total = 0;
        let cotsHtml = cots.map((c, idx) => {
            let pNum = parseFloat(c.precio || 0);
            total += pNum;
            let precio = fmt(pNum);
            let titulo = c.titulo || `Cotización ${idx + 1}`;
            return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px dashed #1f395a;">
                    <span style="color:#cbd5e1; font-size:13px;">Cotización ${idx + 1}: <strong style="color:#e2e8f0;">${titulo}</strong></span>
                    <span style="color:#f59e0b; font-weight:bold; font-size:14px;">$${precio} MXN</span>
                </div>
            `;
        }).join('');

        html += `
            <div style="background:#112641; border:1px solid #1f395a; border-radius:8px; padding:15px; margin-bottom:20px;">
                <div style="color:#94a3b8; font-size:13px; margin-bottom:8px; font-weight:bold; border-bottom:1px solid #1f395a; padding-bottom:5px;">Desglose de Cotizaciones:</div>
                ${cotsHtml}
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding-top:8px; border-top:1px solid #334155;">
                    <span style="color:#e2e8f0; font-weight:bold; font-size:15px;">Precio Total:</span>
                    <span style="color:#10b981; font-weight:bold; font-size:19px;">$${fmt(total || f.precio)} MXN</span>
                </div>
            </div>
        `;
    }

    let textoBoton = esSuplencia ? '🛡️ Asumir Proceso y Aprobar a Corp' : '✔️ Aprobar a Corporativos';

    html += `
        <div style="display:flex; gap:10px; margin-top:20px;">
            <button class="btn-danger" style="flex:1; padding:12px; font-size:13px; font-weight:bold; background:#ef4444 !important; color:white; border:none; border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;" onclick="rechazarDesdeModalAprobar10k('${f.id}')">
                ✖ Rechazar y Sugerir Precios
            </button>
            <button class="btn-success" style="flex:1; padding:12px; font-size:13px; font-weight:bold; background:#10b981 !important; color:white; border:none; border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;" onclick="confirmarAprobacion10k('${f.id}', ${esSuplencia})">
                ${textoBoton}
            </button>
        </div>
    `;

    let modal = document.getElementById('modal-aprobar-10k');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-aprobar-10k';
        modal.className = 'modal-overlay';
        modal.style.zIndex = '9999999';
        modal.innerHTML = `
            <div class="modal-box" style="max-width: 480px; background: #0b1c30; border: 1px solid #1f395a; border-radius: 12px; padding: 25px;">
                <button class="btn-close-modal" onclick="cerrarModalAprobar10k()">×</button>
                <h3 class="modal-header" style="color: #10b981; margin-top: 0; margin-bottom: 15px; font-size: 1.25em;">Aprobar a Corporativos</h3>
                <div id="contenido-aprobar-10k-dinamico"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('contenido-aprobar-10k-dinamico').innerHTML = html;
    modal.style.display = 'flex';
}

function cerrarModalAprobar10k() {
    let modal = document.getElementById('modal-aprobar-10k');
    if (modal) modal.style.display = 'none';
}

function rechazarDesdeModalAprobar10k(id) {
    cerrarModalAprobar10k();
    abrirModalRechazo10kDinamico(id);
}

function confirmarAprobacion10k(id, esSuplencia = false) {
    let msgConfirm = esSuplencia
        ? "⚠️ ¿Deseas ASUMIR EL PROCESO (Autorizar por Ausencia) para aprobar esta cotización en suplencia del Administrador?\n\nLa cotización pasará formalmente a Corporativos."
        : "¿Seguro que deseas APROBAR esta cotización? Pasará a Corporativos.";
    
    if (!confirm(msgConfirm)) return;

    cerrarModalAprobar10k();

    if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Procesando...", "Enviando a Corporativos...");
    }
    enviarDecision10k(id, 'aprobar', "");
}

function abrirModalRechazo10kDinamico(id) {
    cerrarModalAprobar10k();
    const f = facturas10kGlobal.find(x => String(x.id) === String(id));
    if (!f) return;

    let html = `<div style="color: #94a3b8; margin-bottom:15px; font-size:14px;">Ingresa el precio recomendado para cada cotización (opcional) y el motivo general del rechazo.</div>`;

    let cots = f.cotizaciones || [{ precio: f.precio }];
    cots.forEach((c, idx) => {
        let precioActual = parseFloat(c.precio || 0).toLocaleString('en-US');
        let titulo = c.titulo || 'Sin Título';
        html += `<div style="margin-bottom:15px; padding:15px; background:#1e293b; border:1px solid #334155; border-radius:8px;"><div style="font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Cotización ${idx + 1}: ${titulo}</div><div style="font-size:13px; color:#94a3b8; margin-bottom:10px;">Precio cotizado: <span style="font-weight:bold; color:#f59e0b;">$${precioActual} MXN</span></div><label style="display:block; font-size:13px; color:#cbd5e1; margin-bottom:5px;">Precio Recomendado ($):</label><input type="number" class="input-precio-rec-10k" data-idx="${idx}" placeholder="Ej. 1500" style="width:100%; padding:8px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;"></div>`;
    });

    html += `<div style="margin-top:20px;"><label style="display:block; font-size:14px; font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Motivo General del Rechazo: <span style="color:#ef4444;">*</span></label><textarea id="rechazo-10k-motivo" rows="4" placeholder="Escribe aquí el motivo del rechazo..." style="width:100%; padding:10px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;"></textarea></div><button class="btn-danger" style="margin-top:15px; width:100%;" onclick="enviarRechazo10k()">Confirmar Rechazo</button>`;

    let modal = document.getElementById('modal-rechazar-10k');
    let modalBox = modal.querySelector('.modal-box');
    modalBox.innerHTML = `<button class="btn-close-modal" onclick="document.getElementById('modal-rechazar-10k').style.display='none'">×</button><h3 class="modal-header">Rechazar Cotización (Sugerir Precios)</h3><input type="hidden" id="hidden-rechazar-10k-id" value="${id}"><div id="contenido-rechazo-10k-dinamico">${html}</div>`;

    modal.style.display = 'flex';
}

function enviarRechazo10k() {
    let id = document.getElementById('hidden-rechazar-10k-id').value;
    let motivo = document.getElementById('rechazo-10k-motivo').value.trim();
    if (!motivo) { alert("Debes escribir el motivo general del rechazo."); return; }

    let preciosRec = [];
    document.querySelectorAll('.input-precio-rec-10k').forEach(input => {
        let val = input.value.trim();
        if (val !== "") {
            preciosRec.push({
                idx: input.getAttribute('data-idx'),
                precio_recomendado: val
            });
        }
    });

    if (!confirm("¿Estás seguro de que deseas rechazar esta cotización y enviar los nuevos precios recomendados al taller?")) {
        return;
    }

    const modalRechazo = document.getElementById('modal-rechazar-10k');
    if (modalRechazo) modalRechazo.style.display = 'none';

    if (typeof mostrarLoaderDinamico === 'function') mostrarLoaderDinamico("Procesando...", "Notificando al Supervisor y Taller...");
    enviarDecision10k(id, 'rechazar', motivo, preciosRec);
}

function abrirCancelacion10k(id) {
    cancelacion10kActiva = true;
    document.getElementById('rev-id-admin').value = id;
    let modal = document.getElementById('modal-confirmar-cancelacion');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        alert("El modal de cancelación no está disponible.");
    }
}

function ejecutarCancelacionTicket10k() {
    let id = document.getElementById('rev-id-admin').value;
    if (!id) return;
    if (typeof mostrarLoaderDinamico === 'function') mostrarLoaderDinamico("Procesando...", "Moviendo a Cotizaciones Caras...");
    enviarDecision10k(id, 'caras', "");
}

async function enviarDecision10k(id, accion, mensaje, preciosRec = []) {
    try {
        let form = new FormData();
        form.append('id', id);
        form.append('accion', accion);
        form.append('mensaje', mensaje);

        if (preciosRec && preciosRec.length > 0) {
            preciosRec.forEach((p, idx) => {
                form.append(`precio_rec_${idx}`, p.precio_recomendado);
            });
        }

        const res = await fetch('/api/facturas/aprobar_10k', {
            method: 'POST',
            body: form
        });
        const data = await res.json();

        document.getElementById('modal-rechazar-10k').style.display = 'none';

        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();

        setTimeout(() => {
            if (data.status === 'success') {
                alert(data.message);
                cargarCotizaciones10k();
                if (typeof cargarFacturas === 'function') cargarFacturas();
            } else {
                alert("Error: " + data.message);
            }
        }, 50);
    } catch (e) {
        console.error(e);
        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();
        setTimeout(() => alert("Error de conexión al procesar la decisión."), 50);
    }
}
