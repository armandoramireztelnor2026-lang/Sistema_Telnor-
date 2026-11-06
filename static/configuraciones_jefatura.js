// =========================================================
// ARCHIVO: static/configuraciones_jefatura.js
// PROPÓSITO: Lógica de la Vista de Configuraciones para Jefatura
// Incluye:
// 1. Gestión de Correo Emisor y Código SMTP (Actualizar, Agregar, Probar)
// 2. Control Presupuestal y Seguimiento de Cotizaciones
// 3. Modificación del Límite de Cotizaciones Caras (+10000)
// =========================================================

window.LIMITE_COTIZACIONES_CARAS = window.LIMITE_COTIZACIONES_CARAS || 10000;
window._cotizacionesPresupuestoGlobal = [];

// =========================================================
// 1. CARGA INICIAL DE CONFIGURACIONES
// =========================================================
window.cargarConfiguracionesJefatura = async function() {
    try {
        const res = await fetch('/api/configuracion');
        if (!res.ok) {
            console.warn("No se pudo cargar la configuración:", res.status);
            return;
        }
        const data = await res.json();
        if (data.status !== 'success') return;

        const cfg = data.configuracion || {};
        const pres = data.presupuesto || {};

        // 1.1 Sincronizar límite global de cotizaciones caras
        window.LIMITE_COTIZACIONES_CARAS = parseFloat(cfg.limite_cotizaciones_caras || 10000);

        // 1.2 Llenar sección de Correo Emisor
        const inputCorreo = document.getElementById('cfg-correo-emisor');
        const inputCodigo = document.getElementById('cfg-codigo-emisor');
        const inputServidor = document.getElementById('cfg-servidor-smtp');
        const inputPuerto = document.getElementById('cfg-puerto-smtp');
        const badgeCorreoActivo = document.getElementById('cfg-badge-correo-activo');

        if (inputCorreo) inputCorreo.value = cfg.correo_emisor || '';
        if (inputCodigo) inputCodigo.value = cfg.codigo_emisor || '';
        if (inputServidor) inputServidor.value = cfg.servidor_smtp || 'smtp.gmail.com';
        if (inputPuerto) inputPuerto.value = cfg.puerto_smtp || 587;
        if (badgeCorreoActivo) badgeCorreoActivo.innerText = cfg.correo_emisor || 'No configurado';
        // Registrar valores iniciales y bloquear campos
        window._valoresOriginalesCorreo = {
            correo: (inputCorreo ? inputCorreo.value : '').trim(),
            codigo: (inputCodigo ? inputCodigo.value : '').trim(),
            servidor: (inputServidor ? inputServidor.value : '').trim(),
            puerto: (inputPuerto ? String(inputPuerto.value) : '').trim()
        };
        if (typeof window.bloquearCamposCorreoEmisor === 'function') {
            window.bloquearCamposCorreoEmisor();
        }

        // Renderizar tabla de cuentas de correo
        renderizarTablaCuentasCorreo(cfg.cuentas_correo || [], cfg.correo_emisor, cfg.envio_automatico_activo !== false);

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
        }

        // 1.3 Llenar sección de Control Presupuestal
        const elTotal = document.getElementById('cfg-presupuesto-total-txt');
        const elComprometido = document.getElementById('cfg-comprometido-txt');
        const elRestante = document.getElementById('cfg-restante-txt');
        const elTotalCots = document.getElementById('cfg-total-confirmadas-txt');
        const elInputPresupuesto = document.getElementById('cfg-input-presupuesto');
        const elProgreso = document.getElementById('cfg-progreso-presupuesto');
        const elProgresoTxt = document.getElementById('cfg-progreso-presupuesto-txt');

        const totalPres = parseFloat(pres.presupuesto_total || 0);
        const compPres = parseFloat(pres.dinero_comprometido || 0);
        const restPres = parseFloat(pres.presupuesto_restante || 0);
        const pctPres = parseFloat(pres.porcentaje_consumido || 0);

        if (elTotal) elTotal.innerText = `$ ${totalPres.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
        if (elComprometido) elComprometido.innerText = `$ ${compPres.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
        if (elRestante) {
            elRestante.innerText = `$ ${restPres.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
            if (restPres <= 0) {
                elRestante.style.color = '#ef4444';
            } else if (pctPres >= 80) {
                elRestante.style.color = '#f59e0b';
            } else {
                elRestante.style.color = '#10b981';
            }
        }
        if (elTotalCots) elTotalCots.innerText = `${pres.total_confirmadas || 0} Cotizaciones Confirmadas`;
        if (elInputPresupuesto) elInputPresupuesto.value = totalPres;

        if (elProgreso) {
            const cappedPct = Math.min(100, Math.max(0, pctPres));
            elProgreso.style.width = `${cappedPct}%`;
            if (pctPres >= 90) {
                elProgreso.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
            } else if (pctPres >= 70) {
                elProgreso.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
            } else {
                elProgreso.style.background = 'linear-gradient(90deg, #10b981, #059669)';
            }
        }
        if (elProgresoTxt) {
            elProgresoTxt.innerText = `${pctPres.toFixed(2)}% Utilizado (${(100 - pctPres).toFixed(2)}% Disponible)`;
        }

        // Renderizar tabla de cotizaciones confirmadas
        window._cotizacionesPresupuestoGlobal = pres.cotizaciones_confirmadas || [];
        renderizarTablaCotizacionesPresupuesto(window._cotizacionesPresupuestoGlobal);

        // 1.4 Llenar sección de Límite de Cotizaciones Caras
        const elLimiteActual = document.getElementById('cfg-badge-limite-actual');
        const elInputLimite = document.getElementById('cfg-input-limite');
        const limVal = parseFloat(cfg.limite_cotizaciones_caras || 10000);

        if (elLimiteActual) elLimiteActual.innerText = `$ ${limVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
        if (elInputLimite) elInputLimite.value = limVal;

        // 1.5 Activar la sección correspondiente (Paso 1: Correo por defecto, o la guardada)
        let tabActiva = 'correo';
        try {
            const saved = localStorage.getItem('tabConfiguracionActiva');
            if (saved && ['correo', 'presupuesto', 'limite'].includes(saved)) {
                tabActiva = saved;
            }
        } catch (e) {}
        if (typeof window.cambiarTabConfiguracion === 'function') {
            window.cambiarTabConfiguracion(tabActiva);
        }

    } catch (err) {
        console.error("Error cargando configuraciones de jefatura:", err);
    }
};

// =========================================================
// 2. GESTIÓN DE CUENTAS DE CORREO SMTP
// =========================================================

function renderizarTablaCuentasCorreo(cuentas, correoActivo, envioActivo = true) {
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
}

// Variable de control para modo de edición de correo emisor
window._modoEdicionCorreo = false;
window._valoresOriginalesCorreo = null;

window.bloquearCamposCorreoEmisor = function() {
    window._modoEdicionCorreo = false;
    const campos = ['cfg-correo-emisor', 'cfg-codigo-emisor', 'cfg-servidor-smtp', 'cfg-puerto-smtp'];
    campos.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.disabled = true;
            el.style.cursor = 'not-allowed';
            el.style.background = '#0f172a';
            el.style.borderColor = '#1e293b';
            el.style.color = '#94a3b8';
            el.style.opacity = '0.85';
        }
    });

    const btnGuardar = document.getElementById('btn-guardar-correo-emisor');
    const txtGuardar = document.getElementById('btn-guardar-correo-emisor-txt');
    const icoGuardar = document.getElementById('btn-guardar-correo-emisor-icon');
    const btnCancelar = document.getElementById('btn-cancelar-correo-emisor');

    if (btnGuardar) {
        btnGuardar.style.background = '#000000';
        btnGuardar.style.border = '1px solid #334155';
        btnGuardar.style.boxShadow = '0 4px 10px rgba(2, 132, 199, 0.25)';
    }
    if (txtGuardar) txtGuardar.innerText = 'Actualizar datos';
    if (icoGuardar) icoGuardar.innerText = '✏️';
    if (btnCancelar) btnCancelar.style.display = 'none';
};

window.desbloquearCamposCorreoEmisor = function() {
    window._modoEdicionCorreo = true;
    const campos = ['cfg-correo-emisor', 'cfg-codigo-emisor', 'cfg-servidor-smtp', 'cfg-puerto-smtp'];
    campos.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.disabled = false;
            el.style.cursor = 'text';
            el.style.background = '#1e293b';
            el.style.borderColor = '#38bdf8';
            el.style.color = '#ffffff';
            el.style.opacity = '1';
        }
    });

    const btnGuardar = document.getElementById('btn-guardar-correo-emisor');
    const txtGuardar = document.getElementById('btn-guardar-correo-emisor-txt');
    const icoGuardar = document.getElementById('btn-guardar-correo-emisor-icon');
    const btnCancelar = document.getElementById('btn-cancelar-correo-emisor');

    if (btnGuardar) {
        btnGuardar.style.background = '#000000';
        btnGuardar.style.border = '1px solid #38bdf8';
        btnGuardar.style.boxShadow = '0 4px 10px rgba(16, 185, 129, 0.25)';
    }
    if (txtGuardar) txtGuardar.innerText = 'Guardar credenciales de correo';
    if (icoGuardar) icoGuardar.innerText = '💾';
    if (btnCancelar) btnCancelar.style.display = 'inline-flex';

    const inputCorreo = document.getElementById('cfg-correo-emisor');
    if (inputCorreo) inputCorreo.focus();
};

window.cancelarEdicionCorreoEmisor = function() {
    const orig = window._valoresOriginalesCorreo;
    if (orig) {
        const elCorreo = document.getElementById('cfg-correo-emisor');
        const elCodigo = document.getElementById('cfg-codigo-emisor');
        const elServidor = document.getElementById('cfg-servidor-smtp');
        const elPuerto = document.getElementById('cfg-puerto-smtp');

        if (elCorreo) elCorreo.value = orig.correo || '';
        if (elCodigo) elCodigo.value = orig.codigo || '';
        if (elServidor) elServidor.value = orig.servidor || 'smtp.gmail.com';
        if (elPuerto) elPuerto.value = orig.puerto || '587';
    }
    window.bloquearCamposCorreoEmisor();
};

window.guardarCorreoEmisor = async function() {
    // Si los campos están bloqueados, este clic entra en modo de edición ("Actualizar datos")
    if (!window._modoEdicionCorreo) {
        window._valoresOriginalesCorreo = {
            correo: (document.getElementById('cfg-correo-emisor')?.value || '').trim(),
            codigo: (document.getElementById('cfg-codigo-emisor')?.value || '').trim(),
            servidor: (document.getElementById('cfg-servidor-smtp')?.value || '').trim(),
            puerto: (document.getElementById('cfg-puerto-smtp')?.value || '').trim()
        };
        window.desbloquearCamposCorreoEmisor();
        return;
    }

    // Si ya estamos en modo edición, el botón dice "Guardar credenciales de correo"
    const correo = (document.getElementById('cfg-correo-emisor')?.value || '').trim();
    const codigo = (document.getElementById('cfg-codigo-emisor')?.value || '').trim();
    const servidor = (document.getElementById('cfg-servidor-smtp')?.value || '').trim() || 'smtp.gmail.com';
    const puerto = (document.getElementById('cfg-puerto-smtp')?.value || '').trim() || '587';

    // Validar si NO se ha modificado nada
    const orig = window._valoresOriginalesCorreo || {};
    const noModificoNada = (
        correo === (orig.correo || '') &&
        codigo === (orig.codigo || '') &&
        servidor === (orig.servidor || '') &&
        puerto === (orig.puerto || '')
    );

    if (noModificoNada) {
        alert("⚠️ Debes actualizar como mínimo un dato.");
        return;
    }

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }
    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación (App Password de Google).");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas guardar y actualizar las credenciales del correo emisor oficial (${correo})?`);
    if (!confirmar) return;

    if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Guardando Configuración...", "Actualizando correo emisor y credenciales SMTP 📧");
    }

    try {
        const res = await fetch('/api/configuracion/correo/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                correo: correo,
                codigo: codigo,
                servidor_smtp: servidor,
                puerto_smtp: puerto,
                nombre: 'Emisor Principal'
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "Credenciales guardadas exitosamente.");
            cargarConfiguracionesJefatura();
        } else if (data.status === 'no_change') {
            alert("⚠️ Debes actualizar como mínimo un dato.");
        } else {
            alert("Error: " + (data.message || "No se pudo guardar la configuración."));
        }
    } catch (err) {
        console.error("Error al guardar correo emisor:", err);
        alert("Ocurrió un error al guardar la configuración de correo.");
    } finally {
        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();
    }
};

window.abrirModalAgregarCuenta = function() {
    const modal = document.getElementById('modal-agregar-cuenta-correo');
    if (modal) modal.style.display = 'flex';
};

window.cerrarModalAgregarCuenta = function() {
    const modal = document.getElementById('modal-agregar-cuenta-correo');
    if (modal) modal.style.display = 'none';
};

window.guardarNuevaCuentaCorreo = async function() {
    const nombre = document.getElementById('modal-nueva-cuenta-nombre')?.value.trim() || 'Cuenta Adicional';
    const correo = document.getElementById('modal-nueva-cuenta-correo')?.value.trim();
    const codigo = document.getElementById('modal-nueva-cuenta-codigo')?.value.trim();
    const servidor = document.getElementById('modal-nueva-cuenta-servidor')?.value.trim() || 'smtp.gmail.com';
    const puerto = document.getElementById('modal-nueva-cuenta-puerto')?.value.trim() || '587';
    const activar = document.getElementById('modal-nueva-cuenta-activar')?.checked || false;

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }
    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas registrar y agregar la nueva cuenta de correo "${nombre}" (${correo})?`);
    if (!confirmar) return;

    try {
        const res = await fetch('/api/configuracion/correo/agregar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombre: nombre,
                correo: correo,
                codigo: codigo,
                servidor_smtp: servidor,
                puerto_smtp: puerto,
                activar: activar
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "Cuenta agregada exitosamente.");
            cerrarModalAgregarCuenta();
            cargarConfiguracionesJefatura();
        } else {
            alert("Error: " + (data.message || "No se pudo agregar la cuenta."));
        }
    } catch (err) {
        console.error("Error al agregar cuenta:", err);
        alert("Ocurrió un error al registrar la cuenta.");
    }
};

window.activarCuentaCorreo = async function(idOCorreo) {
    if (!confirm(`¿Confirmas que deseas activar la cuenta '${idOCorreo}' como el emisor oficial de todos los correos del sistema?`)) {
        return;
    }

    try {
        const res = await fetch('/api/configuracion/correo/activar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: idOCorreo, correo: idOCorreo })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "Cuenta activada exitosamente.");
            cargarConfiguracionesJefatura();
        } else {
            alert("Error: " + (data.message || "No se pudo activar la cuenta."));
        }
    } catch (err) {
        console.error("Error al activar cuenta:", err);
        alert("Ocurrió un error al activar la cuenta.");
    }
};

window.abrirModalProbarCorreo = function(correoEmisorEspecífico) {
    const correoActivo = correoEmisorEspecífico || document.getElementById('cfg-correo-emisor')?.value.trim();
    const destinoDefault = prompt(`✉️ Envío de Correo de Prueba SMTP\n\nSe enviará un correo de verificación desde '${correoActivo}'.\n\nIngresa el correo destinatario que recibirá el mensaje de prueba:`, correoActivo);

    if (!destinoDefault || !destinoDefault.trim()) return;

    window.enviarCorreoPrueba(destinoDefault.trim(), correoEmisorEspecífico);
};

window.enviarCorreoPrueba = async function(correoDestino, correoEmisor) {
    if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Comprobando Conexión SMTP...", `Enviando correo de prueba a ${correoDestino} ⏳`);
    }

    try {
        const res = await fetch('/api/configuracion/correo/probar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                correo_destino: correoDestino,
                correo: correoEmisor
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "✅ Conexión SMTP verificada con éxito.");
        } else {
            alert(data.message || "❌ Error en la prueba de correo.");
        }
    } catch (err) {
        console.error("Error al probar correo:", err);
        alert("Ocurrió un error al contactar al servidor para la prueba SMTP.");
    } finally {
        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();
    }
};

// =========================================================
// 3. CONTROL PRESUPUESTAL
// =========================================================

window.guardarPresupuestoTotal = async function() {
    const inputVal = document.getElementById('cfg-input-presupuesto')?.value;
    const nuevoMonto = parseFloat(inputVal);

    if (isNaN(nuevoMonto) || nuevoMonto < 0) {
        alert("⚠️ Por favor ingresa un monto de presupuesto válido mayor o igual a 0.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas establecer el Presupuesto Total en $ ${nuevoMonto.toLocaleString('en-US', { minimumFractionDigits: 2 })} MXN?`);
    if (!confirmar) return;

    if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Actualizando Presupuesto...", "Calculando balance y recortando montos de cotizaciones confirmadas 💰");
    }

    try {
        const res = await fetch('/api/configuracion/presupuesto/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ presupuesto_total: nuevoMonto })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "Presupuesto actualizado exitosamente.");
            cargarConfiguracionesJefatura();
        } else {
            alert("Error: " + (data.message || "No se pudo actualizar el presupuesto."));
        }
    } catch (err) {
        console.error("Error al guardar presupuesto:", err);
        alert("Ocurrió un error al actualizar el presupuesto.");
    } finally {
        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();
    }
};

window.renderizarTablaCotizacionesPresupuesto = function(lista) {
    const tbody = document.getElementById('tabla-cotizaciones-presupuesto');
    if (!tbody) return;

    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:25px; color:#94a3b8; font-weight: 500;">No hay cotizaciones confirmadas registradas en el ciclo actual.</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    lista.forEach(item => {
        let precioFmt = item.precio ? `$ ${parseFloat(item.precio).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN` : '$ 0.00 MXN';
        let rawUnidad = String(item.unidad || '').trim();
        let unidadStr = rawUnidad ? (rawUnidad.startsWith('8090-') ? rawUnidad : `8090-${rawUnidad}`) : '--';

        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid #1e293b; transition: background 0.2s ease;">
                <td style="padding: 10px 14px; font-weight: 700; color: #f59e0b;">${item.id_reporte || item.id}</td>
                <td style="padding: 10px 14px; font-weight: 600; color: #38bdf8;">${unidadStr}</td>
                <td style="padding: 10px 14px; color: #cbd5e1;">${item.proveedor}</td>
                <td style="padding: 10px 14px; color: #94a3b8;">${(item.cope && item.cope !== 'N/A') ? item.cope : 'PE CALLE 10'}</td>
                <td style="padding: 10px 14px; font-weight: 700; color: #10b981; font-size: 0.95rem;">${precioFmt}</td>
                <td style="padding: 10px 14px;"><span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">${item.estado}</span></td>
                <td style="padding: 10px 14px; color: #94a3b8; font-size: 0.85rem;">${item.fecha}</td>
            </tr>
        `;
    });
};
const renderizarTablaCotizacionesPresupuesto = window.renderizarTablaCotizacionesPresupuesto;


window.toggleDesglosePresupuesto = function() {
    const contenedor = document.getElementById('contenedor-desglose-presupuesto');
    const badge = document.getElementById('cfg-badge-toggle-desglose');
    const btnTitulo = document.getElementById('cfg-txt-titulo-desglose');

    if (!contenedor) return;

    const estaOculto = contenedor.style.display === 'none' || contenedor.style.display === '';

    if (estaOculto) {
        contenedor.style.display = 'block';
        if (badge) badge.innerHTML = '<span>Ocultar Desglose</span> <span id="cfg-arrow-desglose" style="font-size: 0.82rem;">▲</span>';
        if (btnTitulo) btnTitulo.innerText = 'Desglose de Cotizaciones que han Consumido Presupuesto';
        if (typeof renderizarTablaCotizacionesPresupuesto === 'function' && window._cotizacionesPresupuestoGlobal) {
            renderizarTablaCotizacionesPresupuesto(window._cotizacionesPresupuestoGlobal);
        }
    } else {
        contenedor.style.display = 'none';
        if (badge) badge.innerHTML = '<span>Desplegar Desglose</span> <span id="cfg-arrow-desglose" style="font-size: 0.82rem;">▼</span>';
        if (btnTitulo) btnTitulo.innerText = 'Ver Desglose de Cotizaciones que han Consumido Presupuesto';
    }
};

window.filtrarCotizacionesPresupuesto = function() {
    const input = document.getElementById('buscar-cotizaciones-presupuesto');
    if (!input) return;
    const q = input.value.toLowerCase().trim();

    if (!q) {
        renderizarTablaCotizacionesPresupuesto(window._cotizacionesPresupuestoGlobal);
        return;
    }

    const filtradas = (window._cotizacionesPresupuestoGlobal || []).filter(item => {
        return (
            String(item.id || '').toLowerCase().includes(q) ||
            String(item.id_reporte || '').toLowerCase().includes(q) ||
            String(item.unidad || '').toLowerCase().includes(q) ||
            String(item.proveedor || '').toLowerCase().includes(q) ||
            String(item.cope || '').toLowerCase().includes(q) ||
            String(item.estado || '').toLowerCase().includes(q)
        );
    });

    renderizarTablaCotizacionesPresupuesto(filtradas);
};

// =========================================================
// 4. LÍMITE DE COTIZACIONES CARAS (+10000)
// =========================================================

window.seleccionarLimiteRapido = function(monto) {
    const input = document.getElementById('cfg-input-limite');
    if (input) input.value = monto;
};

window.guardarLimiteCotizacionesCaras = async function() {
    const inputVal = document.getElementById('cfg-input-limite')?.value;
    const nuevoLimite = parseFloat(inputVal);

    if (isNaN(nuevoLimite) || nuevoLimite <= 0) {
        alert("⚠️ Por favor ingresa un monto límite válido mayor a 0.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas establecer el Límite de Cotizaciones Caras en $ ${nuevoLimite.toLocaleString('en-US', { minimumFractionDigits: 2 })} MXN?\n\nCualquier cotización igual o superior a este monto requerirá autorización de Administrador / Corporativo.`);
    if (!confirmar) return;

    if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Actualizando Límite...", "Guardando nuevo umbral de cotizaciones caras 🏷️");
    }

    try {
        const res = await fetch('/api/configuracion/limite_caras/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limite_cotizaciones_caras: nuevoLimite })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || "Límite actualizado exitosamente.");
            window.LIMITE_COTIZACIONES_CARAS = nuevoLimite;
            cargarConfiguracionesJefatura();
        } else {
            alert("Error: " + (data.message || "No se pudo actualizar el límite."));
        }
    } catch (err) {
        console.error("Error al guardar límite:", err);
        alert("Ocurrió un error al actualizar el límite.");
    } finally {
        if (typeof ocultarLoaderDinamico === 'function') ocultarLoaderDinamico();
    }
};

// =========================================================
// 5. UTILIDADES DE INTERFAZ
// =========================================================

const SVG_OJO_ABIERTO = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;

const SVG_OJO_CERRADO = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #38bdf8;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

window.toggleMostrarPassword = function(inputId, btnEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isSmall = btnEl && btnEl.querySelector('svg')?.getAttribute('width') === '18';
    const svgAbierto = isSmall ? SVG_OJO_ABIERTO.replace(/width="20" height="20"/g, 'width="18" height="18"') : SVG_OJO_ABIERTO;
    const svgCerrado = isSmall ? SVG_OJO_CERRADO.replace(/width="20" height="20"/g, 'width="18" height="18"') : SVG_OJO_CERRADO;

    if (input.type === 'password') {
        input.type = 'text';
        if (btnEl) {
            btnEl.innerHTML = svgCerrado;
            btnEl.title = 'Ocultar código';
        }
    } else {
        input.type = 'password';
        if (btnEl) {
            btnEl.innerHTML = svgAbierto;
            btnEl.title = 'Mostrar código';
        }
    }
};

window.cambiarTabConfiguracion = function(tabName) {
    const validTabs = ['correo', 'presupuesto', 'limite'];
    if (!validTabs.includes(tabName)) {
        tabName = 'correo';
    }

    try {
        localStorage.setItem('tabConfiguracionActiva', tabName);
    } catch (e) {}

    const tabStyles = {
        correo: {
            activeBg: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            activeBorder: '#38bdf8',
            color: '#ffffff',
            shadow: '0 4px 12px rgba(2, 132, 199, 0.35)'
        },
        presupuesto: {
            activeBg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            activeBorder: '#34d399',
            color: '#ffffff',
            shadow: '0 4px 12px rgba(16, 185, 129, 0.35)'
        },
        limite: {
            activeBg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            activeBorder: '#fbbf24',
            color: '#0f172a',
            shadow: '0 4px 12px rgba(245, 158, 11, 0.35)'
        }
    };

    validTabs.forEach(t => {
        const sec = document.getElementById(`seccion-cfg-${t}`);
        const btn = document.getElementById(`tab-btn-cfg-${t}`);

        // Mostrar estrictamente solo la actividad seleccionada
        if (sec) {
            sec.style.display = (t === tabName) ? 'block' : 'none';
        }
        if (tabName !== 'correo' && window._modoEdicionCorreo && typeof window.cancelarEdicionCorreoEmisor === 'function') {
            window.cancelarEdicionCorreoEmisor();
        }

        // Estilizar los botones de las actividades independientes
        if (btn) {
            if (t === tabName) {
                const s = tabStyles[t] || tabStyles.correo;
                btn.style.background = s.activeBg;
                btn.style.color = s.color;
                btn.style.border = `1px solid ${s.activeBorder}`;
                btn.style.boxShadow = s.shadow;
                btn.style.fontWeight = '700';
            } else {
                btn.style.background = '#0f172a';
                btn.style.color = '#94a3b8';
                btn.style.border = '1px solid #1e293b';
                btn.style.boxShadow = 'none';
                btn.style.fontWeight = '600';
            }
        }
    });

    const vistaEl = document.getElementById('vista-configuraciones');
    if (vistaEl && vistaEl.style.display !== 'none') {
        vistaEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};

// Auto-cargar umbral de configuración al inicializar la página
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/api/configuracion')
            .then(res => res.json())
            .then(data => {
                if (data && data.configuracion) {
                    window.LIMITE_COTIZACIONES_CARAS = parseFloat(data.configuracion.limite_cotizaciones_caras || 10000);
                }
            })
            .catch(e => {});
    });
}

window.desactivarCuentaCorreo = async function(idOCorreo) {
    if (!confirm(`¿Confirmas que deseas DESACTIVAR la cuenta '${idOCorreo}' para el envío de correos automáticos?\n\nLos avisos por correo quedarán pausados hasta que actives una cuenta.`)) {
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
    if (!confirm(`¿Confirmas que deseas ELIMINAR la cuenta '${idOCorreo}' del sistema?\n\nEsta acción no se puede deshacer.`)) {
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
    const confirmar = confirm("⚠️ ¿Confirmas que deseas RESETEAR el presupuesto utilizado?\n\nEsta acción eliminará el cálculo de dinero consumido en cotizaciones anteriores y reiniciará el saldo disponible al 100% para este nuevo ciclo.");
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

window.descargarExcelPresupuesto = function() {
    window.location.href = '/api/configuracion/presupuesto/exportar_excel';
};
