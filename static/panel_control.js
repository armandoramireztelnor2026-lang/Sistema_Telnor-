// =========================================================
// ARCHIVO: panel_control.js
// PROPÓSITO: Frontend para Panel de Control de Jefatura
// =========================================================

function cargarPanelControl() {
    const container = document.getElementById('panel-personal-container');
    if (!container) return;
    container.innerHTML = '<p style="text-align:center; color:#a3b1c6; padding:40px;">Cargando personal...</p>';

    fetch('/api/panel/personal')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') {
                container.innerHTML = `<p style="color:#ef4444; text-align:center;">${data.message}</p>`;
                return;
            }
            let html = '';

            // SECCIÓN JEFATURA
            html += renderSeccion('🛠️ Jefatura', data.jefatura, '#f59e0b', data.ciudades_disponibles, false);

            // SECCIÓN SUPERVISORES
            html += renderSeccion('👤 Supervisores', data.supervisores, '#10b981', data.ciudades_disponibles, true);

            // SECCIÓN ADMINISTRADORES
            html += renderSeccion('🛡️ Administradores', data.administradores, '#3b82f6', data.ciudades_disponibles, true);

            container.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            container.innerHTML = '<p style="color:#ef4444; text-align:center;">Error al cargar personal.</p>';
        });
}

function renderSeccion(titulo, usuarios, color, ciudadesDisponibles, permiteEditar) {
    let html = `
    <div style="background: #0d1b2a; border-radius: 12px; margin-bottom: 25px; overflow: hidden; border: 1px solid #1e293b;">
        <div style="background: ${color}; padding: 15px 20px;">
            <h3 style="color: white; margin: 0; font-size: 1.2em;">${titulo}</h3>
        </div>
        <div style="padding: 15px;">`;

    if (usuarios.length === 0) {
        html += `<p style="color:#64748b; text-align:center; padding:20px;">No hay personal registrado en esta categoría.</p>`;
    } else {
        usuarios.forEach(u => {
            let fotoSrc = u.foto_ruta ? `/static/foto_administracion/${u.foto_ruta}` : 'https://via.placeholder.com/80/112641/40916c?text=N/A';
            let nombreCompleto = `${u.nombres} ${u.apellido_paterno} ${u.apellido_materno || ''}`.trim();

            // Badge de subrol
            let badgeColor = u.subrol === 'Jefatura' ? '#f59e0b' : u.subrol === 'Supervisor' ? '#10b981' : '#3b82f6';

            // Ciudades asignadas
            let ciudadesHTML = '';
            if (u.ciudades_asignadas && u.ciudades_asignadas.length > 0) {
                ciudadesHTML = u.ciudades_asignadas.map(c => 
                    `<span style="display:inline-flex; align-items:center; background:#1e293b; color:#e2e8f0; padding:4px 10px; border-radius:20px; font-size:0.85em; margin:3px;">
                        ${c} ${permiteEditar ? `<button onclick="quitarCiudadPanel('${u.usuario}', '${c}')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1.1em; margin-left:5px; padding:0;" title="Quitar ciudad">&times;</button>` : ''}
                    </span>`
                ).join('');
            } else {
                ciudadesHTML = '<span style="color:#64748b; font-size:0.85em;">Sin ciudades adicionales</span>';
            }

            // Dropdown para asignar ciudad
            let asignarBtnHTML = '';
            if (permiteEditar) {
                let opcionesHTML = ciudadesDisponibles
                    .filter(c => c !== u.ciudad && !(u.ciudades_asignadas || []).includes(c))
                    .map(c => `<option value="${c}">${c}</option>`)
                    .join('');

                asignarBtnHTML = `
                <div style="display:flex; gap:8px; align-items:center; margin-top:10px;">
                    <select id="select-ciudad-${u.usuario.replace(/[^a-zA-Z0-9]/g, '_')}" style="background:#1e293b; color:#e2e8f0; border:1px solid #334155; border-radius:6px; padding:6px 10px; font-size:0.85em; flex:1;">
                        <option value="">Seleccionar ciudad...</option>
                        ${opcionesHTML}
                    </select>
                    <button onclick="asignarCiudadPanel('${u.usuario}')" style="background:${color}; color:white; border:none; border-radius:6px; padding:6px 14px; cursor:pointer; font-weight:bold; font-size:0.85em; white-space:nowrap;">+ Asignar</button>
                </div>`;
            }

            // Botón cambiar subrol (solo para Supervisores y Administradores)
            let promoverBtnHTML = '';
            if (permiteEditar && u.subrol !== 'Jefatura') {
                let textoBoton = u.subrol === 'Administrador' ? '🔄 Cambiar a Supervisor' : '🔄 Cambiar a Administrador';
                promoverBtnHTML = `
                <button onclick="cambiarSubrolPanel('${u.usuario}', '${nombreCompleto}', '${u.subrol}')" 
                    style="background:#7c3aed; color:white; border:none; border-radius:6px; padding:6px 14px; cursor:pointer; font-weight:bold; font-size:0.85em; margin-top:10px; width:100%;">
                    ${textoBoton}
                </button>`;
            }

            html += `
            <div style="display:flex; gap:15px; align-items:flex-start; background:#111827; border-radius:10px; padding:15px; margin-bottom:12px; border:1px solid #1e293b;">
                <img src="${fotoSrc}" alt="Foto" style="width:70px; height:70px; border-radius:50%; object-fit:cover; border:3px solid ${badgeColor}; flex-shrink:0;">
                <div style="flex:1; min-width:0;">
                    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:5px;">
                        <strong style="color:#e2e8f0; font-size:1.05em;">${nombreCompleto}</strong>
                        <span style="background:${badgeColor}; color:white; padding:2px 10px; border-radius:12px; font-size:0.75em; font-weight:bold;">${u.subrol}</span>
                    </div>
                    <div style="color:#94a3b8; font-size:0.88em; line-height:1.7;">
                        <div>📍 <strong>Ciudad Principal:</strong> ${u.ciudad || 'N/A'} ${u.cope ? '| <strong>COPE:</strong> ' + u.cope : ''}</div>
                        <div>🏢 <strong>Área:</strong> ${u.area || 'N/A'} | <strong>No. Empleado:</strong> ${u.num_empleado || 'N/A'}</div>
                        <div>📧 <strong>Correo:</strong> ${u.correo || 'N/A'}</div>
                    </div>
                    <div style="margin-top:8px;">
                        <div style="color:#a3b1c6; font-size:0.85em; font-weight:600; margin-bottom:5px;">Ciudades Adicionales Asignadas:</div>
                        <div style="display:flex; flex-wrap:wrap; gap:3px;">${ciudadesHTML}</div>
                    </div>
                    ${asignarBtnHTML}
                    ${promoverBtnHTML}
                </div>
            </div>`;
        });
    }

    html += `</div></div>`;
    return html;
}

function asignarCiudadPanel(usuarioId) {
    let selectId = 'select-ciudad-' + usuarioId.replace(/[^a-zA-Z0-9]/g, '_');
    let select = document.getElementById(selectId);
    if (!select || !select.value) {
        alert('Selecciona una ciudad primero.');
        return;
    }
    let ciudad = select.value;
    if (!confirm(`¿Deseas asignar la ciudad "${ciudad}" a este usuario?`)) return;

    fetch('/api/panel/asignar_ciudad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario: usuarioId, ciudad: ciudad })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarPanelControl();
    })
    .catch(err => {
        console.error(err);
        alert('Error al conectar con el servidor.');
    });
}

function quitarCiudadPanel(usuarioId, ciudad) {
    if (!confirm(`¿Deseas REMOVER la ciudad "${ciudad}" de este usuario? Se le enviará un correo de notificación.`)) return;

    fetch('/api/panel/quitar_ciudad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario: usuarioId, ciudad: ciudad })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarPanelControl();
    })
    .catch(err => {
        console.error(err);
        alert('Error al conectar con el servidor.');
    });
}

function cambiarSubrolPanel(usuarioId, nombre, subrolActual) {
    let nuevoSubrol = subrolActual === 'Administrador' ? 'Supervisor' : 'Administrador';
    if (!confirm(`¿Estás seguro de cambiar el rol de "${nombre}" de ${subrolActual} a ${nuevoSubrol}?\n\nEsta acción modificará sus permisos en el sistema.`)) return;

    fetch('/api/panel/cambiar_subrol', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario: usuarioId })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarPanelControl();
    })
    .catch(err => {
        console.error(err);
        alert('Error al conectar con el servidor.');
    });
}
