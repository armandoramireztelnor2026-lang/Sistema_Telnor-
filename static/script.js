// =========================================================
// ARCHIVO: static/script.js
// =========================================================

// --- LÓGICA DE CASCADA GLOBAL ---
const zonasCopeGlobal = {
    "Tijuana": ["PE CALLE 10", "PIO PICO", "CALLE QUINTA", "RIO", "LIBERTAD", "METRO", "PE OTAY INDUSTRIAL", "PE SEMINARIO", "PE PLAYAS", "PE ROSARITO", "PE TECATE"],
    "Tecate": ["PE CALLE 10", "PIO PICO", "CALLE QUINTA", "RIO", "LIBERTAD", "METRO", "PE OTAY INDUSTRIAL", "PE SEMINARIO", "PE PLAYAS", "PE ROSARITO", "PE TECATE"],
    "Ensenada": ["PE ENSENADA", "PE SAN QUINTIN"],
    "San Quintin": ["PE ENSENADA", "PE SAN QUINTIN"],
    "Mexicali": ["PE PERIFERICO", "REFORMA", "ANAHUAC", "DE PIONEROS"],
    "San Luis Rio Colorado": ["PE SAN LUIS RC", "CALLE 14"]
};

function actualizarCopeSelect(ciudadSelectId, copeSelectId, valorPreseleccionado = '') {
    const ciudad = document.getElementById(ciudadSelectId).value;
    const copeSelect = document.getElementById(copeSelectId);
    if (!copeSelect) return;

    copeSelect.innerHTML = '<option value="" disabled selected>Seleccione COPE / Edificio...</option>';
    if (zonasCopeGlobal[ciudad]) {
        zonasCopeGlobal[ciudad].forEach(c => {
            let sel = (c === valorPreseleccionado) ? 'selected' : '';
            copeSelect.innerHTML += `<option value="${c}" ${sel}>${c}</option>`;
        });
    }
}
// ----------------------------------------

let modosLogin = { 'proveedores': true, 'administracion': true, 'corporativos': true };
let pendientesGlobal = [];
let usuariosGlobal = [];

function mostrarAuth(rol) {
    document.getElementById('auth-proveedores').style.display = 'none';
    document.getElementById('auth-administracion').style.display = 'none';
    document.getElementById('auth-corporativos').style.display = 'none';
    const cajaActiva = document.getElementById('auth-' + rol);
    if (cajaActiva) { cajaActiva.style.display = 'block'; cajaActiva.scrollIntoView({ behavior: 'smooth' }); }
}

function toggleModo(rol) {
    modosLogin[rol] = !modosLogin[rol];
    const cajaActiva = document.getElementById('auth-' + rol);
    if (modosLogin[rol]) {
        cajaActiva.classList.remove('registro-modo');
        document.getElementById('login-view-' + rol).style.display = 'block';
        document.getElementById('registro-view-' + rol).style.display = 'none';
        document.getElementById('titulo-' + rol).innerText = "Ingreso - " + rol.toUpperCase();
        document.getElementById('link-' + rol).innerText = "¿No tienes cuenta? Solicitar Registro";
    } else {
        cajaActiva.classList.add('registro-modo');
        document.getElementById('login-view-' + rol).style.display = 'none';
        document.getElementById('registro-view-' + rol).style.display = 'block';
        document.getElementById('titulo-' + rol).innerText = "Registro - " + rol.toUpperCase();
        document.getElementById('link-' + rol).innerText = "¿Ya tienes cuenta? Iniciar Sesión";
    }
}

function mostrarVistaPrevia(input, previewId, labelId, subId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById(previewId).src = e.target.result;
            document.getElementById(previewId).style.display = 'block';
            document.getElementById(labelId).style.display = 'none';
            document.getElementById(subId).style.display = 'none';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function procesarLogin(rol) {
    const usuario = document.getElementById('user-' + rol).value.trim();
    const password = document.getElementById('pass-' + rol).value.trim();
    if (!usuario || !password) return alert("Completa usuario y contraseña.");
    fetch('/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ usuario, password, rol: rol })
    }).then(res => res.json()).then(data => {
        if (data.status === 'success') window.location.href = data.redirect;
        else alert(data.message);
    });
}

function procesarRegistro(rol) {
    if (!confirm('¿Estás seguro de que deseas enviará tu solicitud de registro?')) return;
    let formData = new FormData();
    formData.append('rol', rol);

    if (rol === 'proveedores') {
        formData.append('foto', document.getElementById('foto-prov').files[0]);
        formData.append('nombre_proveedor', document.getElementById('nom-prov').value);
        formData.append('encargado', document.getElementById('encargado-prov').value);
        formData.append('responsable', document.getElementById('responsable-prov').value);
        formData.append('telefono', document.getElementById('tel-prov').value);
        formData.append('direccion', document.getElementById('dir-prov').value);
        formData.append('codigo_postal', document.getElementById('cp-prov').value);
        formData.append('descripcion', document.getElementById('desc-prov').value);
        formData.append('correo', document.getElementById('correo-prov').value);
    } else {
        let pref = (rol === 'administracion') ? 'admin' : 'corp';
        formData.append('foto', document.getElementById('foto-' + pref).files[0]);
        formData.append('apellido_paterno', document.getElementById('ap-' + pref).value);
        formData.append('apellido_materno', document.getElementById('am-' + pref).value);
        formData.append('nombres', document.getElementById('nom-' + pref).value);
        formData.append('ciudad', document.getElementById('ciudad-' + pref).value);
        formData.append('cope', document.getElementById('cope-' + pref) ? document.getElementById('cope-' + pref).value : 'No especificado');
        formData.append('num_empleado', document.getElementById('num-' + pref).value);
        formData.append('area', document.getElementById('area-' + pref).value);

        if (rol === 'administracion') {
            formData.append('correo', document.getElementById('correo-admin').value);
            formData.append('subrol', document.getElementById('subrol-admin').value);
        } else if (rol === 'corporativos') {
            formData.append('correo', document.getElementById('correo-corp').value);
        }
    }

    fetch('/registro', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        alert(data.message);
        if (data.status === 'success') { document.getElementById('registro-view-' + rol).reset(); toggleModo(rol); }
    });
}

function cambiarVistaAdmin(vista) {
    const vistas = ['facturas', 'facturas-finales', 'documentos-contables', 'pendientes', 'accesos', 'lista-prov', 'lista-corp', 'lista-admin', 'reportes', 'seccion-reportes', 'archivo', 'unidades'];
    vistas.forEach(v => {
        let el = document.getElementById('vista-' + v);
        if (el) el.style.display = 'none';
    });

    let vistaId = vista;
    if (vista === 'facturas_finales') vistaId = 'facturas-finales';
    if (vista === 'documentos_contables') vistaId = 'documentos-contables';

    let elVista = document.getElementById('vista-' + vistaId);
    if (elVista) elVista.style.display = 'block';

    if (vista === 'pendientes') cargarPendientes();
    if (vista === 'accesos') cargarAccesos();
    if (vista === 'lista-prov') cargarListaUsuarios('proveedores', 'tabla-lista-prov');
    if (vista === 'lista-corp') cargarListaUsuarios('corporativos', 'tabla-lista-corp');
    if (vista === 'lista-admin') cargarListaUsuarios('administracion', 'tabla-lista-admin');
    if (vista === 'unidades') cargarUnidades();
    if (vista === 'seccion-reportes' && typeof cargarSeccionReportes === 'function') cargarSeccionReportes();

    if (vista === 'reportes' && typeof cargarReportesAdmin === 'function') cargarReportesAdmin();
    if ((vista === 'facturas' || vista === 'facturas_finales' || vista === 'documentos_contables') && typeof cargarFacturas === 'function') cargarFacturas();
}

function cambiarVistaProv(vista) {
    document.getElementById('vista-facturas').style.display = 'none';
    if (document.getElementById('vista-reportes-prov')) {
        document.getElementById('vista-reportes-prov').style.display = 'none';
    }
    if (document.getElementById('vista-facturas-finales')) {
        document.getElementById('vista-facturas-finales').style.display = 'none';
    }
    if (document.getElementById('vista-archivo')) {
        document.getElementById('vista-archivo').style.display = 'none';
    }

    if (vista === 'facturas') {
        document.getElementById('vista-facturas').style.display = 'block';
    } else if (vista === 'reportes') {
        document.getElementById('vista-reportes-prov').style.display = 'block';
        if (typeof cargarReportesProv === 'function') cargarReportesProv();
    } else if (vista === 'facturas_finales') {
        document.getElementById('vista-facturas-finales').style.display = 'block';
        if (typeof cargarFacturas === 'function') cargarFacturas();
    } else if (vista === 'archivo') {
        if (document.getElementById('vista-archivo')) {
            document.getElementById('vista-archivo').style.display = 'block';
        }
        if (typeof cargarFacturas === 'function') cargarFacturas();
    }
}

function cambiarVistaCorp(vista) {
    if (document.getElementById('vista-cotizaciones-corp')) {
        document.getElementById('vista-cotizaciones-corp').style.display = 'none';
    }
    if (document.getElementById('vista-archivo-corp')) {
        document.getElementById('vista-archivo-corp').style.display = 'none';
    }

    if (vista === 'cotizaciones') {
        if (document.getElementById('vista-cotizaciones-corp')) document.getElementById('vista-cotizaciones-corp').style.display = 'block';
    } else if (vista === 'archivo') {
        if (document.getElementById('vista-archivo-corp')) document.getElementById('vista-archivo-corp').style.display = 'block';
    }
    
    if (typeof cargarFacturas === 'function') cargarFacturas();
}

function cerrarModal(id) { document.getElementById(id).style.display = 'none'; }

function filtrarTabla(inputId, tbodyId) {
    const input = document.getElementById(inputId);
    const filtro = input.value.toLowerCase();
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    const filas = tbody.getElementsByTagName('tr');

    for (let i = 0; i < filas.length; i++) {
        if (filas[i].cells.length === 1 && filas[i].cells[0].colSpan > 1) {
            continue;
        }

        const textoFila = filas[i].textContent.toLowerCase();

        if (textoFila.includes(filtro)) {
            filas[i].style.display = '';
        } else {
            filas[i].style.display = 'none';
        }
    }
}

function cargarPendientes() {
    fetch('/api/pendientes').then(res => res.json()).then(data => {
        pendientesGlobal = data.pendientes;
        const tbody = document.getElementById('tabla-pendientes');
        tbody.innerHTML = '';
        if (pendientesGlobal.length === 0) { tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No hay solicitudes</td></tr>'; return; }
        pendientesGlobal.forEach(user => {
            const id = user.rol === 'proveedores' ? user.correo : user.num_empleado;
            const nom = user.rol === 'proveedores' ? user.nombre_proveedor : `${user.nombres} ${user.apellido_paterno}`;
            tbody.innerHTML += `<tr><td><strong>${nom}</strong></td><td style="text-transform: capitalize;">${user.rol}</td><td>${id}</td>
                                <td><button class="btn-success" onclick="abrirModalDetalles('${id}')">Ver Detalles</button></td></tr>`;
        });
    });
}

function abrirModalDetalles(identificador) {
    const user = pendientesGlobal.find(u => u.correo === identificador || u.num_empleado === identificador);
    if (!user) return;

    let html = `<img src="/static/registros_confirmar/${user.foto_ruta}" class="modal-photo" onerror="this.src='https://via.placeholder.com/100/112641/40916c?text=Foto'">
                <div class="form-grid" style="grid-template-columns: 1fr 1fr; text-align: left; margin-bottom: 20px;">`;

    let ciudadCopeTexto = user.ciudad ? `${user.ciudad} / ${user.cope || 'N/A'}` : 'No especificada';

    if (user.rol === 'proveedores') {
        html += `
            <div class="modal-info-line full-width"><strong style="color:#40916c;">Razón Social / Empresa:</strong> ${user.nombre_proveedor}</div>
            <div class="modal-info-line"><strong>Encargado Principal:</strong> ${user.encargado}</div>
            <div class="modal-info-line"><strong>Resp. en Turno:</strong> ${user.responsable || 'No especificado'}</div>
            <div class="modal-info-line"><strong>Teléfono:</strong> ${user.telefono}</div>
            <div class="modal-info-line"><strong>Correo:</strong> ${user.correo}</div>
            <div class="modal-info-line full-width"><strong>Dirección:</strong> ${user.direccion}</div>
            <div class="modal-info-line"><strong>Código Postal:</strong> ${user.codigo_postal || 'No especificado'}</div>
            <div class="modal-info-line full-width"><strong>Giro / Descripción:</strong> <div class="texto-largo" style="margin-top:5px; padding:10px; background:#1b4332; border-radius:5px;">${user.descripcion || 'Sin descripción'}</div></div>
        `;
    } else {
        html += `
            <div class="modal-info-line full-width"><strong style="color:#0284c7;">Nombre Completo:</strong> ${user.nombres} ${user.apellido_paterno} ${user.apellido_materno || ''}</div>
            <div class="modal-info-line"><strong>Num. Empleado:</strong> ${user.num_empleado}</div>
            <div class="modal-info-line"><strong>Ubicación Base:</strong> <span style="color:#0ea5e9; font-weight:bold;">${ciudadCopeTexto}</span></div>
            <div class="modal-info-line"><strong>Área:</strong> ${user.area}</div>
            <div class="modal-info-line"><strong>Correo Alertas:</strong> ${user.correo || 'N/A'}</div>
            <div class="modal-info-line"><strong>Rol Solicitado:</strong> <span style="text-transform: capitalize;">${user.rol}</span> ${user.subrol ? '<strong style="color:#f59e0b">(' + user.subrol + ')</strong>' : ''}</div>
        `;
    }

    html += `</div>`;

    document.getElementById('modal-contenido').innerHTML = html;
    document.getElementById('btn-aceptar').setAttribute('onclick', `procesarAccion('${identificador}', 'aprobar')`);
    document.getElementById('btn-rechazar').setAttribute('onclick', `procesarAccion('${identificador}', 'rechazar')`);

    document.getElementById('modal-detalles').style.display = 'flex';
}

function procesarAccion(identificador, accion) {
    if (accion === 'rechazar') {
        cerrarModal('modal-detalles');
        if (typeof abrirModalRechazo === 'function') {
            abrirModalRechazo(identificador, 'usuario');
        } else {
            alert("Error: No se pudo cargar el componente de rechazo.");
        }
        return;
    }

    let mensaje = '¿¿Aceptar usuario y generar credenciales?';
    if (confirm(mensaje)) {
        fetch(`/api/${accion}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ identificador: identificador })
        }).then(res => res.json()).then(data => { alert(data.message); cerrarModal('modal-detalles'); cargarPendientes(); });
    }
}

function abrirModalDetallesUsuario(usuarioId) {
    const user = usuariosGlobal.find(u => u.usuario === usuarioId);
    if (!user) return;

    const dp = user.datos_perfil;
    const carpeta = (user.rol === 'proveedores') ? 'logos_proveedores' : ((user.rol === 'administracion') ? 'foto_administracion' : 'foto_corporativos');
    const rolTexto = user.rol.toUpperCase();
    let ciudadCopeTexto = dp.ciudad ? `${dp.ciudad} / ${dp.cope || 'N/A'}` : 'No especificada';

    let htmlContent = `
        <div class="pdf-header-doc">
            <h2>RED ULTIMA MILLA DEL NOROESTE (RUMN)</h2>
            <p>PERFIL DE USUARIO - ${rolTexto}</p>
        </div>
        <div class="pdf-body">
            <img src="/static/${carpeta}/${dp.foto_ruta}" class="pdf-photo-doc" onerror="this.src='https://via.placeholder.com/150/ffffff/000000?text=Foto'">
            <div class="pdf-details">
    `;

    if (user.rol === 'proveedores') {
        htmlContent += `
            <div class="pdf-section-title">■ DATOS DE LA EMPRESA</div>
            <div class="pdf-line"><strong>Razón Social:</strong> ${dp.nombre_proveedor}</div>
            <div class="pdf-line"><strong>Descripción:</strong> <span class="texto-largo">${dp.descripcion}</span></div>
            <div class="pdf-line"><strong>Usuario Sistema:</strong> ${user.usuario}</div>
            <br>
            <div class="pdf-section-title">■ INFORMACIÓN DE CONTACTO</div>
            <div class="pdf-line"><strong>Encargado Principal:</strong> ${dp.encargado}</div>
            <div class="pdf-line"><strong>Teléfono:</strong> ${dp.telefono}</div>
            <div class="pdf-line"><strong>Correo:</strong> ${dp.correo}</div>
            <div class="pdf-line"><strong>Dirección:</strong> <span class="texto-largo">${dp.direccion} (C.P. ${dp.codigo_postal})</span></div>
        `;
    } else {
        htmlContent += `
            <div class="pdf-section-title">■ INFORMACIÓN DEL EMPLEADO</div>
            <div class="pdf-line"><strong>Nombre Completo:</strong> ${dp.nombres} ${dp.apellido_paterno} ${dp.apellido_materno || ''}</div>
            <div class="pdf-line"><strong>Ubicación Base:</strong> <span style="color:#0284c7; font-weight:bold;">${ciudadCopeTexto}</span></div>
            <div class="pdf-line"><strong>Área Asignada:</strong> ${dp.area}</div>
            <div class="pdf-line"><strong>Número Empleado:</strong> ${dp.num_empleado}</div>
            <div class="pdf-line"><strong>Correo Electrónico:</strong> ${dp.correo || 'N/A'}</div>
            <br>
            <div class="pdf-section-title">■ CREDENCIALES DEL SISTEMA</div>
            <div class="pdf-line"><strong>Usuario Asignado:</strong> ${user.usuario}</div>
            <div class="pdf-line"><strong>Nivel de Acceso:</strong> ${rolTexto} ${dp.subrol ? ' - <strong style="color:#f59e0b">' + dp.subrol + '</strong>' : ''}</div>
        `;
    }

    const fechaHoy = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' });
    htmlContent += `
            </div>
        </div>
        <div class="pdf-footer">Documento extraído de la Base de Datos Central el: ${fechaHoy}</div>
    `;

    document.getElementById('pdf-perfil-contenido').innerHTML = htmlContent;
    document.getElementById('modal-detalles-usuario').style.display = 'flex';
}

function descargarPDFUsuario() {
    const elemento = document.getElementById('pdf-perfil-contenido');
    const opciones = {
        margin: 0.4,
        filename: 'Perfil_Usuario_RUMN.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opciones).from(elemento).save();
}

function cargarListaUsuarios(rolBuscado, idTabla) {
    fetch('/api/accesos').then(res => res.json()).then(data => {
        usuariosGlobal = data.usuarios || [];
        const tbody = document.getElementById(idTabla);
        tbody.innerHTML = '';

        let filtrados = usuariosGlobal.filter(u => u.rol === rolBuscado && u.datos_perfil);

        // --- ¡NUEVO!: FILTRO GEOGRÁFICO PARA EL SUPERVISOR EN LA INTERFAZ ---
        let subrolActualElement = document.getElementById('subrol-actual');
        let ciudadActualElement = document.getElementById('ciudad-actual');
        let subrolActual = subrolActualElement ? subrolActualElement.value : '';
        let miCiudad = ciudadActualElement ? ciudadActualElement.value : '';

        // El filtro de ciudad para supervisores ha sido removido porque los proveedores ahora son globales
        // -------------------------------------------------------------------

        if (filtrados.length === 0) { tbody.innerHTML = `<tr><td colspan="12" style="text-align:center;">No hay usuarios en esta sección</td></tr>`; return; }

        filtrados.forEach(u => {
            const dp = u.datos_perfil;
            const carpeta = (rolBuscado === 'proveedores') ? 'logos_proveedores' : ((rolBuscado === 'administracion') ? 'foto_administracion' : 'foto_corporativos');
            const img = `<img src="/static/${carpeta}/${dp.foto_ruta}" class="mini-profile-pic" onerror="this.src='https://via.placeholder.com/40/112641/40916c?text=X'">`;

            const ciudad = dp.ciudad ? `${dp.ciudad} <br><small style="color:#f59e0b;">${dp.cope || ''}</small>` : 'No especificada';

            const btnAcciones = `
                <div class="acciones-td" style="flex-direction: column;">
                    <button class="btn-danger" style="background-color: #b45309; margin-bottom: 5px; width: 100%;" onclick="abrirModalDetallesUsuario('${u.usuario}')">📄 Ver PDF / Detalles</button>
                    <div style="display:flex; gap:5px; width:100%;">
                        <button class="btn-info" onclick="abrirModalEditar('${u.usuario}')" style="flex:1;">Editar</button>
                        <button class="btn-danger-sm" onclick="eliminarUsuario('${u.usuario}', '${rolBuscado}')" style="flex:1;">Eliminar</button>
                    </div>
                </div>`;

            if (rolBuscado === 'proveedores') {
                tbody.innerHTML += `<tr><td>${img}</td><td><strong>${dp.nombre_proveedor}</strong></td><td style="color:#40916c">${u.usuario}</td><td>${dp.encargado}</td><td>${dp.responsable || 'N/A'}</td><td>${dp.telefono}</td><td>${dp.correo}</td><td>${dp.direccion}</td><td>${dp.codigo_postal}</td><td><div style="min-width: 400px; width: 400px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4;">${dp.descripcion}</div></td><td>${btnAcciones}</td></tr>`;
            } else {
                let areaYRol = dp.subrol ? `${dp.area} <br><small style="color:#f59e0b; font-weight:bold;">[${dp.subrol}]</small>` : dp.area;
                tbody.innerHTML += `<tr><td>${img}</td><td><strong>${dp.nombres} ${dp.apellido_paterno} ${dp.apellido_materno || ''}</strong><br><small style="color:#a3b1c6;">${dp.correo || ''}</small></td><td style="color:#40916c">${u.usuario}</td><td>${dp.num_empleado}</td><td><span style="color:#0ea5e9; font-weight:bold;">${ciudad}</span></td><td>${areaYRol}</td><td>${btnAcciones}</td></tr>`;
            }
        });
    });
}

function eliminarUsuario(usuarioId, rol) {
    if (confirm(`⚠️ ATENCIÓN ⚠️\n¿¿Eliminar COMPLETAMENTE a este usuario? Esta acción no se puede deshacer.`)) {
        fetch('/api/eliminar_usuario', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ usuario: usuarioId })
        }).then(res => res.json()).then(data => { alert(data.message); cargarListaUsuarios(rol, 'tabla-lista-' + (rol === 'proveedores' ? 'prov' : (rol === 'administracion' ? 'admin' : 'corp'))); cargarAccesos(); });
    }
}

function abrirModalEditar(usuarioId) {
    const user = usuariosGlobal.find(u => u.usuario === usuarioId);
    if (!user) return;
    document.getElementById('edit-usuario-id').value = user.usuario;
    document.getElementById('edit-rol').value = user.rol;
    document.getElementById('edit-foto').value = '';
    document.getElementById('edit-preview').style.display = 'none';
    document.getElementById('edit-label').style.display = 'block';
    document.getElementById('edit-sub').style.display = 'block';

    const dp = user.datos_perfil;
    let camposHtml = '';

    let htmlCiudadCope = `
        <div class="input-group">
            <label>Ciudad / Municipio Base</label>
            <select name="ciudad" id="edit-ciudad" class="input-form" required onchange="actualizarCopeSelect('edit-ciudad', 'edit-cope')">
                <option value="Tijuana" ${dp.ciudad === 'Tijuana' ? 'selected' : ''}>Tijuana</option>
                <option value="Tecate" ${dp.ciudad === 'Tecate' ? 'selected' : ''}>Tecate</option>
                <option value="Ensenada" ${dp.ciudad === 'Ensenada' ? 'selected' : ''}>Ensenada</option>
                <option value="San Quintin" ${dp.ciudad === 'San Quintin' ? 'selected' : ''}>San Quintin</option>
                <option value="Mexicali" ${dp.ciudad === 'Mexicali' ? 'selected' : ''}>Mexicali</option>
                <option value="San Luis Rio Colorado" ${dp.ciudad === 'San Luis Rio Colorado' ? 'selected' : ''}>San Luis Rio Colorado</option>
            </select>
        </div>
        <div class="input-group">
            <label>COPE / Edificio</label>
            <select name="cope" id="edit-cope" class="input-form" required></select>
        </div>
    `;

    if (user.rol === 'proveedores') {
        camposHtml += `<div class="input-group full-width"><label>Empresa</label><input type="text" name="nombre_proveedor" value="${dp.nombre_proveedor}" required></div><div class="input-group"><label>Encargado</label><input type="text" name="encargado" value="${dp.encargado}" required></div><div class="input-group"><label>Responsable</label><input type="text" name="responsable" value="${dp.responsable || ''}"></div><div class="input-group"><label>Teléfono</label><input type="text" name="telefono" value="${dp.telefono}" required></div><div class="input-group"><label>Correo</label><input type="text" name="correo" value="${dp.correo}" required></div><div class="input-group"><label>C.P.</label><input type="text" name="codigo_postal" value="${dp.codigo_postal}" required></div><div class="input-group full-width"><label>Dirección</label><input type="text" name="direccion" value="${dp.direccion}" required></div><div class="input-group full-width"><label>Descripción</label><textarea name="descripcion" required style="width: 100%; min-height: 80px; padding: 12px 15px; border-radius: 8px; border: 1px solid #1f395a; background-color: #112641; color: white; font-family: 'Poppins', sans-serif; resize: vertical;">${dp.descripcion}</textarea></div>`;
    } else if (user.rol === 'administracion') {
        camposHtml += `<div class="input-group full-width"><label>Nombre(s)</label><input type="text" name="nombres" value="${dp.nombres}" required></div><div class="input-group"><label>Apellido Paterno</label><input type="text" name="apellido_paterno" value="${dp.apellido_paterno}" required></div><div class="input-group"><label>Apellido Materno</label><input type="text" name="apellido_materno" value="${dp.apellido_materno || ''}"></div>${htmlCiudadCope}<div class="input-group"><label>Núm. Empleado</label><input type="text" name="num_empleado" value="${dp.num_empleado}" required></div><div class="input-group"><label>Área</label><input type="text" name="area" value="${dp.area}" required></div><div class="input-group"><label>Correo Alertas</label><input type="email" name="correo" value="${dp.correo || ''}" required></div><div class="input-group"><label>Puesto</label><select name="subrol" class="input-form" required><option value="Jefatura" ${dp.subrol === 'Jefatura' ? 'selected' : ''}>Jefatura</option><option value="Supervisor" ${dp.subrol === 'Supervisor' ? 'selected' : ''}>Supervisor</option></select></div>`;
    } else if (user.rol === 'corporativos') {
        camposHtml += `<div class="input-group full-width"><label>Nombre(s)</label><input type="text" name="nombres" value="${dp.nombres}" required></div><div class="input-group"><label>Apellido Paterno</label><input type="text" name="apellido_paterno" value="${dp.apellido_paterno}" required></div><div class="input-group"><label>Apellido Materno</label><input type="text" name="apellido_materno" value="${dp.apellido_materno || ''}"></div>${htmlCiudadCope}<div class="input-group"><label>Núm. Empleado</label><input type="text" name="num_empleado" value="${dp.num_empleado}" required></div><div class="input-group"><label>Área</label><input type="text" name="area" value="${dp.area}" required></div><div class="input-group full-width"><label>Correo Electrónico</label><input type="email" name="correo" value="${dp.correo || ''}" required></div>`;
    }

    document.getElementById('edit-campos-dinamicos').innerHTML = camposHtml;
    if (document.getElementById('edit-ciudad')) {
        actualizarCopeSelect('edit-ciudad', 'edit-cope', dp.cope);
    }
    document.getElementById('modal-editar').style.display = 'flex';
}

function procesarEdicion() {
    if (!confirm("⚠️ ¿Estás seguro de guardar los cambios para este usuario?")) return;

    let formData = new FormData(document.getElementById('form-editar'));
    formData.append('usuario_id', document.getElementById('edit-usuario-id').value);
    formData.append('rol', document.getElementById('edit-rol').value);

    let elCiudad = document.getElementById('edit-ciudad');
    if (elCiudad) formData.append('ciudad', elCiudad.value);

    let elCope = document.getElementById('edit-cope');
    if (elCope) formData.append('cope', elCope.value);

    const foto = document.getElementById('edit-foto').files[0];
    if (foto) formData.append('foto', foto);
    fetch('/api/editar_usuario', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        alert(data.message);
        if (data.status === 'success') { cerrarModal('modal-editar'); let rol = document.getElementById('edit-rol').value; cargarListaUsuarios(rol, 'tabla-lista-' + (rol === 'proveedores' ? 'prov' : (rol === 'administracion' ? 'admin' : 'corp'))); }
    });
}

function togglePass(id) {
    let input = document.getElementById('pass-' + id);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

function cargarAccesos() {
    fetch('/api/accesos').then(res => res.json()).then(data => {
        const tbody = document.getElementById('tabla-accesos');
        tbody.innerHTML = '';
        if (!data.usuarios || data.usuarios.length === 0) { tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No hay credenciales</td></tr>'; return; }

        data.usuarios.forEach(user => {
            if (user.datos_perfil) {
                let nombreCompleto = '';
                if (user.rol === 'proveedores') {
                    nombreCompleto = user.datos_perfil.nombre_proveedor;
                } else {
                    nombreCompleto = `${user.datos_perfil.nombres} ${user.datos_perfil.apellido_paterno}`;
                }

                let rolYNombre = `<span style="text-transform: capitalize; font-weight:bold; color:#0284c7;">${user.rol}</span><br><small style="color:#a3b1c6;">${nombreCompleto}</small>`;

                let passHtml = `
                    <div style="display:flex; align-items:center; gap:10px;">
                        <input type="password" value="${user.password}" id="pass-${user.usuario}" readonly style="background:transparent; border:none; color:#f59e0b; font-weight:bold; letter-spacing:2px; width:120px; outline:none;">
                        <button onclick="togglePass('${user.usuario}')" style="background:none; border:none; cursor:pointer; font-size:18px;" title="Ver Contraseña">👁️</button>
                    </div>`;

                tbody.innerHTML += `<tr><td>${rolYNombre}</td><td><strong style="color:#40916c;">${user.usuario}</strong></td><td>${passHtml}</td><td><button class="btn-info" onclick="renovarPassword('${user.usuario}')">🔄 Renovar Clave</button></td></tr>`;
            }
        });
    });
}

function renovarPassword(usuarioId) {
    if (confirm('¿Generar una NUEVA contraseña para este usuario? La contraseña anterior dejará de funcionar.')) {
        fetch('/api/renovar_password', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ usuario: usuarioId })
        }).then(res => res.json()).then(data => { alert(data.message); cargarAccesos(); });
    }
}

function abrirMiPerfil() {
    const dateSpan = document.getElementById('pdf-fecha');
    if (dateSpan) {
        const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
        dateSpan.innerText = new Date().toLocaleDateString('es-MX', opciones);
    }
    document.getElementById('modal-mi-perfil').style.display = 'flex';
}

function descargarPDF() {
    if (confirm('¿¿Confirmas que deseas descargar este perfil en formato PDF?')) {
        const elemento = document.getElementById('pdf-content');
        const opciones = {
            margin: 0.4,
            filename: 'Perfil_Usuario_RUMN.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        html2pdf().set(opciones).from(elemento).save();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById('vista-pendientes')) { cambiarVistaAdmin('facturas'); }
    if (document.getElementById('vista-reportes-prov')) { cambiarVistaProv('facturas'); }
    if (document.getElementById('vista-cotizaciones-corp')) { cambiarVistaCorp('cotizaciones'); }
});