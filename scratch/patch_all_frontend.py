import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. ACTUALIZAR templates/administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_pres_form = """                        <!-- Formulario para Modificar Presupuesto Total -->
                        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px;">
                            <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1rem; font-weight: 700;">Modificar Presupuesto Asignado:</h4>
                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <div style="position: relative; max-width: 320px; width: 100%;">
                                    <span style="position: absolute; left: 14px; top: 11px; color: #94a3b8; font-weight: bold;">$</span>
                                    <input type="number" id="cfg-input-presupuesto" min="0" step="1000" placeholder="500000" style="width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 10px 14px 10px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700;">
                                </div>
                                <button type="button" class="btn-success" onclick="guardarPresupuestoTotal()" style="background: #10b981; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);">
                                    <span>💾</span> <span>Actualizar Presupuesto</span>
                                </button>
                            </div>
                        </div>"""

new_pres_form = """<!-- Zona de Acciones de Presupuesto: Modificar y Resetear (Simétrico) -->
                        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 22px; display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; align-items: start;">
                            <!-- Modificar Presupuesto Total -->
                            <div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
                                <div>
                                    <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 1rem; font-weight: 700;">Modificar Presupuesto Asignado:</h4>
                                    <p style="margin: 0 0 14px 0; color: #94a3b8; font-size: 0.83rem;">
                                        Ajusta el monto total de presupuesto financiero asignado para las cotizaciones.
                                    </p>
                                </div>
                                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                                    <div style="position: relative; max-width: 240px; width: 100%;">
                                        <span style="position: absolute; left: 14px; top: 11px; color: #94a3b8; font-weight: bold;">$</span>
                                        <input type="number" id="cfg-input-presupuesto" min="0" step="1000" placeholder="500000" style="width: 100%; height: 42px; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 0 14px 0 28px; border-radius: 8px; font-size: 1rem; font-weight: 700;">
                                    </div>
                                    <button type="button" class="btn-success" onclick="guardarPresupuestoTotal()" style="background: #10b981; color: white; border: none; height: 42px; padding: 0 20px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);">
                                        <span>💾</span> <span>Actualizar</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Resetear Presupuesto Utilizado -->
                            <div style="border-left: 1px solid #1e293b; padding-left: 20px; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
                                <div>
                                    <h4 style="margin: 0 0 8px 0; color: #f59e0b; font-size: 1rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                        <span>🔄</span> Reiniciar Presupuesto Utilizado:
                                    </h4>
                                    <p style="margin: 0 0 14px 0; color: #94a3b8; font-size: 0.83rem; line-height: 1.45;">
                                        Permite a Jefatura eliminar el cálculo del dinero acumulado y reiniciar el saldo disponible al 100% para un nuevo ciclo.
                                    </p>
                                </div>
                                <div>
                                    <button type="button" onclick="resetearPresupuestoUtilizado()" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border: none; height: 42px; padding: 0 22px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
                                        <span>🗑️</span> <span>Resetear Dinero Utilizado</span>
                                    </button>
                                </div>
                            </div>
                        </div>"""

assert old_pres_form in html, "old_pres_form not found in administracion.html"
html = html.replace(old_pres_form, new_pres_form, 1)

# Cache buster a v=4
html = html.replace('configuraciones_jefatura.js?v=3', 'configuraciones_jefatura.js?v=4')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("templates/administracion.html actualizado con zona de reseteo de presupuesto.")

# 2. ACTUALIZAR static/configuraciones_jefatura.js
with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Actualizar renderizarTablaCuentasCorreo
old_render_cuentas = """function renderizarTablaCuentasCorreo(cuentas, correoActivo) {
    const tbody = document.getElementById('tabla-cuentas-correo');
    if (!tbody) return;

    if (!cuentas || cuentas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:15px; color:#94a3b8;">No hay cuentas de correo registradas.</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    cuentas.forEach((c, idx) => {
        const esActiva = c.activa === true || (c.correo && correoActivo && c.correo.toLowerCase() === correoActivo.toLowerCase());
        const badgeEstado = esActiva
            ? '<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 700;">✅ Emisor Activo</span>'
            : '<span style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid #64748b; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem;">Secundaria</span>';

        const btnActivar = esActiva
            ? '<span style="color:#10b981; font-size:0.8rem; font-weight:600;">En uso</span>'
            : `<button type="button" class="btn-info" style="padding: 4px 10px; font-size: 0.78rem;" onclick="activarCuentaCorreo('${c.id || c.correo}')">⚡ Activar</button>`;

        const btnProbar = `<button type="button" class="btn-secondary" style="padding: 4px 10px; font-size: 0.78rem; background: #334155; color: white;" onclick="abrirModalProbarCorreo('${c.correo}')">✉️ Probar</button>`;

        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid #1e293b;">
                <td style="font-weight: 600; color: #f8fafc;">${c.nombre || 'Cuenta ' + (idx + 1)}</td>
                <td style="color: #38bdf8;">${c.correo}</td>
                <td style="color: #cbd5e1; font-size: 0.85rem;">${c.servidor_smtp || 'smtp.gmail.com'}:${c.puerto_smtp || 587}</td>
                <td style="text-align: center;">${badgeEstado}</td>
                <td style="color: #94a3b8; font-size: 0.8rem;">${c.fecha_registro || '--'}</td>
                <td style="text-align: center;">
                    <div style="display: flex; gap: 6px; justify-content: center; align-items: center;">
                        ${btnActivar}
                        ${btnProbar}
                    </div>
                </td>
            </tr>
        `;
    });
}"""

new_render_cuentas = """function renderizarTablaCuentasCorreo(cuentas, correoActivo, envioActivo = true) {
    const tbody = document.getElementById('tabla-cuentas-correo');
    if (!tbody) return;

    if (!cuentas || cuentas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:15px; color:#94a3b8;">No hay cuentas de correo registradas.</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    const hayMultiples = cuentas.length > 1;

    cuentas.forEach((c, idx) => {
        const esActiva = (c.activa === true || (c.correo && correoActivo && c.correo.toLowerCase() === correoActivo.toLowerCase())) && envioActivo;

        const badgeEstado = esActiva
            ? '<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; padding: 4px 12px; border-radius: 12px; font-size: 0.78rem; font-weight: 700;">🟢 Emisor Activo</span>'
            : '<span style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid #64748b; padding: 4px 12px; border-radius: 12px; font-size: 0.78rem;">⚪ Inactiva</span>';

        let btnAccionActivarDesactivar = '';
        if (esActiva) {
            btnAccionActivarDesactivar = `<button type="button" style="padding: 5px 12px; font-size: 0.8rem; background: #334155; color: #f59e0b; border: 1px solid #f59e0b; border-radius: 6px; cursor: pointer; font-weight: 600;" onclick="desactivarCuentaCorreo('${c.id || c.correo}')" title="Desactivar esta cuenta para envíos automáticos">⏸️ Desactivar</button>`;
        } else {
            btnAccionActivarDesactivar = `<button type="button" style="padding: 5px 12px; font-size: 0.8rem; background: #0284c7; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;" onclick="activarCuentaCorreo('${c.id || c.correo}')" title="Activar esta cuenta como emisor automático">⚡ Activar</button>`;
        }

        const btnProbar = `<button type="button" style="padding: 5px 10px; font-size: 0.8rem; background: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 6px; cursor: pointer;" onclick="abrirModalProbarCorreo('${c.correo}')" title="Enviar prueba con esta cuenta">✉️ Probar</button>`;

        const btnEliminar = hayMultiples
            ? `<button type="button" style="padding: 5px 8px; font-size: 0.8rem; background: transparent; color: #ef4444; border: 1px solid #ef4444; border-radius: 6px; cursor: pointer;" onclick="eliminarCuentaCorreo('${c.id || c.correo}')" title="Eliminar cuenta">🗑️</button>`
            : '';

        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid #1e293b;">
                <td style="font-weight: 600; color: #f8fafc;">${c.nombre || 'Cuenta ' + (idx + 1)}</td>
                <td style="color: #38bdf8;">${c.correo}</td>
                <td style="color: #cbd5e1; font-size: 0.85rem;">${c.servidor_smtp || 'smtp.gmail.com'}:${c.puerto_smtp || 587}</td>
                <td style="text-align: center;">${badgeEstado}</td>
                <td style="color: #94a3b8; font-size: 0.8rem;">${c.fecha_registro || '--'}</td>
                <td style="text-align: center;">
                    <div style="display: flex; gap: 8px; justify-content: center; align-items: center; flex-wrap: wrap;">
                        ${btnAccionActivarDesactivar}
                        ${btnProbar}
                        ${btnEliminar}
                    </div>
                </td>
            </tr>
        `;
    });
}"""

assert old_render_cuentas in js, "old_render_cuentas not found"
js = js.replace(old_render_cuentas, new_render_cuentas, 1)

# Actualizar llamada a renderizarTablaCuentasCorreo en cargarConfiguracionesJefatura
old_call_render = "renderizarTablaCuentasCorreo(cfg.cuentas_correo || [], cfg.correo_emisor);"
new_call_render = """renderizarTablaCuentasCorreo(cfg.cuentas_correo || [], cfg.correo_emisor, cfg.envio_automatico_activo !== false);

        // Actualizar badge de emisor activo
        if (badgeCorreoActivo) {
            if (cfg.envio_automatico_activo !== false && cfg.correo_emisor) {
                badgeCorreoActivo.innerText = `🟢 Activo: ${cfg.correo_emisor}`;
                badgeCorreoActivo.style.background = 'rgba(16, 185, 129, 0.15)';
                badgeCorreoActivo.style.color = '#10b981';
                badgeCorreoActivo.style.borderColor = '#10b981';
            } else {
                badgeCorreoActivo.innerText = '⏸️ Envíos Automáticos Pausados';
                badgeCorreoActivo.style.background = 'rgba(239, 68, 68, 0.15)';
                badgeCorreoActivo.style.color = '#ef4444';
                badgeCorreoActivo.style.borderColor = '#ef4444';
            }
        }"""

assert old_call_render in js, "old_call_render not found"
js = js.replace(old_call_render, new_call_render, 1)

# Agregar funciones desactivarCuentaCorreo, eliminarCuentaCorreo y resetearPresupuestoUtilizado
nuevas_funciones_js = """
window.desactivarCuentaCorreo = async function(idOCorreo) {
    if (!confirm(`¿Confirmas que deseas DESACTIVAR la cuenta '${idOCorreo}' para el envío de correos automáticos?\\n\\nLos avisos por correo quedarán pausados hasta que actives una cuenta.`)) {
        return;
    }

    try {
        const res = await fetch('/api/configuracion/correo/desactivar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: idOCorreo, correo: idOCorreo })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert("⏸️ " + data.message);
            cargarConfiguracionesJefatura();
        } else {
            alert("❌ " + (data.message || "Error al desactivar cuenta"));
        }
    } catch (err) {
        console.error("Error al desactivar cuenta:", err);
        alert("❌ Error de comunicación con el servidor.");
    }
};

window.eliminarCuentaCorreo = async function(idOCorreo) {
    if (!confirm(`¿Confirmas que deseas ELIMINAR la cuenta '${idOCorreo}' del sistema?\\n\\nEsta acción no se puede deshacer.`)) {
        return;
    }

    try {
        const res = await fetch('/api/configuracion/correo/eliminar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: idOCorreo, correo: idOCorreo })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert("🗑️ " + data.message);
            cargarConfiguracionesJefatura();
        } else {
            alert("❌ " + (data.message || "Error al eliminar cuenta"));
        }
    } catch (err) {
        console.error("Error al eliminar cuenta:", err);
        alert("❌ Error de comunicación con el servidor.");
    }
};

window.resetearPresupuestoUtilizado = async function() {
    const confirmar = confirm("⚠️ ¿Confirmas que deseas RESETEAR el presupuesto utilizado?\\n\\nEsta acción eliminará el cálculo de dinero consumido en cotizaciones anteriores y reiniciará el saldo disponible al 100% para este nuevo ciclo.");
    if (!confirmar) return;

    try {
        const res = await fetch('/api/configuracion/presupuesto/resetear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert("✅ " + data.message);
            cargarConfiguracionesJefatura();
        } else {
            alert("❌ " + (data.message || "Error al resetear presupuesto"));
        }
    } catch (err) {
        console.error("Error al resetear presupuesto:", err);
        alert("❌ Error de comunicación con el servidor.");
    }
};
"""

js += nuevas_funciones_js

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("static/configuraciones_jefatura.js actualizado con desactivar, eliminar y resetear presupuesto!")

