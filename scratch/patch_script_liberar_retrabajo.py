# -*- coding: utf-8 -*-

with open('static/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update cambiarVistaAdmin vistas array and dispatch
t_vistas = """    const vistas = ['facturas', 'facturas-finales', 'documentos-contables', 'liberar-doc-contable', 'pendientes', 'accesos', 'lista-prov', 'lista-corp', 'lista-admin', 'reportes', 'seccion-reportes', 'archivo', 'unidades', 'panel-control', 'cotizaciones-10k', 'ciudades-copes', 'analitica', 'retrabajo', 'tiempo-garantia', 'flujo-trabajo'];"""
r_vistas = """    const vistas = ['facturas', 'facturas-finales', 'documentos-contables', 'liberar-doc-contable', 'pendientes', 'accesos', 'lista-prov', 'lista-corp', 'lista-admin', 'reportes', 'seccion-reportes', 'archivo', 'unidades', 'panel-control', 'cotizaciones-10k', 'ciudades-copes', 'analitica', 'retrabajo', 'tiempo-garantia', 'flujo-trabajo', 'liberar-retrabajo'];"""

t_vids = """    if (vista === 'flujo_trabajo') vistaId = 'flujo-trabajo';"""
r_vids = """    if (vista === 'flujo_trabajo') vistaId = 'flujo-trabajo';
    if (vista === 'liberar_retrabajo') vistaId = 'liberar-retrabajo';"""

t_vcalls = """    if (vista === 'cotizaciones-10k' && typeof cargarCotizaciones10k === 'function') cargarCotizaciones10k();"""
r_vcalls = """    if (vista === 'cotizaciones-10k' && typeof cargarCotizaciones10k === 'function') cargarCotizaciones10k();
    if (vista === 'liberar-retrabajo' || vista === 'liberar_retrabajo') {
        if (typeof cargarLiberarRetrabajosSupervisor === 'function') cargarLiberarRetrabajosSupervisor();
    }
    if (typeof actualizarBadgeLiberarRetrabajoSupervisor === 'function') {
        actualizarBadgeLiberarRetrabajoSupervisor();
    }"""

# 2. Update marcarRetrabajoFinalizado
t_marcar = """    const confirmar = confirm(`⚠️ ¿Confirmas que los trabajos de retrabajo / garantía para el ticket ${ticketId} han sido FINALIZADOS por el taller?\\n\\nAl confirmar, la orden de retrabajo concluirá y se desbloquearán las acciones del ticket.`);
    if (!confirmar) return;

    try {
        let res = await fetch('/api/garantia/taller/finalizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        let data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Retrabajo finalizado con éxito.');"""

r_marcar = """    const confirmar = confirm(`⚠️ ¿Confirmas que los trabajos de retrabajo / garantía para el ticket ${ticketId} han sido concluidos por el taller?\\n\\nAl confirmar, el ticket se enviará a Supervisión al módulo "Liberar/Retrabajo" para su validación final.`);
    if (!confirmar) return;

    try {
        let res = await fetch('/api/garantia/taller/finalizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        let data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'La unidad ha sido marcada como lista y enviada a Supervisión para su liberación.');"""

# 3. New implementations for Liberar/Retrabajo
new_functions = """

// ============================================================
// FUNCIONES PARA EL MÓDULO SUPERVISOR: LIBERAR / RETRABAJO
// ============================================================

window.cargarLiberarRetrabajosSupervisor = async function() {
    const tbody = document.getElementById('tabla-liberar-retrabajo');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:20px; color:#94a3b8;">Cargando retrabajos listos para liberar...</td></tr>';

    try {
        const res = await fetch('/api/garantia/supervisor/por_liberar');
        const data = await res.json();
        const retrabajos = data.retrabajos || [];

        const badge = document.getElementById('badge-liberar-retrabajo');
        if (badge) {
            if (retrabajos.length > 0) {
                badge.innerText = retrabajos.length;
                badge.style.display = 'inline-flex';
                badge.style.alignItems = 'center';
                badge.style.justifyContent = 'center';
            } else {
                badge.style.display = 'none';
            }
        }

        if (retrabajos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:25px; color:#94a3b8;">No hay unidades con retrabajo concluido por el taller pendientes de liberación.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        retrabajos.forEach(r => {
            let ticketId = r.ticket_original || r.ticket || r.id;
            let unidadStr = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            let fechaReasig = r.fecha_reasignacion || r.fecha_solicitud || '--';
            let fechaListoTaller = r.fecha_finalizacion_taller || '--';
            let taller = r.proveedor || (r.seccion_2 && r.seccion_2.proveedor) || 'Taller';
            let motivoLimpio = String(r.motivo_chofer || 'Sin motivo reportado').trim().replace(/^["'«»“”„]+|["'«»“”„]+$/g, '').trim();

            let badgeEstado = `<span style="background:rgba(56, 189, 248, 0.15); color:#38bdf8; border:1px solid #38bdf8; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:0.82rem; display:inline-block; white-space:nowrap;">🔧 Listo en Taller</span>`;

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${fechaReasig}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #4ade80;">${fechaListoTaller}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #ffffff;">${unidadStr}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #38bdf8; font-weight: 600;">${r.cope || '--'}</span></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${r.ciudad || '--'}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #cbd5e1;">${taller}</span></td>
                    <td style="white-space: normal; min-width: 260px; max-width: 420px; vertical-align: middle; padding: 10px 12px; line-height: 1.5; word-break: break-word;">
                        <p style="margin: 0; padding: 0; color: #f1f5f9; font-size: 0.88rem; font-weight: 500; line-height: 1.5; white-space: normal; word-break: break-word; text-align: left;">${motivoLimpio}</p>
                    </td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">${badgeEstado}</td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center; padding: 12px 10px;">
                        <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
                            <button type="button" class="btn-info" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer;" onclick="abrirDetallesTicketRetrabajo('${ticketId}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button type="button" class="btn-success" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: #10b981; border: none; color: white;" onclick="liberarRetrabajoSupervisor('${ticketId}')">
                                ✅ Liberar Retrabajo
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        if (typeof aplicarPaginacion === 'function') {
            aplicarPaginacion('tabla-liberar-retrabajo', 15, true);
        }
    } catch (err) {
        console.error('Error al cargar retrabajos por liberar:', err);
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:20px; color:#ef4444;">Error al cargar las unidades pendientes de liberación.</td></tr>';
    }
};

window.liberarRetrabajoSupervisor = async function(ticketId) {
    if (!ticketId) return;
    const confirmar = confirm(`⚠️ ¿Confirmas la liberación del retrabajo para el ticket ${ticketId}?\\n\\nAl confirmar, la unidad quedará formalmente concluida de su proceso de garantía y volverá a estar operativa en circulación.`);
    if (!confirmar) return;

    try {
        const res = await fetch('/api/garantia/supervisor/liberar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Retrabajo liberado exitosamente.');
            cargarLiberarRetrabajosSupervisor();
            if (typeof actualizarBadgeLiberarRetrabajoSupervisor === 'function') {
                actualizarBadgeLiberarRetrabajoSupervisor();
            }
            if (typeof cargarRetrabajosAdmin === 'function') {
                cargarRetrabajosAdmin();
            }
            if (typeof cargarFacturas === 'function') {
                cargarFacturas();
            }
        } else {
            alert('Error: ' + (data.message || 'No se pudo liberar el retrabajo.'));
        }
    } catch (err) {
        console.error('Error al liberar retrabajo:', err);
        alert('Ocurrió un error al procesar la liberación del retrabajo.');
    }
};

window.actualizarBadgeLiberarRetrabajoSupervisor = async function() {
    const badge = document.getElementById('badge-liberar-retrabajo');
    if (!badge) return;
    try {
        const res = await fetch('/api/garantia/supervisor/por_liberar');
        const data = await res.json();
        const count = (data.retrabajos || []).length;
        if (count > 0) {
            badge.innerText = count;
            badge.style.display = 'inline-flex';
            badge.style.alignItems = 'center';
            badge.style.justifyContent = 'center';
        } else {
            badge.style.display = 'none';
        }
    } catch(e) {}
};
"""

# 4. In load listener, call actualizarBadgeLiberarRetrabajoSupervisor
t_load = """            } else if (subrolActual === 'Supervisor') {
                cambiarVistaAdmin('reportes');"""
r_load = """            } else if (subrolActual === 'Supervisor') {
                cambiarVistaAdmin('reportes');
                if (typeof actualizarBadgeLiberarRetrabajoSupervisor === 'function') {
                    actualizarBadgeLiberarRetrabajoSupervisor();
                }"""

is_crlf = '\r\n' in code
code_norm = code.replace('\r\n', '\n')

def replace_chunk(src, t, r, name):
    t_n = t.replace('\r\n', '\n')
    r_n = r.replace('\r\n', '\n')
    if t_n in src:
        print(f"SUCCESS: {name}")
        return src.replace(t_n, r_n, 1)
    else:
        print(f"FAILED: {name}")
        return src

code_norm = replace_chunk(code_norm, t_vistas, r_vistas, "vistas array")
code_norm = replace_chunk(code_norm, t_vids, r_vids, "vistaId check")
code_norm = replace_chunk(code_norm, t_vcalls, r_vcalls, "cambiarVista calls")
code_norm = replace_chunk(code_norm, t_marcar, r_marcar, "marcarRetrabajoFinalizado messages")
code_norm = replace_chunk(code_norm, t_load, r_load, "load listener supervisor badge")

code_norm += new_functions

if is_crlf:
    final_code = code_norm.replace('\n', '\r\n')
else:
    final_code = code_norm

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(final_code)

print("script.js updated.")

