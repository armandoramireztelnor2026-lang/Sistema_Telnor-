# -*- coding: utf-8 -*-

modal_html = '''
<!-- MODAL PARA VALIDAR CÓDIGO Y LIBERAR RETRABAJO -->
<div id="modal-validar-codigo-liberacion" style="display: none; position: fixed; inset: 0; background: rgba(3, 7, 18, 0.78); backdrop-filter: blur(4px); z-index: 999999; align-items: center; justify-content: center; padding: 16px;">
    <div style="background: #0f172a; border: 1.5px solid #38bdf8; border-radius: 16px; width: 100%; max-width: 480px; box-shadow: 0 20px 45px rgba(0,0,0,0.85); overflow: hidden; animation: fadeInModal 0.2s ease;">
        <div style="background: linear-gradient(135deg, #0b192c 0%, #1e293b 100%); padding: 18px 22px; border-bottom: 1px solid #334155; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.6rem;">🔐</span>
                <div>
                    <h3 style="margin: 0; color: #ffffff; font-size: 1.1rem; font-weight: 700;">Validación de Entrega de Unidad</h3>
                    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 0.78rem;">Liberación de Retrabajo / Garantía</p>
                </div>
            </div>
            <button type="button" onclick="cerrarModalValidarCodigoLiberacion()" style="background: transparent; border: none; color: #94a3b8; font-size: 1.4rem; cursor: pointer; line-height: 1; padding: 2px 6px;">&times;</button>
        </div>
        <div style="padding: 22px 24px;">
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 10px; padding: 12px 16px; margin-bottom: 18px; font-size: 0.85rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #94a3b8;">Ticket:</span>
                    <strong id="modal-val-ticket" style="color: #f59e0b;">--</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #94a3b8;">Unidad:</span>
                    <strong id="modal-val-unidad" style="color: #38bdf8;">--</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #94a3b8;">Taller:</span>
                    <span id="modal-val-taller" style="color: #e2e8f0; font-weight: 600;">--</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">Chofer Asignado:</span>
                    <span id="modal-val-chofer" style="color: #10b981; font-weight: 600;">--</span>
                </div>
            </div>

            <p style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.5; margin: 0 0 14px 0; text-align: center;">
                Ingresa el <strong>código de 6 dígitos</strong> que el chofer recibió en su correo al entregarse la unidad, o el <strong>código de respaldo</strong> enviado a supervisión:
            </p>

            <div style="margin-bottom: 18px; text-align: center;">
                <input type="text" id="input-codigo-liberacion-retrabajo" maxlength="10" placeholder="000000" autocomplete="off"
                    style="width: 200px; text-align: center; font-size: 1.8rem; font-weight: 800; letter-spacing: 6px; font-family: monospace; padding: 10px 14px; background: #06111f; border: 2px solid #38bdf8; border-radius: 10px; color: #ffffff; outline: none; box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);"
                    onkeydown="if(event.key==='Enter') confirmarValidacionLiberacionRetrabajo()">
            </div>

            <div id="modal-val-error" style="display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; font-size: 0.82rem; padding: 8px 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
            </div>

            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button type="button" onclick="cerrarModalValidarCodigoLiberacion()" style="padding: 9px 18px; font-size: 0.85rem; font-weight: 600; border-radius: 8px; background: #334155; color: #cbd5e1; border: none; cursor: pointer;">
                    Cancelar
                </button>
                <button type="button" id="btn-confirmar-liberacion-modal" onclick="confirmarValidacionLiberacionRetrabajo()" style="padding: 9px 20px; font-size: 0.85rem; font-weight: 700; border-radius: 8px; background: #10b981; color: #ffffff; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);">
                    ✅ Validar y Liberar
                </button>
            </div>
        </div>
    </div>
</div>
'''

def patch_admin():
    with open("templates/administracion.html", "r", encoding="utf-8") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    norm = content.replace("\r\n", "\n")

    t_anchor = '            </div>\n\n            <!-- VISTA DE TIEMPO / GARANTÍA (JEFATURA: TODOS LOS TALLERES) -->'
    assert t_anchor in norm, "t_anchor not found in administracion.html"

    r_anchor = '            </div>\n' + modal_html + '\n            <!-- VISTA DE TIEMPO / GARANTÍA (JEFATURA: TODOS LOS TALLERES) -->'
    norm = norm.replace(t_anchor, r_anchor, 1)

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open("templates/administracion.html", "w", encoding="utf-8") as f:
        f.write(final)
    print("administracion.html patched with modal.")


def patch_script():
    with open("static/script.js", "r", encoding="utf-8") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    norm = content.replace("\r\n", "\n")

    # Replace cargarLiberarRetrabajosSupervisor and liberarRetrabajoSupervisor
    t_old_funcs = '''        tbody.innerHTML = '';
        retrabajos.forEach(r => {
            let ticketId = r.ticket_original || r.ticket || r.id;
            let unidadStr = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            let fechaReasig = r.fecha_reasignacion || r.fecha_solicitud || '--';
            let fechaListoTaller = r.fecha_finalizacion_taller || '--';
            let taller = r.proveedor || (r.seccion_2 && r.seccion_2.proveedor) || 'Taller';
            let motivoLimpio = String(r.motivo_chofer || 'Sin motivo reportado').trim().replace(/^["\'«»“”„]+|["\'«»“”„]+$/g, '').trim();

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
};'''

    r_new_funcs = '''        tbody.innerHTML = '';
        retrabajos.forEach(r => {
            let ticketId = r.ticket_original || r.ticket || r.id;
            let unidadStr = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            let fechaReasig = r.fecha_reasignacion || r.fecha_solicitud || '--';
            let fechaListoTaller = r.fecha_finalizacion_taller || '--';
            let taller = r.proveedor || (r.seccion_2 && r.seccion_2.proveedor) || 'Taller';
            let chofer = r.chofer || (r.seccion_1 && r.seccion_1.empleado) || 'Chofer';
            let motivoLimpio = String(r.motivo_chofer || 'Sin motivo reportado').trim().replace(/^["\'«»“”„]+|["\'«»“”„]+$/g, '').trim();

            let badgeEstado = `<span style="background:rgba(56, 189, 248, 0.15); color:#38bdf8; border:1px solid #38bdf8; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:0.82rem; display:inline-block; white-space:nowrap;">🔧 Listo en Taller</span>`;

            let ticketEscaped = String(ticketId).replace(/'/g, "\\\\'");
            let unidadEscaped = String(unidadStr).replace(/'/g, "\\\\'");
            let tallerEscaped = String(taller).replace(/'/g, "\\\\'");
            let choferEscaped = String(chofer).replace(/'/g, "\\\\'");

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${fechaReasig}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #4ade80;">${fechaListoTaller}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;">
                        <strong style="color: #ffffff;">${unidadStr}</strong><br>
                        <small style="color: #94a3b8; font-size: 0.75rem;">👤 ${chofer}</small>
                    </td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #38bdf8; font-weight: 600;">${r.cope || '--'}</span></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${r.ciudad || '--'}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #cbd5e1;">${taller}</span></td>
                    <td style="white-space: normal; min-width: 260px; max-width: 420px; vertical-align: middle; padding: 10px 12px; line-height: 1.5; word-break: break-word;">
                        <p style="margin: 0; padding: 0; color: #f1f5f9; font-size: 0.88rem; font-weight: 500; line-height: 1.5; white-space: normal; word-break: break-word; text-align: left;">${motivoLimpio}</p>
                    </td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">${badgeEstado}</td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center; padding: 12px 10px;">
                        <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
                            <button type="button" class="btn-info" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer;" onclick="abrirDetallesTicketRetrabajo('${ticketEscaped}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button type="button" class="btn-success" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; background: #10b981; border: none; color: white;" onclick="abrirModalValidarCodigoLiberacion('${ticketEscaped}', '${unidadEscaped}', '${tallerEscaped}', '${choferEscaped}')">
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

window.abrirModalValidarCodigoLiberacion = function(ticketId, unidad, taller, chofer) {
    window._ticketLiberarActual = ticketId;
    const modal = document.getElementById('modal-validar-codigo-liberacion');
    if (!modal) {
        const codigo = prompt(`🔐 Validación de Retrabajo - Ticket ${ticketId} (Unidad ${unidad}):\\n\\nIngresa el código de 6 dígitos que el chofer recibió en su correo (o el código de respaldo del supervisor):`);
        if (codigo) {
            ejecutarLiberacionDirecta(ticketId, codigo);
        }
        return;
    }

    const tEl = document.getElementById('modal-val-ticket');
    if (tEl) tEl.innerText = ticketId || '--';
    const uEl = document.getElementById('modal-val-unidad');
    if (uEl) uEl.innerText = unidad || '--';
    const talEl = document.getElementById('modal-val-taller');
    if (talEl) talEl.innerText = taller || '--';
    const chEl = document.getElementById('modal-val-chofer');
    if (chEl) chEl.innerText = chofer || 'Chofer';

    const input = document.getElementById('input-codigo-liberacion-retrabajo');
    if (input) input.value = '';

    const errEl = document.getElementById('modal-val-error');
    if (errEl) {
        errEl.style.display = 'none';
        errEl.innerText = '';
    }

    modal.style.display = 'flex';
    setTimeout(() => {
        if (input) input.focus();
    }, 100);
};

window.cerrarModalValidarCodigoLiberacion = function() {
    const modal = document.getElementById('modal-validar-codigo-liberacion');
    if (modal) modal.style.display = 'none';
    window._ticketLiberarActual = null;
};

window.confirmarValidacionLiberacionRetrabajo = async function() {
    const ticketId = window._ticketLiberarActual;
    if (!ticketId) return;

    const input = document.getElementById('input-codigo-liberacion-retrabajo');
    const codigo = (input?.value || '').trim();
    const errEl = document.getElementById('modal-val-error');

    if (!codigo) {
        if (errEl) {
            errEl.innerText = '⚠️ Por favor ingresa el código de 6 dígitos recibido por el chofer o el código de respaldo.';
            errEl.style.display = 'block';
        }
        if (input) input.focus();
        return;
    }

    if (errEl) errEl.style.display = 'none';

    const btn = document.getElementById('btn-confirmar-liberacion-modal');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Validando...';
    }

    try {
        const res = await fetch('/api/garantia/supervisor/liberar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId, codigo: codigo })
        });
        const data = await res.json();

        if (data.status === 'success') {
            cerrarModalValidarCodigoLiberacion();
            alert(data.message || 'Código validado con éxito. Retrabajo liberado y unidad entregada.');
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
            if (typeof cargarSeccionReportes === 'function') {
                cargarSeccionReportes();
            }
        } else {
            if (errEl) {
                errEl.innerText = data.message || '❌ Código de validación incorrecto.';
                errEl.style.display = 'block';
            } else {
                alert('Error: ' + (data.message || 'Código incorrecto.'));
            }
            if (input) {
                input.select();
                input.focus();
            }
        }
    } catch (err) {
        console.error('Error al validar código y liberar retrabajo:', err);
        if (errEl) {
            errEl.innerText = 'Ocurrió un error al procesar la validación.';
            errEl.style.display = 'block';
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '✅ Validar y Liberar';
        }
    }
};

window.liberarRetrabajoSupervisor = function(ticketId, unidad, taller, chofer) {
    abrirModalValidarCodigoLiberacion(ticketId, unidad, taller, chofer);
};'''

    assert t_old_funcs in norm, "t_old_funcs not found in script.js"
    norm = norm.replace(t_old_funcs, r_new_funcs, 1)

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open("static/script.js", "w", encoding="utf-8") as f:
        f.write(final)
    print("script.js patched with modal validation logic.")


if __name__ == "__main__":
    patch_admin()
    patch_script()

