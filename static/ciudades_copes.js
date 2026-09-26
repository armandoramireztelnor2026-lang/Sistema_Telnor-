// =========================================================
// ARCHIVO: ciudades_copes.js
// PROPÓSITO: Panel CRUD de Ciudades/COPEs para Jefatura
// =========================================================

function cargarCiudadesCopes() {
    const container = document.getElementById('ciudades-copes-container');
    if (!container) return;
    container.innerHTML = '<p style="text-align:center;color:#a3b1c6;padding:40px;">Cargando catálogo...</p>';

    fetch('/api/ciudades_copes')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                container.innerHTML = `<p style="color:#ef4444;text-align:center;">${data.message}</p>`;
                return;
            }
            renderCiudadesCopes(data.ciudades);
        })
        .catch(() => {
            container.innerHTML = '<p style="color:#ef4444;text-align:center;">Error al cargar el catálogo.</p>';
        });
}

function renderCiudadesCopes(ciudades) {
    const container = document.getElementById('ciudades-copes-container');

    let html = `
    <!-- Header con botón agregar ciudad -->
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; flex-wrap:wrap; gap:12px;">
        <div>
            <h2 style="color:#e2e8f0; margin:0; font-size:1.4em;">🗺️ Catálogo de Ciudades y COPEs</h2>
            <p style="color:#64748b; font-size:0.88em; margin:4px 0 0 0;">${ciudades.length} ciudad(es) registrada(s) · Los COPEs son la unidad de asignación para Supervisores y Administradores</p>
        </div>
        <button onclick="mostrarFormAgregarCiudad()" style="background:linear-gradient(135deg,#10b981,#059669); color:white; border:none; border-radius:8px; padding:10px 20px; cursor:pointer; font-weight:bold; font-size:0.9em; display:flex; align-items:center; gap:6px;">
            ＋ Agregar Ciudad
        </button>
    </div>

    <!-- Form agregar ciudad (oculto por defecto) -->
    <div id="form-agregar-ciudad" style="display:none; background:#0d1b2a; border:1px solid #10b981; border-radius:10px; padding:18px; margin-bottom:20px;">
        <p style="color:#10b981; font-weight:bold; margin:0 0 10px 0;">➕ Nueva Ciudad</p>
        <div style="display:flex; gap:10px;">
            <input id="input-nueva-ciudad" type="text" placeholder="Nombre de la ciudad (ej: Rosarito)" 
                style="flex:1; background:#1e293b; color:#e2e8f0; border:1px solid #334155; border-radius:6px; padding:8px 12px; font-size:0.9em;"
                onkeydown="if(event.key==='Enter') guardarNuevaCiudad()">
            <button onclick="guardarNuevaCiudad()" style="background:#10b981; color:white; border:none; border-radius:6px; padding:8px 16px; cursor:pointer; font-weight:bold;">Guardar</button>
            <button onclick="document.getElementById('form-agregar-ciudad').style.display='none'" style="background:#334155; color:#e2e8f0; border:none; border-radius:6px; padding:8px 16px; cursor:pointer;">Cancelar</button>
        </div>
    </div>

    <!-- Grid de ciudades -->
    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:18px;">`;

    if (ciudades.length === 0) {
        html += `<p style="color:#64748b; grid-column:1/-1; text-align:center; padding:40px;">No hay ciudades registradas aún.</p>`;
    }

    ciudades.forEach(ciudad => {
        const copesBadges = ciudad.copes.length > 0
            ? ciudad.copes.map(cope => `
                <span style="display:inline-flex; align-items:center; background:#1e293b; border:1px solid #334155; color:#e2e8f0; padding:5px 10px; border-radius:20px; font-size:0.82em; margin:3px; gap:6px;">
                    🏢 ${cope}
                    <button onclick="eliminarCope('${ciudad.nombre}','${cope}')" title="Eliminar COPE"
                        style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1em; padding:0; line-height:1;">&times;</button>
                </span>`).join('')
            : `<span style="color:#64748b; font-size:0.85em; font-style:italic;">Sin COPEs registrados</span>`;

        const safeId = ciudad.nombre.replace(/[^a-zA-Z0-9]/g, '_');

        html += `
        <div style="background:#0d1b2a; border-radius:12px; overflow:hidden; border:1px solid #1e293b; display:flex; flex-direction:column;">
            <!-- Header ciudad -->
            <div style="background:linear-gradient(135deg,#1e3a5f,#112641); padding:14px 16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="color:#e2e8f0; font-weight:bold; font-size:1.05em;">📍 ${ciudad.nombre}</div>
                    <div style="color:#64748b; font-size:0.8em; margin-top:2px;">${ciudad.copes.length} COPE(s)</div>
                </div>
                <button onclick="confirmarEliminarCiudad('${ciudad.nombre}')" title="Eliminar ciudad"
                    style="background:#7f1d1d; color:#fca5a5; border:none; border-radius:6px; padding:5px 10px; cursor:pointer; font-size:0.8em;">
                    🗑️ Eliminar
                </button>
            </div>
            <!-- COPEs -->
            <div style="padding:14px 14px 8px 14px; flex:1;">
                <div style="display:flex; flex-wrap:wrap; gap:2px; min-height:36px;">
                    ${copesBadges}
                </div>
            </div>
            <!-- Form agregar COPE inline -->
            <div style="padding:10px 14px 14px 14px; border-top:1px solid #1e293b;">
                <div style="display:flex; gap:8px;">
                    <input id="input-cope-${safeId}" type="text" placeholder="Nuevo COPE (ej: PE NORTE)"
                        style="flex:1; background:#1e293b; color:#e2e8f0; border:1px solid #334155; border-radius:6px; padding:6px 10px; font-size:0.82em;"
                        onkeydown="if(event.key==='Enter') agregarCope('${ciudad.nombre}')">
                    <button onclick="agregarCope('${ciudad.nombre}')"
                        style="background:#3b82f6; color:white; border:none; border-radius:6px; padding:6px 12px; cursor:pointer; font-weight:bold; font-size:0.82em; white-space:nowrap;">
                        + COPE
                    </button>
                </div>
            </div>
        </div>`;
    });

    html += `</div>`;
    container.innerHTML = html;
}

function mostrarFormAgregarCiudad() {
    const f = document.getElementById('form-agregar-ciudad');
    f.style.display = 'block';
    document.getElementById('input-nueva-ciudad').focus();
}

function guardarNuevaCiudad() {
    const nombre = document.getElementById('input-nueva-ciudad').value.trim();
    if (!nombre) { alert('Escribe el nombre de la ciudad.'); return; }
    if (!confirm(`¿Agregar la ciudad "${nombre}" al catálogo?`)) return;

    fetch('/api/ciudades_copes/agregar_ciudad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarCiudadesCopes();
    });
}

function confirmarEliminarCiudad(nombre) {
    if (!confirm(`¿Eliminar la ciudad "${nombre}" y todos sus COPEs?\n\nNo se puede si hay reportes activos en sus COPEs.`)) return;
    fetch('/api/ciudades_copes/eliminar_ciudad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarCiudadesCopes();
    });
}

function agregarCope(ciudadNombre) {
    const safeId = ciudadNombre.replace(/[^a-zA-Z0-9]/g, '_');
    const cope = document.getElementById(`input-cope-${safeId}`).value.trim().toUpperCase();
    if (!cope) { alert('Escribe el nombre del COPE.'); return; }
    if (!confirm(`¿Agregar el COPE "${cope}" a la ciudad ${ciudadNombre}?`)) return;

    fetch('/api/ciudades_copes/agregar_cope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ciudad: ciudadNombre, cope })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarCiudadesCopes();
    });
}

function eliminarCope(ciudadNombre, cope) {
    if (!confirm(`¿Eliminar el COPE "${cope}" de ${ciudadNombre}?\n\nNo se puede si hay reportes activos.`)) return;
    fetch('/api/ciudades_copes/eliminar_cope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ciudad: ciudadNombre, cope })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') cargarCiudadesCopes();
    });
}
