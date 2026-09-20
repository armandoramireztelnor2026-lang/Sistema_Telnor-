// cotizaciones_10k.js
function verCotizacionesMas10000() {
    // Hide all views
    const vistas = ['facturas', 'facturas-finales', 'documentos-contables', 'pendientes', 'reportes', 'dashboard', 'seccion-reportes', 'archivo', 'unidades', 'cotizaciones-10k'];
    vistas.forEach(v => {
        let el = document.getElementById('vista-' + v);
        if (el) el.style.display = 'none';
    });

    // Show the new view
    document.getElementById('vista-cotizaciones-10k').style.display = 'block';

    // Fetch data
    cargarCotizaciones10k();
}

let facturas10kGlobal = [];

async function cargarCotizaciones10k() {
    const tbody = document.getElementById('tabla-cotizaciones-10k');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Cargando cotizaciones...</td></tr>';

    try {
        const response = await fetch('/api/facturas/lista');
        const result = await response.json();

        if (result.facturas) {
            const facturas = result.facturas;

            // Filter: price >= 10001 AND admin hasn't approved it yet AND supervisor has assigned numbers
            const pendientes = facturas.filter(f => {
                const p = parseFloat(f.precio_estimado || f.precio || 0);
                let ap10k = f.aprobado_admin_10k !== undefined ? f.aprobado_admin_10k : false;
                let supAsignado = f.aprobado_admin === true; // Supervisor ya procesó y asignó números
                // Excluir tickets cancelados
                let cancelado = f.estado === 'Cancelado_Cotizacion_Cara' || f.estado === 'Archivado';
                return p >= 10001 && ap10k === false && supAsignado && !cancelado;
            });

            facturas10kGlobal = pendientes;

            if (pendientes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#94a3b8;">No hay cotizaciones pendientes mayores a $10,000.</td></tr>';
                return;
            }

            tbody.innerHTML = '';
            pendientes.forEach(f => {
                let pFormat = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';

                // Precios individuales
                let cots = f.cotizaciones && f.cotizaciones.length > 0 ? f.cotizaciones : [{ precio: f.precio }];
                let indStr = cots.map((c, i) => `Cot ${i + 1}: $${parseFloat(c.precio || 0).toLocaleString('en-US')}`).join('<br>');
                let tdPrecioInd = `<td><small style="color:#a3b1c6;">${indStr}</small></td>`;

                let btnStyle = "width:100% !important; font-size:12px !important; font-weight:bold !important; padding:0 !important; margin-bottom:5px !important; border-radius:5px !important; box-sizing:border-box !important; height:36px !important; min-height:36px !important; max-height:36px !important; display:flex !important; align-items:center !important; justify-content:center !important; text-align:center !important; border:none !important; cursor:pointer !important; line-height:1.2 !important; color:white !important;";

                let btnAprobar = `<button class="btn-success" style="${btnStyle}" onclick="accion10k('${f.id}', 'aprobar')">✔️ Aprobar a Corporativos</button>`;
                let btnRechazar = `<button class="btn-danger" style="${btnStyle}" onclick="abrirModalRechazo10kDinamico('${f.id}')">✖ Rechazar (Sugerir Precios)</button>`;
                let btnCaras = `<button class="btn-danger-modal" style="${btnStyle}" onclick="abrirCancelacion10k('${f.id}')">Cancelar Ticket (Cara)</button>`;

                let acciones = `<div style="display:flex; flex-direction:column;">${btnAprobar}${btnRechazar}${btnCaras}</div>`;

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${f.id}</strong></td>
                        <td>${f.fecha}</td>
                        <td><strong>${f.proveedor}</strong></td>
                        <td>${f.unidad}</td>
                        <td>${f.titulo}</td>
                        <td><strong>$${pFormat} MXN</strong></td>
                        ${tdPrecioInd}
                        <td>${acciones}</td>
                    </tr>
                `;
            });

        } else {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#ef4444;">Error al cargar datos del servidor.</td></tr>`;
        }
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#ef4444;">Error de conexión.</td></tr>`;
    }
}

function accion10k(id, accion) {
    if (accion === 'aprobar') {
        if (!confirm("¿Seguro que deseas APROBAR esta cotización? Pasará a Corporativos.")) return;
        enviarDecision10k(id, accion, "");
    }
}

function abrirModalRechazo10kDinamico(id) {
    const f = facturas10kGlobal.find(x => String(x.id) === String(id));
    if (!f) return;

    document.getElementById('hidden-rechazar-10k-id').value = id;

    let html = `<div style="color: #94a3b8; margin-bottom:15px; font-size:14px;">Ingresa el precio recomendado para cada cotización (opcional) y el motivo general del rechazo.</div>`;

    let cots = f.cotizaciones || [{ precio: f.precio }];
    cots.forEach((c, idx) => {
        let precioActual = parseFloat(c.precio || 0).toLocaleString('en-US');
        let titulo = c.titulo || 'Sin Título';
        html += `
        <div style="margin-bottom:15px; padding:15px; background:#1e293b; border:1px solid #334155; border-radius:8px;">
            <div style="font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Cotización ${idx + 1}: ${titulo}</div>
            <div style="font-size:13px; color:#94a3b8; margin-bottom:10px;">Precio cotizado: <span style="font-weight:bold; color:#f59e0b;">$${precioActual} MXN</span></div>
            <label style="display:block; font-size:13px; color:#cbd5e1; margin-bottom:5px;">Precio Recomendado ($):</label>
            <input type="number" class="input-precio-rec-10k" data-idx="${idx}" placeholder="Ej. 1500" style="width:100%; padding:8px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;">
        </div>
        `;
    });

    html += `
    <div style="margin-top:20px;">
        <label style="display:block; font-size:14px; font-weight:bold; color:#e2e8f0; margin-bottom:5px;">Motivo General del Rechazo: <span style="color:#ef4444;">*</span></label>
        <textarea id="rechazo-10k-motivo" rows="4" placeholder="Escribe aquí el motivo del rechazo y las observaciones generales..." style="width:100%; padding:10px; background:#0f172a; color:white; border:1px solid #334155; border-radius:5px;"></textarea>
    </div>
    <button class="btn-danger" style="margin-top:15px; width:100%;" onclick="enviarRechazo10k()">Confirmar Rechazo</button>
    `;

    // Reutilizamos el cuerpo del modal de rechazo original modificando su interior
    let modal = document.getElementById('modal-rechazar-10k');
    let modalBox = modal.querySelector('.modal-box');

    // Limpiamos contenido anterior y ponemos el nuevo dinámico
    modalBox.innerHTML = `
        <button class="btn-close-modal" onclick="document.getElementById('modal-rechazar-10k').style.display='none'">×</button>
        <h3 class="modal-header">Rechazar Cotización (Sugerir Precios)</h3>
        <input type="hidden" id="hidden-rechazar-10k-id" value="${id}">
        <div id="contenido-rechazo-10k-dinamico">${html}</div>
    `;

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

    if (typeof mostrarLoaderDinamico === 'function') mostrarLoaderDinamico("Procesando...", "Notificando al Supervisor...");
    enviarDecision10k(id, 'rechazar', motivo, preciosRec);
}

function abrirCancelacion10k(id) {
    document.getElementById('hidden-caras-10k-id').value = id;

    // Usar el mismo modal de cancelación de cotizaciones caras
    let modal = document.getElementById('modal-confirmar-cancelacion');
    if (modal) {
        // Guardamos el id temporalmente
        document.getElementById('rev-id-admin').value = id;
        modal.style.display = 'flex';
    } else {
        alert("El modal de cancelación no está disponible.");
    }
}

async function enviarDecision10k(id, accion, mensaje, preciosRec = []) {
    try {
        let form = new FormData();
        form.append('id', id);
        form.append('accion', accion);
        form.append('mensaje', mensaje);

        // Agregar precios recomendados al formulario
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

        if (typeof cerrarLoaderDinamico === 'function') cerrarLoaderDinamico();

        if (data.status === 'success') {
            alert(data.message);
            cargarCotizaciones10k();
            if (typeof cargarFacturas === 'function') cargarFacturas();
        } else {
            alert("Error: " + data.message);
        }
    } catch (e) {
        console.error(e);
        if (typeof cerrarLoaderDinamico === 'function') cerrarLoaderDinamico();
        alert("Error de conexión al procesar la decisión.");
    }
}
