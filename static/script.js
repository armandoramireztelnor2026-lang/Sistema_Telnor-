
if (typeof window.mostrarLoaderDinamico !== 'function') {
    window.mostrarLoaderDinamico = function(textoPrincipal, textoSecundario) {
        let loader = document.getElementById('loader-confirmacion');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'loader-confirmacion';
            loader.innerHTML = `
                <div class="loader-box">
                    <div class="spinner"></div>
                    <div class="loader-text" id="loader-txt-main"></div>
                    <div style="color: #a3b1c6; font-size: 0.85em; margin-top:-10px;" id="loader-txt-sub"></div>
                </div>
            `;
            document.body.appendChild(loader);
        }
        const txtMain = document.getElementById('loader-txt-main');
        const txtSub = document.getElementById('loader-txt-sub');
        if (txtMain) txtMain.innerText = textoPrincipal || 'Procesando...';
        if (txtSub) txtSub.innerText = textoSecundario || 'Por favor espera un momento...';
        loader.style.zIndex = '99999999';
        loader.style.display = 'flex';
    };
}
if (typeof window.ocultarLoaderDinamico !== 'function') {
    window.ocultarLoaderDinamico = function() {
        let loader = document.getElementById('loader-confirmacion');
        if (loader) loader.style.display = 'none';
    };
}


// ==========================================
// LÓGICA DE PAGINACIÓN GLOBAL
// ==========================================
window.paginacionEstado = {};

window.cambiarPagina = function(tbodyId, direccion) {
    if (!window.paginacionEstado[tbodyId]) window.paginacionEstado[tbodyId] = 1;
    window.paginacionEstado[tbodyId] += direccion;
    aplicarPaginacion(tbodyId, 20, false);
};

window.aplicarPaginacion = function(tbodyId, itemsPerPage = 20, resetPage = true) {

    if (resetPage) {
        window.paginacionEstado[tbodyId] = 1;
    }
    
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    
    const filas = Array.from(tbody.getElementsByTagName('tr')).filter(tr => {
        // Ignorar filas que dicen "No hay datos"
        if (tr.cells.length === 1 && tr.cells[0].colSpan > 1) return false;
        // Ignorar filas ocultas por el buscador
        return !tr.classList.contains('oculto-por-filtro');
    });
    
    const totalItems = filas.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
    
    let currentPage = window.paginacionEstado[tbodyId] || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;
    window.paginacionEstado[tbodyId] = currentPage;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    
    // Mostrar/Ocultar filas basadas en la página actual
    let idx = 0;
    for (let tr of tbody.getElementsByTagName('tr')) {
        if (tr.cells.length === 1 && tr.cells[0].colSpan > 1) continue;
        
        if (tr.classList.contains('oculto-por-filtro')) {
            tr.style.display = 'none';
        } else {
            if (idx >= startIndex && idx < endIndex) {
                tr.style.display = '';
            } else {
                tr.style.display = 'none';
            }
            idx++;
        }
    }
    
    // Contenedor de controles
    let pagContainer = document.getElementById('paginacion-' + tbodyId);
    if (!pagContainer) {
        pagContainer = document.createElement('div');
        pagContainer.id = 'paginacion-' + tbodyId;
        pagContainer.style.marginTop = '15px';
        pagContainer.style.display = 'flex';
        pagContainer.style.justifyContent = 'space-between';
        pagContainer.style.alignItems = 'center';
        
        let tableElement = tbody.closest('table');
        if (tableElement) {
            let wrapper = tableElement.closest('.table-responsive') || tableElement.closest('.admin-container') || tableElement.parentNode;
            if (wrapper === tableElement.parentNode) {
                tableElement.parentNode.insertBefore(pagContainer, tableElement.nextSibling);
            } else {
                wrapper.parentNode.insertBefore(pagContainer, wrapper.nextSibling);
            }
        }
    }
    
    if (totalItems <= itemsPerPage) {
        pagContainer.style.display = 'none';
    } else {
        pagContainer.style.display = 'flex';
        pagContainer.innerHTML = `
            <span style="color:#a3b1c6; font-size:0.9em; font-weight:bold;">Mostrando ${totalItems === 0 ? 0 : startIndex + 1} - ${Math.min(endIndex, totalItems)} de ${totalItems} tickets</span>
            <div style="display:flex; align-items:center;">
                <button onclick="cambiarPagina('${tbodyId}', -1)" ${currentPage === 1 ? 'disabled style="opacity:0.5; cursor:not-allowed; padding:6px 15px; margin-right:10px; font-size:0.85em; font-weight:bold; background:#334155; color:white; border:none; border-radius:6px;"' : 'style="padding:6px 15px; margin-right:10px; font-size:0.85em; font-weight:bold; background:#0ea5e9; color:white; border:none; border-radius:6px; cursor:pointer;"'}>◄ Anterior</button>
                <span style="color:white; font-size:0.9em; margin:0 15px; font-weight:bold;">Página ${currentPage} de ${totalPages}</span>
                <button onclick="cambiarPagina('${tbodyId}', 1)" ${currentPage === totalPages ? 'disabled style="opacity:0.5; cursor:not-allowed; padding:6px 15px; font-size:0.85em; font-weight:bold; background:#334155; color:white; border:none; border-radius:6px;"' : 'style="padding:6px 15px; font-size:0.85em; font-weight:bold; background:#0ea5e9; color:white; border:none; border-radius:6px; cursor:pointer;"'}>Siguiente ►</button>
            </div>
        `;
    }
};
// ==========================================

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
        formData.append('ciudad', document.getElementById('ciudad-prov').value);
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

function marcarBotonActivo(vista) {
    document.querySelectorAll('.btn-sidebar').forEach(b => {
        let onclickAttr = b.getAttribute('onclick');
        if (onclickAttr) {
            let matchesView = onclickAttr.includes("('" + vista + "')");
            let matches10k = (vista === 'cotizaciones-10k' && (onclickAttr.includes("verCotizacionesMas10000") || onclickAttr.includes("cotizaciones-10k")));
            let matchesFF = ((vista === 'facturas-finales' || vista === 'facturas_finales') && (onclickAttr.includes("facturas-finales") || onclickAttr.includes("facturas_finales")));
            let matchesDoc = ((vista === 'documentos-contables' || vista === 'documentos_contables') && (onclickAttr.includes("documentos-contables") || onclickAttr.includes("documentos_contables")));
            let matchesLib = ((vista === 'liberar-doc-contable' || vista === 'liberar_doc_contable') && (onclickAttr.includes("liberar-doc-contable") || onclickAttr.includes("liberar_doc_contable")));
            
            if (matchesView || matches10k || matchesFF || matchesDoc || matchesLib) {
                let nav = b.closest('.nav-menu') || b.closest('.sidebar');
                if (nav) {
                    nav.querySelectorAll('.btn-sidebar').forEach(btn => btn.classList.remove('active'));
                    b.classList.add('active');
                }
            }
        }
    });
}

window.obtenerNombresDelegacion = window.obtenerNombresDelegacion || function(ticketId, rolTitularBase) {
    let nombreAdmin = "Manuel Alejandro Marquez";
    let nombreSuper = "Samuel Giron";

    if (window.USUARIOS_ADMIN_SISTEMA && Array.isArray(window.USUARIOS_ADMIN_SISTEMA)) {
        let adminUser = window.USUARIOS_ADMIN_SISTEMA.find(u => u.subrol === 'Administrador');
        if (adminUser && adminUser.nombre_completo) {
            nombreAdmin = adminUser.nombre_completo;
        }
    }

    let subrolActual = document.getElementById('subrol-actual') ? document.getElementById('subrol-actual').value.trim() : '';
    let nombreActual = document.getElementById('nombre-usuario-actual') ? document.getElementById('nombre-usuario-actual').value.trim() : '';

    if (subrolActual === 'Supervisor' && nombreActual) {
        nombreSuper = nombreActual;
    } else if (subrolActual === 'Administrador' && nombreActual) {
        nombreAdmin = nombreActual;
    }

    if (rolTitularBase === 'Supervisor') {
        return {
            titular: `Supervisor: ${nombreSuper}`,
            suplente: `Administrador: ${nombreAdmin}`,
            titularTexto: `el Supervisor (${nombreSuper})`
        };
    } else {
        return {
            titular: `Administrador: ${nombreAdmin}`,
            suplente: `Supervisor: ${nombreSuper}`,
            titularTexto: `el Administrador (${nombreAdmin})`
        };
    }
};

window.solicitarConfirmacionDelegacion = window.solicitarConfirmacionDelegacion || function(param1, param2) {
    let callback = null;
    let info = {};
    if (typeof param1 === 'function' || typeof param1 === 'string') {
        callback = param1;
        info = param2 || {};
    } else {
        info = param1 || {};
        callback = param2;
    }

    window.callbackAccionDelegada = callback;
    const modal = document.getElementById('modal-advertencia-delegacion');
    if (modal) {
        const elTicket = document.getElementById('delegacion-ticket-id');
        const elProceso = document.getElementById('delegacion-proceso-nombre');
        const elDesc = document.getElementById('delegacion-proceso-desc');
        const elTitular = document.getElementById('delegacion-rol-titular');
        const elSuplente = document.getElementById('delegacion-rol-suplente');
        const elTitularTexto = document.getElementById('delegacion-titular-texto');

        let ticketTxt = info.ticket || 'N/A';
        if (info.unidad) {
            ticketTxt += ` | Eco #${info.unidad}`;
        }

        if (elTicket) elTicket.innerText = ticketTxt;
        if (elProceso) elProceso.innerText = info.proceso || 'Proceso Operativo';
        if (elDesc) elDesc.innerText = info.descripcion || 'Acción de contingencia operativa.';
        if (elTitular) elTitular.innerText = info.titular || '--';
        if (elSuplente) elSuplente.innerText = info.suplente || '--';
        if (elTitularTexto) elTitularTexto.innerText = info.titularTexto || info.titular || 'el responsable';

        modal.style.display = 'flex';
    } else {
        let msg = `⚠️ AVISO DE DELEGACIÓN / EMERGENCIA:\n\n` +
                  `Proceso a delegar: ${info.proceso || 'Acción Operativa'}\n` +
                  `¿A quién corresponde?: ${info.titular || 'Responsable'}\n` +
                  `Asumido por: ${info.suplente || 'Usuario en Suplencia'}\n\n` +
                  `Este botón es solo para emergencias o en caso de que ${info.titularTexto || 'el responsable'} no pueda confirmar desde su propio perfil.\n\n` +
                  `¿Estás enterado y deseas continuar a la interfaz habitual?`;
        if (confirm(msg)) {
            if (typeof callback === 'function') {
                callback();
            } else if (typeof callback === 'string') {
                try { (new Function(callback))(); } catch(e) { console.error(e); }
            }
        }
    }
};

window.cerrarModalAdvertenciaDelegacion = window.cerrarModalAdvertenciaDelegacion || function() {
    const modal = document.getElementById('modal-advertencia-delegacion');
    if (modal) modal.style.display = 'none';
    window.callbackAccionDelegada = null;
};

window.confirmarEnteradoDelegacion = window.confirmarEnteradoDelegacion || function() {
    const cb = window.callbackAccionDelegada;
    window.cerrarModalAdvertenciaDelegacion();
    if (typeof cb === 'function') {
        cb();
    } else if (typeof cb === 'string') {
        try { (new Function(cb))(); } catch(e) { console.error(e); }
    }
};

window.delegarLiberarTicket = window.delegarLiberarTicket || function(id, unidad) {
    const roles = window.obtenerNombresDelegacion(id, 'Administrador');
    window.solicitarConfirmacionDelegacion(() => {
        if (typeof abrirModalLiberarTicket === 'function') {
            abrirModalLiberarTicket(id);
        } else if (typeof asumirLiberacionAdmin === 'function') {
            asumirLiberacionAdmin(id, true);
        }
    }, {
        proceso: "Liberar Ticket para Facturación Fiscal",
        descripcion: "Autorización administrativa y contable previa para permitir al taller proveedor emitir y subir su factura fiscal al sistema.",
        titular: roles.titular,
        suplente: roles.suplente,
        titularTexto: roles.titularTexto,
        ticket: id,
        unidad: unidad
    });
};

window.delegarAprobar10k = window.delegarAprobar10k || function(id, unidad) {
    const roles = window.obtenerNombresDelegacion(id, 'Administrador');
    window.solicitarConfirmacionDelegacion(() => {
        if (typeof accion10k === 'function') {
            accion10k(id, 'aprobar', true);
        } else if (typeof abrirModalAprobar10k === 'function') {
            abrirModalAprobar10k(id, true);
        }
    }, {
        proceso: "Aprobación de Cotización Mayor a $10,000 hacia Corporativos",
        descripcion: "Filtro y autorización previa de presupuesto de alto costo (mayor a $10,000 MXN) para canalizar a Corporativos.",
        titular: roles.titular,
        suplente: roles.suplente,
        titularTexto: roles.titularTexto,
        ticket: id,
        unidad: unidad
    });
};

window.cerrarModalAlertaCortaDelegacion = function() {
    const modal = document.getElementById('modal-alerta-corta-delegacion');
    if (modal) modal.style.display = 'none';
    window.callbackAlertaCortaDelegacion = null;
};

window.confirmarAlertaCortaDelegacion = function() {
    const cb = window.callbackAlertaCortaDelegacion;
    window.cerrarModalAlertaCortaDelegacion();
    if (typeof cb === 'function') {
        cb();
    } else if (typeof cb === 'string') {
        try { (new Function(cb))(); } catch(e) { console.error(e); }
    }
};

window.mostrarAlertaCortaDelegacion = function(mensaje, callback) {
    window.callbackAlertaCortaDelegacion = callback;
    const modal = document.getElementById('modal-alerta-corta-delegacion');
    const msgEl = document.getElementById('alerta-corta-delegacion-msg');
    if (modal && msgEl) {
        msgEl.innerHTML = mensaje;
        modal.style.display = 'flex';
    } else {
        const textoPlano = (mensaje || '').replace(/<[^>]*>?/gm, '');
        if (confirm(`⚠️ DELEGACIÓN POR AUSENCIA\n\n${textoPlano}\n\n¿Deseas continuar?`)) {
            if (typeof callback === 'function') callback();
        }
    }
};

window.abrirVistaDelegada = function(tipo) {
    let mensaje = '';
    let callback = null;

    if (tipo === 'cotizaciones-10k') {
        callback = () => {
            if (typeof verCotizacionesMas10000 === 'function') verCotizacionesMas10000();
            else cambiarVistaAdmin('cotizaciones-10k');
        };
        mensaje = 'Estás ingresando a <strong style="color: #fbbf24;">Cotizaciones +10,000</strong> bajo el protocolo de <strong style="color: #fbbf24;">Delegación por Ausencia</strong> (suplencia del Administrador).<br><br>¿Deseas continuar?';
    } else if (tipo === 'liberar-doc-contable') {
        callback = () => cambiarVistaAdmin('liberar-doc-contable');
        mensaje = 'Estás ingresando a <strong style="color: #fbbf24;">Liberar Doc. Contable</strong> bajo el protocolo de <strong style="color: #fbbf24;">Delegación por Ausencia</strong> (suplencia del Administrador).<br><br>¿Deseas continuar?';
    } else if (tipo === 'facturas') {
        callback = () => cambiarVistaAdmin('facturas');
        mensaje = 'Estás ingresando a <strong style="color: #fbbf24;">Cotizaciones y Órdenes</strong> bajo el protocolo de <strong style="color: #fbbf24;">Delegación por Ausencia</strong> (suplencia del Supervisor).<br><br>¿Deseas continuar?';
    } else if (tipo === 'facturas_finales' || tipo === 'facturas-finales') {
        callback = () => cambiarVistaAdmin('facturas_finales');
        mensaje = 'Estás ingresando a <strong style="color: #fbbf24;">Facturas</strong> bajo el protocolo de <strong style="color: #fbbf24;">Delegación por Ausencia</strong> (suplencia del Supervisor).<br><br>¿Deseas continuar?';
    } else {
        callback = () => cambiarVistaAdmin(tipo);
        mensaje = 'Estás ingresando a esta sección bajo el protocolo de <strong style="color: #fbbf24;">Delegación por Ausencia</strong>.<br><br>¿Deseas continuar?';
    }

    if (typeof window.mostrarAlertaCortaDelegacion === 'function') {
        window.mostrarAlertaCortaDelegacion(mensaje, callback);
    } else {
        const textoPlano = (mensaje || '').replace(/<[^>]*>?/gm, '');
        if (confirm(`⚠️ DELEGACIÓN POR AUSENCIA\n\n${textoPlano}\n\n¿Deseas continuar?`)) {
            if (callback) callback();
        }
    }
};

function cambiarVistaAdmin(vista) {
    localStorage.setItem('activeViewAdmin', vista);
    marcarBotonActivo(vista);
    const vistas = ['facturas', 'facturas-finales', 'documentos-contables', 'liberar-doc-contable', 'pendientes', 'accesos', 'lista-prov', 'lista-corp', 'lista-admin', 'reportes', 'seccion-reportes', 'archivo', 'unidades', 'panel-control', 'cotizaciones-10k', 'ciudades-copes', 'analitica', 'retrabajo', 'tiempo-garantia', 'flujo-trabajo'];
    vistas.forEach(v => {
        let el = document.getElementById('vista-' + v);
        if (el) el.style.display = 'none';
    });

    let vistaId = vista;
    if (vista === 'facturas_finales') vistaId = 'facturas-finales';
    if (vista === 'documentos_contables') vistaId = 'documentos-contables';
    if (vista === 'liberar_doc_contable') vistaId = 'liberar-doc-contable';
    if (vista === 'tiempo_garantia') vistaId = 'tiempo-garantia';
    if (vista === 'flujo_trabajo') vistaId = 'flujo-trabajo';

    let elVista = document.getElementById('vista-' + vistaId);
    if (elVista) elVista.style.display = 'block';

    if (vista === 'pendientes') cargarPendientes();
    if (vista === 'accesos') cargarAccesos();
    if (vista === 'lista-prov') cargarListaUsuarios('proveedores', 'tabla-lista-prov');
    if (vista === 'lista-corp') cargarListaUsuarios('corporativos', 'tabla-lista-corp');
    if (vista === 'lista-admin') cargarListaUsuarios('administracion', 'tabla-lista-admin');
    if (vista === 'unidades') cargarUnidades();
    if (vista === 'seccion-reportes' && typeof cargarSeccionReportes === 'function') cargarSeccionReportes();

    if (vista === 'panel-control' && typeof cargarPanelControl === 'function') cargarPanelControl();
    if (vista === 'ciudades-copes' && typeof cargarCiudadesCopes === 'function') cargarCiudadesCopes();
    if (vista === 'reportes' && typeof cargarReportesAdmin === 'function') cargarReportesAdmin();
    if (vista === 'analitica' && typeof cargarAnalitica === 'function') cargarAnalitica();
    if (vista === 'retrabajo' && typeof cargarRetrabajosAdmin === 'function') cargarRetrabajosAdmin();
    if (vista === 'tiempo-garantia' || vista === 'tiempo_garantia') {
        if (typeof cargarTiempoGarantiaJefatura === 'function') {
            cargarTiempoGarantiaJefatura();
        } else {
            cargarListaUsuarios('proveedores', 'tabla-tiempo-garantia');
        }
    }
    if ((vista === 'facturas' || vista === 'facturas_finales' || vista === 'facturas-finales' || vista === 'documentos_contables' || vista === 'documentos-contables' || vista === 'liberar-doc-contable' || vista === 'liberar_doc_contable' || vista === 'archivo') && typeof cargarFacturas === 'function') cargarFacturas();
    if (vista === 'cotizaciones-10k' && typeof cargarCotizaciones10k === 'function') cargarCotizaciones10k();
}

function cambiarVistaProv(vista) {
    localStorage.setItem('activeViewProv', vista);
    marcarBotonActivo(vista);
    if (document.getElementById('vista-facturas')) document.getElementById('vista-facturas').style.display = 'none';
    if (document.getElementById('vista-reportes-prov')) {
        document.getElementById('vista-reportes-prov').style.display = 'none';
    }
    if (document.getElementById('vista-facturas-finales')) {
        document.getElementById('vista-facturas-finales').style.display = 'none';
    }
    if (document.getElementById('vista-archivo')) {
        document.getElementById('vista-archivo').style.display = 'none';
    }
    if (document.getElementById('vista-retrabajo')) {
        document.getElementById('vista-retrabajo').style.display = 'none';
    }

    if (vista === 'facturas') {
        if (document.getElementById('vista-facturas')) document.getElementById('vista-facturas').style.display = 'block';
    } else if (vista === 'reportes') {
        if (document.getElementById('vista-reportes-prov')) document.getElementById('vista-reportes-prov').style.display = 'block';
        if (typeof cargarReportesProv === 'function') cargarReportesProv();
    } else if (vista === 'facturas_finales') {
        if (document.getElementById('vista-facturas-finales')) document.getElementById('vista-facturas-finales').style.display = 'block';
        if (typeof cargarFacturas === 'function') cargarFacturas();
    } else if (vista === 'archivo') {
        if (document.getElementById('vista-archivo')) {
            document.getElementById('vista-archivo').style.display = 'block';
        }
        if (typeof cargarFacturas === 'function') cargarFacturas();
    } else if (vista === 'retrabajo') {
        if (document.getElementById('vista-retrabajo')) {
            document.getElementById('vista-retrabajo').style.display = 'block';
        }
        if (typeof cargarRetrabajosProveedor === 'function') cargarRetrabajosProveedor();
    }
}

function cambiarVistaCorp(vista) {
    localStorage.setItem('activeViewCorp', vista);
    marcarBotonActivo(vista);
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
            filas[i].classList.remove('oculto-por-filtro');
        } else {
            filas[i].classList.add('oculto-por-filtro');
        }
    }
    
    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion(tbodyId, 20, true);
    } else {
        for (let i = 0; i < filas.length; i++) {
            if (filas[i].cells.length === 1 && filas[i].cells[0].colSpan > 1) continue;
            filas[i].style.display = filas[i].classList.contains('oculto-por-filtro') ? 'none' : '';
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
        if (typeof aplicarPaginacion === 'function') aplicarPaginacion('tabla-pendientes', 20, true);
    });
}

async function cargarRetrabajosAdmin() {
    const tbody = document.getElementById('tabla-retrabajos');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:20px; color:#94a3b8;">Cargando retrabajos asignados...</td></tr>';
    
    try {
        const res = await fetch('/api/garantia/supervisor/lista');
        const data = await res.json();
        const retrabajos = data.retrabajos || [];
        window.retrabajosSupervisorGlobal = retrabajos;
        
        if (retrabajos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:25px; color:#94a3b8;">No hay solicitudes de garantía o retrabajo registradas para tu supervisión.</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        retrabajos.forEach(r => {
            let ticketId = r.ticket_original || r.ticket || r.id;
            let unidadStr = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            let fechaSalida = r.fecha_salida_taller || r.fecha_salida || (r.seccion_2 && (r.seccion_2.fecha_salida || r.seccion_2.fecha_ingreso)) || '--';
            let motivoLimpio = String(r.motivo_chofer || 'Sin motivo reportado').trim().replace(/^["'«»“”„]+|["'«»“”„]+$/g, '').trim();
            
            let tallerPrevio = (r.seccion_2 && r.seccion_2.proveedor) ? r.seccion_2.proveedor : 'Taller no asignado';
            
            let estadoColor = '#eab308';
            if (r.estado === 'Atendido') estadoColor = '#22c55e';
            if (r.estado === 'Rechazado') estadoColor = '#ef4444';
            
            let badgeEstado = `<span style="background: rgba(234, 179, 8, 0.15); color: ${estadoColor}; border: 1px solid ${estadoColor}; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; display: inline-block;">${r.estado || 'Pendiente'}</span>`;
            
            // Precio individual de cotizaciones
            let preciosHTML = '';
            let cotsList = (r.seccion_2 && r.seccion_2.cotizaciones) ? r.seccion_2.cotizaciones : [];
            if (cotsList.length > 0) {
                preciosHTML = cotsList.map((c, idx) => {
                    let etiqueta = cotsList.length > 1 ? `Cot #${idx + 1}: ` : '';
                    let pVal = Number(c.precio || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 });
                    return `<div style="white-space: nowrap; font-size: 0.82rem; color: #4ade80; font-weight: 600;"><span style="color: #94a3b8; font-weight: 400;">${etiqueta}</span>$${pVal}</div>`;
                }).join('');
                if (cotsList.length > 1) {
                    let totalVal = Number(r.seccion_2.precio_total || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 });
                    preciosHTML += `<div style="white-space: nowrap; font-size: 0.82rem; color: #f59e0b; font-weight: 700; border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 3px; padding-top: 2px;">Total: $${totalVal}</div>`;
                }
            } else if (r.seccion_2 && r.seccion_2.precio_total) {
                let pVal = Number(r.seccion_2.precio_total).toLocaleString('es-MX', { minimumFractionDigits: 2 });
                preciosHTML = `<div style="white-space: nowrap; font-size: 0.82rem; color: #4ade80; font-weight: 700;">$${pVal}</div>`;
            } else {
                preciosHTML = `<span style="color: #94a3b8; font-size: 0.82rem;">--</span>`;
            }

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${r.fecha_solicitud || '--'}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #38bdf8;">${fechaSalida}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #ffffff;">${unidadStr}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #38bdf8; font-weight: 600;">${r.cope || '--'}</span></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${r.ciudad || '--'}</td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #cbd5e1;">${tallerPrevio}</span></td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: right; padding: 10px 12px;">${preciosHTML}</td>
                    <td style="white-space: normal; min-width: 260px; max-width: 420px; vertical-align: middle; padding: 10px 12px; line-height: 1.5; word-break: break-word;">
                        <p style="margin: 0; padding: 0; color: #f1f5f9; font-size: 0.88rem; font-weight: 500; line-height: 1.5; white-space: normal; word-break: break-word; text-align: left;">${motivoLimpio}</p>
                    </td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">${badgeEstado}</td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">
                        <button class="btn-success" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer;" onclick="abrirDetalleRetrabajo('${ticketId}')">
                            Ver Retrabajo
                        </button>
                    </td>
                </tr>
            `;
        });
        
        if (typeof aplicarPaginacion === 'function') {
            aplicarPaginacion('tabla-retrabajos', 15, true);
        }
    } catch (err) {
        console.error('Error al cargar retrabajos:', err);
        tbody.innerHTML = '<tr><td colspan="11" style="text-align:center; padding:20px; color:#ef4444;">Error al cargar las solicitudes de retrabajo.</td></tr>';
    }
}

async function abrirDetalleRetrabajo(ticketId) {
    try {
        const res = await fetch(`/api/garantia/retrabajo/${encodeURIComponent(ticketId)}`);
        const data = await res.json();
        if (data.status !== 'success' || !data.retrabajo) {
            alert('No se pudo cargar la información de la garantía.');
            return;
        }
        
        const r = data.retrabajo;
        const s1 = r.seccion_1 || {};
        const s2 = r.seccion_2 || {};
        
        const ticketVal = r.ticket_original || r.ticket || r.id;
        const tit = document.getElementById('modal-retrabajo-titulo');
        const sub = document.getElementById('modal-retrabajo-subtitulo');
        if (tit) tit.innerText = `🛡️ Garantía / Retrabajo - Ticket: ${ticketVal}`;
        if (sub) sub.innerText = `Unidad: 8090-${r.unidad} | COPE: ${r.cope} | Supervisor: ${r.supervisor_asignado}`;
        
        const cont = document.getElementById('contenido-detalle-retrabajo');
        if (!cont) return;
        
        // Firma del Chofer si existe
        let firmaHTML = '';
        if (s1.firma_chofer && String(s1.firma_chofer).startsWith('data:image')) {
            firmaHTML = `
                <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #1f395a; text-align: center;">
                    <span style="color: #94a3b8; font-size: 0.8rem; display: block; margin-bottom: 6px;">✍️ Firma del Chofer / Operador:</span>
                    <img src="${s1.firma_chofer}" alt="Firma del Chofer" style="background: white; border-radius: 8px; max-width: 260px; max-height: 90px; border: 2px solid #1f395a; padding: 4px;">
                </div>
            `;
        }
        
        // Cotizaciones y Diagnóstico Taller (Sección 2)
        let cotizacionesHTML = '';
        const cots = s2.cotizaciones || [];
        cots.forEach((c, idx) => {
            let numCotStr = cots.length > 1 ? ` (Cotización #${idx + 1})` : '';
            
            let pdfLink = '';
            if (c.pdf_cotizacion) {
                let nombreArchivo = String(c.pdf_cotizacion);
                pdfLink = `
                    <div style="margin-top: 10px; max-width: 100%; box-sizing: border-box;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block; margin-bottom: 5px;">Documento de Cotización Adjunto:</span>
                        <a href="/static/facturas_archivos/${c.pdf_cotizacion}" target="_blank" 
                           style="display: inline-flex; align-items: flex-start; gap: 8px; max-width: 100%; background: #081422; border: 1px solid #1e3a5f; padding: 8px 14px; border-radius: 8px; color: #38bdf8; font-weight: 600; font-size: 0.85rem; text-decoration: none; box-sizing: border-box; word-break: break-all; overflow-wrap: anywhere; line-height: 1.45; transition: all 0.2s;" 
                           onmouseover="this.style.borderColor='#38bdf8'; this.style.background='#0d1e33';" 
                           onmouseout="this.style.borderColor='#1e3a5f'; this.style.background='#081422';"
                           title="${nombreArchivo}">
                            <span style="font-size: 18px; flex-shrink: 0; margin-top: 1px;">📄</span>
                            <span style="word-break: break-all; overflow-wrap: anywhere;">
                                <span style="font-weight: 700; color: #38bdf8; text-decoration: underline;">Ver Archivo</span>
                                <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 400; margin-left: 4px;">(${nombreArchivo})</span>
                            </span>
                        </a>
                    </div>
                `;
            }
            
            let evidenciasHTML = '';
            if (c.fotos_evidencia && c.fotos_evidencia.length > 0) {
                evidenciasHTML = `
                    <div style="margin-top: 10px;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block; margin-bottom: 6px;">Evidencias Adjuntas del Taller:</span>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                `;
                c.fotos_evidencia.forEach(foto => {
                    const fLow = String(foto).toLowerCase();
                    if (fLow.endsWith('.mp4') || fLow.endsWith('.mov') || fLow.endsWith('.webm')) {
                        evidenciasHTML += `
                            <a href="/static/facturas_archivos/${foto}" target="_blank" style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 85px; height: 85px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; text-decoration: none; color: #38bdf8; font-size: 11px;">
                                <span style="font-size: 24px;">🎥</span>
                                <span style="font-size: 9px; text-align: center; overflow: hidden; text-overflow: ellipsis; max-width: 75px;">Video</span>
                            </a>
                        `;
                    } else {
                        evidenciasHTML += `
                            <a href="/static/facturas_archivos/${foto}" target="_blank" style="display: block; width: 85px; height: 85px; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
                                <img src="/static/facturas_archivos/${foto}" alt="Evidencia" style="width: 100%; height: 100%; object-fit: cover;">
                            </a>
                        `;
                    }
                });
                evidenciasHTML += `</div></div>`;
            }
            
            cotizacionesHTML += `
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e3a5f; border-radius: 8px; padding: 14px; margin-top: 10px; max-width: 100%; box-sizing: border-box; overflow: hidden;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px dashed #1e3a5f; padding-bottom: 6px;">
                        <span style="color: #38bdf8; font-weight: 700; font-size: 0.95rem;">${c.titulo || 'Detalle de Reparación'}${numCotStr}</span>
                        <div style="text-align: right;">
                            <span style="color: #94a3b8; font-size: 0.72rem; display: block; font-weight: 600; text-transform: uppercase;">Precio Individual:</span>
                            <span style="background: #064e3b; color: #4ade80; border: 1px solid #22c55e; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.88rem; display: inline-block;">$${Number(c.precio || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 8px; font-size: 0.88rem;">
                        <div><strong style="color: #94a3b8;">Mantenimiento:</strong> <span style="color: #ffffff;">${c.mantenimiento || 'Correctivo'}</span></div>
                        <div><strong style="color: #94a3b8;">Diagnóstico del Mecánico:</strong> <div style="background: #09131f; padding: 8px 12px; border-radius: 6px; margin-top: 3px; color: #f1f5f9; border-left: 3px solid #38bdf8;">${c.diagnostico || 'Sin diagnóstico registrado'}</div></div>
                        <div><strong style="color: #94a3b8;">Trabajo a Realizar:</strong> <div style="background: #09131f; padding: 8px 12px; border-radius: 6px; margin-top: 3px; color: #f1f5f9; border-left: 3px solid #10b981;">${c.trabajo_realizar || 'Sin trabajo registrado'}</div></div>
                        ${c.retro ? `<div><strong style="color: #94a3b8;">Retro / Situación:</strong> <div style="background: #09131f; padding: 8px 12px; border-radius: 6px; margin-top: 3px; color: #f1f5f9; font-style: italic;">${c.retro}</div></div>` : ''}
                    </div>
                    ${pdfLink}
                    ${evidenciasHTML}
                </div>
            `;
        });
        
        cont.innerHTML = `
            <!-- BANNER DEL MOTIVO DE RETRABAJO REPORTADO POR CHOFER -->
            <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(245, 158, 11, 0.12)); border: 2px solid #f59e0b; border-radius: 12px; padding: 18px 20px; margin-bottom: 22px;">
                <div style="display: flex; align-items: center; gap: 8px; color: #f59e0b; font-weight: 800; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    <span style="font-size: 20px;">⚠️</span> MOTIVO DEL RETRABAJO / FALLA NO RESUELTA (REPORTADO POR EL CHOFER)
                </div>
                <div style="background: #0d1e33; border: 1px solid #1f395a; border-radius: 8px; padding: 14px 16px;">
                    <p style="margin: 0; color: #fef08a; font-size: 0.95rem; line-height: 1.6; word-break: break-word; white-space: pre-wrap; font-style: normal;">${String(r.motivo_chofer || 'No especificado').trim().replace(/^["'«»“”„]+|["'«»“”„]+$/g, '').trim()}</p>
                </div>
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; margin-top: 10px; font-size: 0.82rem; color: #94a3b8;">
                    <span>📅 Solicitado: <strong>${r.fecha_solicitud} ${r.hora_solicitud || ''}</strong></span>
                    <span>🏢 COPE / Edificio: <strong style="color:#38bdf8;">${r.cope}</strong></span>
                    <span>👤 Supervisor Asignado: <strong style="color:#4ade80;">${r.supervisor_asignado}</strong></span>
                </div>
            </div>

            <!-- GRID CONTENIENDO EXCLUSIVAMENTE SECCION 1 Y SECCION 2 -->
            <div style="display: flex; flex-direction: column; gap: 24px;">
                
                <!-- ■ SECCIÓN 1: REPORTE DE INCIDENCIA (CHOFER) -->
                <div style="background: #0d1e33; border: 1.5px solid #0284c7; border-radius: 12px; padding: 18px 20px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; border-bottom: 1.5px solid #0284c7; padding-bottom: 8px;">
                        <span style="color: #38bdf8; font-weight: 800; font-size: 1.05rem; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
                            <span>■</span> SECCIÓN 1: REPORTE DE INCIDENCIA ORIGINAL (CHOFER)
                        </span>
                        <span style="background: #0369a1; color: white; padding: 2px 10px; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">Ticket: ${s1.ticket || r.ticket_original}</span>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 0.88rem;">
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Unidad:</span><strong style="color: #ffffff; font-size: 1rem;">8090-${s1.unidad || r.unidad}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Marca y Modelo:</span><strong style="color: #ffffff;">${s1.marca || 'N/A'} ${s1.modelo || 'N/A'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Fecha y Hora Reporte:</span><strong style="color: #cbd5e1;">${s1.fecha || '--'} ${s1.hora ? s1.hora + ' hrs' : ''}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Kilometraje:</span><strong style="color: #cbd5e1;">${s1.kilometraje || 'No registrado'} km</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Compañía:</span><strong style="color: #10b981;">${s1.compania || 'Telnor'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Tipo Mantenimiento:</span><strong style="color: ${s1.mantenimiento === 'Preventivo' ? '#38bdf8' : '#ef4444'};">${s1.mantenimiento || 'Correctivo'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Ciudad y COPE:</span><strong style="color: #38bdf8;">${s1.ciudad || '--'} - ${s1.cope || '--'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Departamento:</span><strong style="color: #cbd5e1;">${s1.departamento || 'No especificado'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Chofer / Operador:</span><strong style="color: #ffffff;">${s1.empleado || 'No registrado'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Teléfono Celular:</span><strong style="color: #cbd5e1;">${s1.celular || 'No registrado'}</strong></div>
                        <div style="grid-column: 1 / -1;"><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Correo Electrónico:</span><strong style="color: #cbd5e1;">${s1.email || 'No registrado'}</strong></div>
                        
                        <div style="grid-column: 1 / -1; margin-top: 5px;">
                            <span style="color: #f59e0b; font-size: 0.82rem; font-weight: 700; display: block; margin-bottom: 4px;">Falla Original Reportada:</span>
                            <div style="background: #09131f; padding: 12px 14px; border-radius: 8px; color: #e2e8f0; font-style: italic; border-left: 3px solid #f59e0b;">
                                "${s1.falla_original || 'Sin detalle de falla'}"
                            </div>
                        </div>
                    </div>
                    ${firmaHTML}
                </div>

                <!-- ■ SECCIÓN 2: DIAGNÓSTICO Y COTIZACIÓN (TALLER) -->
                <div style="background: #0d1e33; border: 1.5px solid #10b981; border-radius: 12px; padding: 18px 20px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; border-bottom: 1.5px solid #10b981; padding-bottom: 8px;">
                        <span style="color: #4ade80; font-weight: 800; font-size: 1.05rem; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
                            <span>■</span> SECCIÓN 2: DIAGNÓSTICO, TRABAJO Y COTIZACIÓN (TALLER PREVIO)
                        </span>
                        <span style="background: #064e3b; color: #4ade80; padding: 2px 10px; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">Proveedor: ${s2.proveedor || 'Taller'}</span>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 0.88rem; margin-bottom: 12px;">
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Taller / Proveedor:</span><strong style="color: #ffffff; font-size: 1rem;">${s2.proveedor || 'No asignado'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Responsable en Turno:</span><strong style="color: #ffffff;">${s2.responsable || 'No registrado'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Fecha Ingreso a Taller:</span><strong style="color: #cbd5e1;">${s2.fecha_ingreso || '--'}</strong></div>
                        <div><span style="color: #94a3b8; font-size: 0.8rem; display: block;">Costo Previo Total (s/IVA):</span><strong style="color: #4ade80; font-size: 1rem;">$${Number(s2.precio_total || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</strong></div>
                    </div>

                    <!-- Cotizaciones / Trabajos de Sección 2 -->
                    ${cotizacionesHTML}
                </div>

            </div>
        `;
        
        document.getElementById('modal-detalle-retrabajo').style.display = 'flex';
        const btnReasig = document.getElementById('btn-reasignar-retrabajo');
        if (btnReasig) {
            btnReasig.setAttribute('data-ticket', ticketId);
            if (r.estado === 'Reasignado' || r.estado === 'Reasignado_Taller') {
                btnReasig.disabled = true;
                btnReasig.innerText = 'Reasignado al Taller ✓';
                btnReasig.style.opacity = '0.65';
                btnReasig.style.cursor = 'not-allowed';
            } else if (r.estado === 'Finalizado') {
                btnReasig.disabled = true;
                btnReasig.innerText = 'Retrabajo Finalizado ✓';
                btnReasig.style.opacity = '0.65';
                btnReasig.style.cursor = 'not-allowed';
            } else {
                btnReasig.disabled = false;
                btnReasig.innerText = 'Reasignar';
                btnReasig.style.opacity = '1';
                btnReasig.style.cursor = 'pointer';
            }
        }
        const btnCancelReasig = document.getElementById('btn-cancelar-reasignacion');
        if (btnCancelReasig) {
            btnCancelReasig.setAttribute('data-ticket', ticketId);
        }
    } catch (err) {
        console.error('Error al abrir detalle de retrabajo:', err);
        alert('Error al obtener los detalles de la garantía.');
    }
}
window.abrirDetalleRetrabajo = abrirDetalleRetrabajo;

window.accionReasignarRetrabajo = async function() {
    const btn = document.getElementById('btn-reasignar-retrabajo');
    const ticketId = btn ? btn.getAttribute('data-ticket') : null;
    if (!ticketId) {
        alert('No se pudo identificar el ticket a reasignar.');
        return;
    }

    const confirmar = confirm(`⚠️ ¿Confirmas la REASIGNACIÓN de garantía / retrabajo para el ticket ${ticketId}?\n\nAl confirmar, se enviará la orden de retrabajo al taller en su respectivo botón de Retrabajo y se le notificará por correo electrónico que la unidad no fue reparada de manera correcta y se sigue presentando el fallo del ticket.`);
    if (!confirmar) return;

    if (typeof window.mostrarLoaderDinamico === 'function') {
        window.mostrarLoaderDinamico("Reasignando al Taller...", `Canalizando ticket ${ticketId} y notificando por correo...`);
    } else if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Reasignando al Taller...", `Canalizando ticket ${ticketId} y notificando por correo...`);
    }

    try {
        let res = await fetch('/api/garantia/reasignar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        let data = await res.json();

        if (typeof window.ocultarLoaderDinamico === 'function') {
            window.ocultarLoaderDinamico();
        } else if (typeof ocultarLoaderDinamico === 'function') {
            ocultarLoaderDinamico();
        }

        if (data.status === 'success') {
            alert(data.message || 'Retrabajo reasignado exitosamente al taller.');
            cerrarModal('modal-detalle-retrabajo');
            if (typeof cargarRetrabajosAdmin === 'function') cargarRetrabajosAdmin();
        } else {
            alert('Error: ' + (data.message || 'No se pudo reasignar el retrabajo.'));
        }
    } catch (err) {
        if (typeof window.ocultarLoaderDinamico === 'function') {
            window.ocultarLoaderDinamico();
        } else if (typeof ocultarLoaderDinamico === 'function') {
            ocultarLoaderDinamico();
        }
        console.error('Error al reasignar retrabajo:', err);
        alert('Ocurrió un error al procesar la reasignación de garantía.');
    }
};

window.abrirModalCancelarReasignacion = function() {
    const btn = document.getElementById('btn-cancelar-reasignacion');
    const ticketId = btn ? btn.getAttribute('data-ticket') : null;
    if (!ticketId) {
        alert('No se pudo identificar el ticket a cancelar.');
        return;
    }

    let unidadTxt = '--';
    let choferTxt = '--';

    if (window.retrabajosSupervisorGlobal && Array.isArray(window.retrabajosSupervisorGlobal)) {
        let r = window.retrabajosSupervisorGlobal.find(x => String(x.ticket_original || x.ticket || x.id) === String(ticketId));
        if (r) {
            unidadTxt = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            choferTxt = (r.seccion_1 && r.seccion_1.empleado) ? r.seccion_1.empleado : (r.empleado || '--');
        }
    }

    const elTick = document.getElementById('cancelar-reasig-ticket');
    const elUni = document.getElementById('cancelar-reasig-unidad');
    const elChof = document.getElementById('cancelar-reasig-chofer');
    const txtMotivo = document.getElementById('cancelar-reasig-motivo');

    if (elTick) elTick.innerText = ticketId;
    if (elUni) elUni.innerText = unidadTxt;
    if (elChof) elChof.innerText = choferTxt;
    if (txtMotivo) txtMotivo.value = '';

    const modal = document.getElementById('modal-cancelar-reasignacion');
    if (modal) {
        modal.setAttribute('data-ticket', ticketId);
        modal.style.display = 'flex';
        if (txtMotivo) setTimeout(() => txtMotivo.focus(), 100);
    }
};

window.ejecutarCancelarReasignacion = async function() {
    const modal = document.getElementById('modal-cancelar-reasignacion');
    const ticketId = modal ? modal.getAttribute('data-ticket') : null;
    const txtMotivo = document.getElementById('cancelar-reasig-motivo');
    const motivo = txtMotivo ? txtMotivo.value.trim() : '';

    if (!ticketId) {
        alert('No se pudo identificar el ticket.');
        return;
    }

    if (!motivo) {
        alert('Por favor escribe la razón por la cual no se puede retrabajar para notificar al chofer.');
        if (txtMotivo) txtMotivo.focus();
        return;
    }

    const confirmar = confirm(`⚠️ ¿Confirmas la CANCELACIÓN de la reasignación para el ticket ${ticketId}?\n\nEl reporte de retrabajo se eliminará permanentemente del sistema y se le enviará un correo explicativo al chofer con el motivo ingresado.`);
    if (!confirmar) return;

    if (typeof window.mostrarLoaderDinamico === 'function') {
        window.mostrarLoaderDinamico("Cancelando Reasignación...", `Notificando al chofer y archivando ticket ${ticketId}...`);
    } else if (typeof mostrarLoaderDinamico === 'function') {
        mostrarLoaderDinamico("Cancelando Reasignación...", `Notificando al chofer y archivando ticket ${ticketId}...`);
    }

    try {
        let res = await fetch('/api/garantia/cancelar_reasignacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId, motivo: motivo })
        });
        let data = await res.json();

        if (typeof window.ocultarLoaderDinamico === 'function') {
            window.ocultarLoaderDinamico();
        } else if (typeof ocultarLoaderDinamico === 'function') {
            ocultarLoaderDinamico();
        }

        if (data.status === 'success') {
            alert(data.message || 'La reasignación ha sido cancelada y el reporte eliminado.');
            cerrarModal('modal-cancelar-reasignacion');
            cerrarModal('modal-detalle-retrabajo');
            if (typeof cargarRetrabajosAdmin === 'function') cargarRetrabajosAdmin();
        } else {
            alert('Error: ' + (data.message || 'No se pudo cancelar la reasignación.'));
        }
    } catch (err) {
        if (typeof window.ocultarLoaderDinamico === 'function') {
            window.ocultarLoaderDinamico();
        } else if (typeof ocultarLoaderDinamico === 'function') {
            ocultarLoaderDinamico();
        }
        console.error('Error al cancelar reasignación:', err);
        alert('Ocurrió un error al procesar la cancelación de la reasignación.');
    }
};

window.cargarRetrabajosProveedor = async function() {
    const tbody = document.getElementById('tabla-retrabajos-prov');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px; color:#94a3b8;">Cargando órdenes de retrabajo...</td></tr>';

    try {
        const res = await fetch('/api/garantia/proveedor/lista');
        const data = await res.json();
        const retrabajos = data.retrabajos || [];

        const badgeProv = document.getElementById('badge-retrabajo-prov');
        if (badgeProv) {
            if (retrabajos.length > 0) {
                badgeProv.innerText = retrabajos.length;
                badgeProv.style.display = 'inline-block';
            } else {
                badgeProv.style.display = 'none';
            }
        }

        if (retrabajos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:25px; color:#94a3b8;">No tienes órdenes de retrabajo o garantía pendientes de atender.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        retrabajos.forEach(r => {
            let ticketId = r.ticket_original || r.ticket || r.id;
            let unidadStr = r.unidad ? (r.unidad.startsWith('8090-') ? r.unidad : `8090-${r.unidad}`) : '--';
            let fechaReasig = r.fecha_reasignacion || r.fecha_solicitud || '--';
            let motivoLimpio = String(r.motivo_chofer || 'Falla no solventada en reparación previa').trim().replace(/^["'«»“”„]+|["'«»“”„]+$/g, '').trim();
            let supervisor = r.supervisor_reasigno || r.supervisor_asignado || 'Supervisión Vehicular';

            let badgeEstado = `<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:0.82rem; display:inline-block; white-space:nowrap;">Retrabajo</span>`;

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #38bdf8;">${fechaReasig}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #ffffff;">${unidadStr}</strong></td>
                    <td style="white-space: normal; min-width: 260px; max-width: 420px; vertical-align: middle; padding: 10px 12px; line-height: 1.5; word-break: break-word;">
                        <p style="margin: 0; padding: 0; color: #f1f5f9; font-size: 0.88rem; font-weight: 500; line-height: 1.5; white-space: normal; word-break: break-word; text-align: left;">${motivoLimpio}</p>
                    </td>
                    <td style="white-space: nowrap; vertical-align: middle;"><span style="color: #cbd5e1;">${supervisor}</span></td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">${badgeEstado}</td>
                    <td style="white-space: nowrap; vertical-align: middle; text-align: center;">
                        <div style="display: flex; gap: 6px; justify-content: center; align-items: center; flex-wrap: wrap;">
                            <button class="btn-info" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #0284c7; color: white; border: none;" onclick="abrirDetallesTicketRetrabajo('${ticketId}', '${r.factura_id || ''}')">
                                Ver Detalles
                            </button>
                            <button class="btn-success" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #10b981; color: white; border: none;" onclick="abrirDetalleRetrabajo('${ticketId}')">
                                Ver Retrabajo
                            </button>
                            <button class="btn-primary" style="padding: 6px 12px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; white-space: nowrap; cursor: pointer; background: #16a34a; color: white; border: none;" onclick="marcarRetrabajoFinalizado('${ticketId}')">
                                Retrabajo Finalizado
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error('Error al cargar retrabajos del proveedor:', err);
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:25px; color:#ef4444;">Error al cargar las órdenes de retrabajo.</td></tr>';
    }
};

window.abrirDetallesTicketRetrabajo = function(ticketId, facturaId) {
    let fId = facturaId;
    if (!fId && typeof facturasGlobal !== 'undefined') {
        let found = facturasGlobal.find(x => String(x.id) === String(ticketId) || String(x.id_reporte) === String(ticketId) || String(x.retro).includes(ticketId));
        if (found) fId = found.id;
    }
    if (fId && typeof abrirDetalles === 'function') {
        abrirDetalles(fId);
    } else if (typeof abrirReporteProv === 'function') {
        abrirReporteProv(ticketId);
    } else if (typeof abrirDetalles === 'function') {
        abrirDetalles(ticketId);
    } else {
        abrirDetalleRetrabajo(ticketId);
    }
};

window.marcarRetrabajoFinalizado = async function(ticketId) {
    if (!ticketId) {
        alert('Ticket no identificado.');
        return;
    }

    const confirmar = confirm(`⚠️ ¿Confirmas que los trabajos de retrabajo / garantía para el ticket ${ticketId} han sido FINALIZADOS por el taller?\n\nAl confirmar, la orden de retrabajo concluirá y se desbloquearán las acciones del ticket.`);
    if (!confirmar) return;

    try {
        let res = await fetch('/api/garantia/taller/finalizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        let data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Retrabajo finalizado con éxito.');
            if (typeof cargarRetrabajosProveedor === 'function') {
                cargarRetrabajosProveedor();
            }
            if (typeof cargarFacturas === 'function') {
                cargarFacturas();
            }
        } else {
            alert('Error: ' + (data.message || 'No se pudo finalizar el retrabajo.'));
        }
    } catch (err) {
        console.error('Error al finalizar retrabajo:', err);
        alert('Ocurrió un error al marcar el retrabajo como finalizado.');
    }
};


if (typeof window.escapeHtml !== 'function') {
    window.escapeHtml = function(text) {
        if (!text) return '';
        var d = document.createElement('div');
        d.innerText = text;
        return d.innerHTML;
    };
}

window.cargarTiempoGarantiaJefatura = async function() {
    const tbody = document.getElementById('tabla-tiempo-garantia');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#94a3b8;">Cargando tiempos de garantía de talleres...</td></tr>';

    try {
        const res = await fetch('/api/garantia/talleres_tiempo');
        const data = await res.json();
        const talleres = data.talleres || [];
        window.talleresTiempoGarantiaGlobal = talleres;

        if (talleres.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:25px; color:#94a3b8;">No se encontraron talleres registrados.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        talleres.forEach(t => {
            const logoImg = t.foto_ruta ? `<img src="${t.foto_ruta}" class="mini-profile-pic" onerror="this.src='https://via.placeholder.com/40/112641/40916c?text=T'">` : `<div class="mini-profile-pic" style="display:flex;align-items:center;justify-content:center;background:#112641;color:#10b981;font-weight:bold;">T</div>`;

            const ciudadCope = t.ciudad ? `${t.ciudad} <br><small style="color:#f59e0b;">${t.cope || ''}</small>` : 'No especificada';
            const contacto = `${t.telefono || 'N/A'}<br><small style="color:#94a3b8;">${t.correo || 'N/A'}</small>`;

            tbody.innerHTML += `
                <tr>
                    <td style="text-align:center;">${logoImg}</td>
                    <td><strong>${escapeHtml(t.nombre_proveedor)}</strong><br><small style="color:#64748b;">${escapeHtml(t.usuario)}</small></td>
                    <td>${escapeHtml(t.encargado)}</td>
                    <td>${contacto}</td>
                    <td><span style="color:#0ea5e9; font-weight:bold;">${ciudadCope}</span></td>
                    <td>
                        <span style="background: rgba(16, 185, 129, 0.18); border: 1px solid #10b981; color: #34d399; font-weight: 700; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 5px;">
                            ⏱️ ${t.tiempo_formateado}
                        </span>
                    </td>
                    <td><span style="color:#94a3b8; font-size:0.78rem;">${t.fecha_actualizacion || 'Predefinido (30 días)'}</span></td>
                    <td>
                        <button class="btn-success" style="background-color: #0284c7; padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px;" onclick="abrirModalAjustarGarantiaJefatura('${t.usuario}', '${escapeHtml(t.nombre_proveedor).replace(/'/g, "\\'")}', ${t.dias_garantia}, ${t.horas_garantia}, ${t.minutos_garantia}, ${t.segundos_garantia})">
                            ⚙️ Ajustar Tiempo
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error('Error al cargar tiempos de garantía de talleres:', err);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#ef4444;">Error al cargar la información de garantías.</td></tr>';
    }
};

window.abrirModalAjustarGarantiaJefatura = function(usuario, nombre, d, h, m, s) {
    if (document.getElementById('ajuste-taller-usuario')) document.getElementById('ajuste-taller-usuario').value = usuario;
    if (document.getElementById('ajuste-taller-nombre')) document.getElementById('ajuste-taller-nombre').innerText = nombre;
    if (document.getElementById('ajuste-taller-dias')) document.getElementById('ajuste-taller-dias').value = d !== undefined ? d : 30;
    if (document.getElementById('ajuste-taller-horas')) document.getElementById('ajuste-taller-horas').value = h !== undefined ? h : 0;
    if (document.getElementById('ajuste-taller-minutos')) document.getElementById('ajuste-taller-minutos').value = m !== undefined ? m : 0;
    if (document.getElementById('ajuste-taller-segundos')) document.getElementById('ajuste-taller-segundos').value = s !== undefined ? s : 0;
    actualizarPreviewAjusteJefatura();
    const modal = document.getElementById('modal-ajustar-garantia-jefatura');
    if (modal) modal.style.display = 'flex';
};

window.actualizarPreviewAjusteJefatura = function() {
    const d = parseInt(document.getElementById('ajuste-taller-dias')?.value || 0) || 0;
    const h = parseInt(document.getElementById('ajuste-taller-horas')?.value || 0) || 0;
    const m = parseInt(document.getElementById('ajuste-taller-minutos')?.value || 0) || 0;
    const s = parseInt(document.getElementById('ajuste-taller-segundos')?.value || 0) || 0;

    const tot = d * 86400 + h * 3600 + m * 60 + s;
    const el = document.getElementById('ajuste-taller-preview');
    if (!el) return;

    if (tot <= 0) {
        el.innerText = '⚠️ Tiempo total: 0 seg (Inválido - mínimo debe ser mayor a 0)';
        el.style.color = '#f87171';
        el.style.borderColor = '#ef4444';
        return;
    }

    el.style.color = '#34d399';
    el.style.borderColor = '#10b981';
    let partes = [];
    if (d > 0) partes.push(d === 1 ? '1 día' : `${d} días`);
    if (h > 0) partes.push(h === 1 ? '1 hora' : `${h} horas`);
    if (m > 0) partes.push(m === 1 ? '1 min' : `${m} mins`);
    if (s > 0) partes.push(`${s} seg`);

    el.innerText = `Tiempo total configurado: ${partes.join(', ')}`;
};

window.setValoresGarantiaJefatura = function(d, h, m, s) {
    if (document.getElementById('ajuste-taller-dias')) document.getElementById('ajuste-taller-dias').value = d;
    if (document.getElementById('ajuste-taller-horas')) document.getElementById('ajuste-taller-horas').value = h;
    if (document.getElementById('ajuste-taller-minutos')) document.getElementById('ajuste-taller-minutos').value = m;
    if (document.getElementById('ajuste-taller-segundos')) document.getElementById('ajuste-taller-segundos').value = s;
    actualizarPreviewAjusteJefatura();
};

window.guardarAjusteGarantiaJefatura = async function() {
    const usuario = document.getElementById('ajuste-taller-usuario')?.value;
    const d = parseInt(document.getElementById('ajuste-taller-dias')?.value || 0) || 0;
    const h = parseInt(document.getElementById('ajuste-taller-horas')?.value || 0) || 0;
    const m = parseInt(document.getElementById('ajuste-taller-minutos')?.value || 0) || 0;
    const s = parseInt(document.getElementById('ajuste-taller-segundos')?.value || 0) || 0;

    const tot = d * 86400 + h * 3600 + m * 60 + s;
    if (tot <= 0) {
        alert("El tiempo de garantía debe ser mayor a 0 segundos.");
        return;
    }

    try {
        const res = await fetch('/api/garantia/taller/actualizar_dias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario: usuario,
                dias_garantia: d,
                horas_garantia: h,
                minutos_garantia: m,
                segundos_garantia: s
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Tiempo de garantía actualizado con éxito.');
            cerrarModal('modal-ajustar-garantia-jefatura');
            cargarTiempoGarantiaJefatura();
        } else {
            alert('Error: ' + (data.message || 'No se pudo actualizar'));
        }
    } catch (err) {
        console.error('Error al guardar ajuste de garantía:', err);
        alert('No se pudo conectar con el servidor.');
    }
};


function abrirModalDetalles(identificador) {
    const user = pendientesGlobal.find(u => u.correo === identificador || u.num_empleado === identificador);
    if (!user) return;

    let isProv = user.rol === 'proveedores';
    let nombrePrincipal = isProv ? user.nombre_proveedor : `${user.nombres} ${user.apellido_paterno} ${user.apellido_materno || ''}`;
    let rolLabel = isProv ? 'TALLER / PROVEEDOR' : `EMPLEADO: ${user.rol.toUpperCase()} ${user.subrol ? '(' + user.subrol + ')' : ''}`;
    let borderRadius = isProv ? '15px' : '50%';
    let ciudadCopeTexto = user.ciudad ? `${user.ciudad} / ${user.cope || 'N/A'}` : 'No especificada';

    let html = `
        <style>
            .hover-zoom:hover { transform: scale(1.05); cursor: pointer; }
            .info-card-modern {
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #0ea5e9;
                transition: background 0.2s;
            }
            .info-card-modern:hover { background: rgba(255,255,255,0.1); }
            .info-label { font-size: 0.8em; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
            .info-value { color: #f1f5f9; font-size: 1.05em; word-wrap: break-word; }
        </style>
        
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; padding: 25px 20px; border-radius: 10px; text-align: center; margin-bottom: 25px; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <a href="/static/registros_confirmar/${user.foto_ruta}" target="_blank" title="Haz clic para ver la imagen en tamaño completo">
                <img src="/static/registros_confirmar/${user.foto_ruta}" 
                     style="width: 140px; height: 140px; object-fit: contain; border-radius: ${borderRadius}; border: 3px solid #40916c; box-shadow: 0 8px 20px rgba(0,0,0,0.4); background: white; transition: transform 0.3s;"
                     class="hover-zoom"
                     onerror="this.src='https://via.placeholder.com/150/112641/40916c?text=Logo/Foto'">
            </a>
            <h3 style="color: #f8fafc; margin-top: 15px; font-size: 1.4em; font-weight: 600; letter-spacing: 0.5px;">${nombrePrincipal}</h3>
            <div style="margin-top: 10px;">
                <span style="background: rgba(14, 165, 233, 0.2); padding: 6px 15px; border-radius: 20px; color: #38bdf8; font-size: 0.85em; font-weight: bold; border: 1px solid rgba(14, 165, 233, 0.3);">${rolLabel}</span>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: left; margin-bottom: 20px;">
    `;

    if (isProv) {
        html += `
            <div class="info-card-modern"><div class="info-label">👤 Encargado Principal</div><div class="info-value">${user.encargado}</div></div>
            <div class="info-card-modern"><div class="info-label">🤝 Resp. en Turno</div><div class="info-value">${user.responsable || 'N/A'}</div></div>
            <div class="info-card-modern"><div class="info-label">📞 Teléfono</div><div class="info-value">${user.telefono}</div></div>
            <div class="info-card-modern"><div class="info-label">📧 Correo</div><div class="info-value">${user.correo}</div></div>
            <div class="info-card-modern" style="grid-column: span 2;"><div class="info-label">📍 Dirección Completa</div><div class="info-value">${user.direccion} <span style="color:#94a3b8; font-size:0.9em;">(C.P. ${user.codigo_postal || 'N/A'})</span></div></div>
            <div class="info-card-modern" style="grid-column: span 2; border-left-color: #40916c;"><div class="info-label">🏢 Giro / Descripción</div><div class="info-value" style="font-size: 0.95em; line-height: 1.5; color: #cbd5e1;">${user.descripcion || 'Sin descripción'}</div></div>
        `;
    } else {
        html += `
            <div class="info-card-modern"><div class="info-label">🆔 Num. Empleado</div><div class="info-value">${user.num_empleado}</div></div>
            <div class="info-card-modern"><div class="info-label">💼 Área</div><div class="info-value">${user.area}</div></div>
            <div class="info-card-modern"><div class="info-label">📍 Ubicación Base / COPE</div><div class="info-value" style="color:#38bdf8; font-weight:bold;">${ciudadCopeTexto}</div></div>
            <div class="info-card-modern"><div class="info-label">📧 Correo Alertas</div><div class="info-value">${user.correo || 'N/A'}</div></div>
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

    let mensaje = '¿Aceptar usuario y generar credenciales?';
    if (confirm(mensaje)) {
        fetch(`/api/${accion}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ identificador: identificador })
        }).then(res => res.json()).then(data => { alert(data.message); cerrarModal('modal-detalles'); cargarPendientes(); });
    }
}

function abrirModalDetallesUsuario(usuarioId) {
    const user = (usuariosGlobal || []).find(u => u.usuario === usuarioId);
    if (!user) return;

    const dp = user.datos_perfil || {};
    const rol = user.rol;
    const isProv = rol === 'proveedores';
    const isCorp = rol === 'corporativos';
    const isAdmin = rol === 'administracion';

    const carpeta = isProv ? 'logos_proveedores' : (isAdmin ? 'foto_administracion' : 'foto_corporativos');
    const fotoSrc = dp.foto_ruta ? `/static/${carpeta}/${dp.foto_ruta}` : 'https://via.placeholder.com/150/112641/40916c?text=Foto';

    let ciudadCopeTexto = dp.ciudad ? (dp.cope ? `${dp.ciudad} / ${dp.cope}` : dp.ciudad) : 'No especificada';

    let headerIcon = '👤';
    let headerIconBg = 'rgba(64, 145, 108, 0.2)';
    let headerIconColor = '#40916c';
    let headerIconBorder = 'rgba(64, 145, 108, 0.4)';
    let headerTitle = 'Perfil de Usuario del Sistema';
    let headerSubtitle = 'Portal Automotriz';
    let borderColorPhoto = '#40916c';
    let photoBg = '#081422';
    let photoFit = 'cover';
    let photoPadding = '0';
    let statusBadgeText = 'Usuario Activo';
    let statusBadgeBg = 'rgba(16, 185, 129, 0.15)';
    let statusBadgeColor = '#34d399';
    let statusBadgeBorder = 'rgba(16, 185, 129, 0.3)';
    let statusDotColor = '#10b981';
    let photoTooltip = 'Clic en foto para ampliar';
    let nivelAccesoBadge = `<span style="background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; display: inline-block;">${dp.subrol || 'Administración'}</span>`;

    if (isProv) {
        headerIcon = '🏢';
        headerIconBg = 'rgba(16, 185, 129, 0.2)';
        headerIconColor = '#10b981';
        headerIconBorder = 'rgba(16, 185, 129, 0.4)';
        headerTitle = 'Perfil de Taller Autorizado';
        headerSubtitle = 'Portal Proveedores';
        borderColorPhoto = '#10b981';
        photoBg = '#ffffff';
        photoFit = 'contain';
        photoPadding = '6px';
        statusBadgeText = 'Proveedor Verificado';
        statusBadgeBg = 'rgba(16, 185, 129, 0.15)';
        statusBadgeColor = '#34d399';
        statusBadgeBorder = 'rgba(16, 185, 129, 0.3)';
        statusDotColor = '#10b981';
        photoTooltip = 'Clic en logo para ampliar';
        nivelAccesoBadge = `<span style="background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; display: inline-block;">Proveedor</span>`;
    } else if (isCorp) {
        headerIcon = '🏛️';
        headerIconBg = 'rgba(168, 85, 247, 0.2)';
        headerIconColor = '#a855f7';
        headerIconBorder = 'rgba(168, 85, 247, 0.4)';
        headerTitle = 'Perfil de Dirección Corporativa';
        headerSubtitle = 'Portal Ejecutivo';
        borderColorPhoto = '#a855f7';
        photoBg = '#081422';
        photoFit = 'cover';
        photoPadding = '0';
        statusBadgeText = 'Acceso Ejecutivo';
        statusBadgeBg = 'rgba(139, 92, 246, 0.15)';
        statusBadgeColor = '#c084fc';
        statusBadgeBorder = 'rgba(139, 92, 246, 0.3)';
        statusDotColor = '#a855f7';
        photoTooltip = 'Clic en foto para ampliar';
        nivelAccesoBadge = `<span style="background: rgba(139, 92, 246, 0.18); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.4); padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; display: inline-block;">Corporativo</span>`;
    }

    let seccion1HTML = '';
    if (isProv) {
        seccion1HTML = `
            <div style="background: #0d1e33; border: 1px solid #1f395a; border-radius: 10px; padding: 14px 18px;">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>🏢</span> DATOS DE LA EMPRESA Y CONTACTO
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Razón Social / Empresa:</span>
                        <strong style="color: #ffffff; font-size: 1.05rem;">${dp.nombre_proveedor || 'Sin razón social'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Encargado Principal:</span>
                        <strong style="color: #ffffff;">${dp.encargado || 'N/A'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Resp. en Turno:</span>
                        <strong style="color: #ffffff;">${dp.responsable || 'N/A'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Ciudad Base:</span>
                        <strong style="color: #38bdf8;">${dp.ciudad || 'No especificada'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Teléfono:</span>
                        <strong style="color: #ffffff;">${dp.telefono || 'N/A'}</strong>
                    </div>
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Correo Electrónico:</span>
                        <strong style="color: #e2e8f0;">${dp.correo || 'N/A'}</strong>
                    </div>
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Dirección del Taller:</span>
                        <span style="color: #cbd5e1; font-size: 0.85rem;">${dp.direccion || 'No registrada'} (C.P. ${dp.codigo_postal || 'N/A'})</span>
                    </div>
                    ${dp.descripcion ? `
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Descripción:</span>
                        <span style="color: #94a3b8; font-style: italic; font-size: 0.85rem;">${dp.descripcion}</span>
                    </div>` : ''}
                </div>
            </div>
        `;
    } else if (isCorp) {
        seccion1HTML = `
            <div style="background: #0d1e33; border: 1px solid #1f395a; border-radius: 10px; padding: 14px 18px;">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>👔</span> INFORMACIÓN DEL DIRECTIVO
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Nombre Completo:</span>
                        <strong style="color: #ffffff; font-size: 1.05rem;">${dp.nombres || ''} ${dp.apellido_paterno || ''} ${dp.apellido_materno || ''}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">No. de Empleado:</span>
                        <strong style="color: #ffffff;">${dp.num_empleado || 'N/A'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Ciudad Base:</span>
                        <strong style="color: #38bdf8;">${dp.ciudad || 'No especificada'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Área Asignada:</span>
                        <strong style="color: #ffffff;">${dp.area || 'N/A'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Correo Electrónico:</span>
                        <strong style="color: #e2e8f0;">${dp.correo || 'No registrado'}</strong>
                    </div>
                </div>
            </div>
        `;
    } else {
        seccion1HTML = `
            <div style="background: #0d1e33; border: 1px solid #1f395a; border-radius: 10px; padding: 14px 18px;">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <span>📋</span> INFORMACIÓN DEL EMPLEADO
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Nombre Completo:</span>
                        <strong style="color: #ffffff;">${dp.nombres || ''} ${dp.apellido_paterno || ''} ${dp.apellido_materno || ''}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">No. de Empleado:</span>
                        <strong style="color: #ffffff;">${dp.num_empleado || 'N/A'}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Ciudad Base:</span>
                        <strong style="color: #38bdf8;">${ciudadCopeTexto}</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Área Asignada:</span>
                        <strong style="color: #ffffff;">${dp.area || 'N/A'}</strong>
                    </div>
                    <div style="grid-column: span 2;">
                        <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Correo Electrónico:</span>
                        <strong style="color: #e2e8f0;">${dp.correo || 'No registrado'}</strong>
                    </div>
                </div>
            </div>
        `;
    }

    const opcionesFecha = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    const fechaHoy = new Date().toLocaleDateString('es-MX', opcionesFecha);

    const modalHTML = `
        <button class="btn-close-modal" onclick="cerrarModal('modal-detalles-usuario')" style="color: #94a3b8; font-size: 24px; top: 15px; right: 20px;">×</button>
        
        <!-- Header del Modal -->
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 22px; border-bottom: 1px solid #1f395a; padding-bottom: 16px;">
            <div style="width: 44px; height: 44px; border-radius: 10px; background: ${headerIconBg}; color: ${headerIconColor}; display: flex; align-items: center; justify-content: center; font-size: 22px; border: 1px solid ${headerIconBorder};">
                ${headerIcon}
            </div>
            <div>
                <h3 style="color: #ffffff; margin: 0; font-size: 1.3rem; font-weight: 700;">${headerTitle}</h3>
                <p style="color: #94a3b8; margin: 3px 0 0 0; font-size: 0.85rem;">${headerSubtitle}</p>
            </div>
        </div>

        <!-- Cuerpo del Perfil -->
        <div style="display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap;">
            
            <!-- Columna Izquierda: Foto y Estado -->
            <div style="display: flex; flex-direction: column; align-items: center; min-width: 170px;">
                <div style="width: 150px; height: 150px; border-radius: 14px; border: 3px solid ${borderColorPhoto}; box-shadow: 0 8px 24px rgba(0,0,0,0.5); overflow: hidden; background: ${photoBg}; padding: ${photoPadding}; display: flex; align-items: center; justify-content: center; position: relative;">
                    <img src="${fotoSrc}"
                        style="width: 100%; height: 100%; object-fit: ${photoFit}; cursor: pointer; transition: transform 0.3s;" onclick="abrirLightbox(this.src)" title="${photoTooltip}" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'" onerror="this.src='https://via.placeholder.com/150/112641/40916c?text=Foto'">
                </div>
                <div style="margin-top: 12px; display: inline-flex; align-items: center; gap: 6px; background: ${statusBadgeBg}; color: ${statusBadgeColor}; font-size: 0.82rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; border: 1px solid ${statusBadgeBorder};">
                    <span style="display: inline-block; width: 8px; height: 8px; background: ${statusDotColor}; border-radius: 50%;"></span>
                    ${statusBadgeText}
                </div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 6px;">${photoTooltip}</div>
            </div>

            <!-- Columna Derecha: Tarjetas de Información -->
            <div style="flex: 1; min-width: 280px; display: flex; flex-direction: column; gap: 14px;">
                ${seccion1HTML}

                <!-- Sección 2: Credenciales y Nivel de Acceso -->
                <div style="background: #0d1e33; border: 1px solid #1f395a; border-radius: 10px; padding: 14px 18px;">
                    <div style="font-size: 0.8rem; text-transform: uppercase; color: ${headerIconColor}; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <span>🔐</span> CREDENCIALES DEL SISTEMA
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem; align-items: center;">
                        <div>
                            <span style="color: #94a3b8; font-size: 0.8rem; display: block;">Usuario del Sistema:</span>
                            <code style="background: rgba(255,255,255,0.08); padding: 3px 8px; border-radius: 4px; color: #e2e8f0; font-size: 0.85rem;">${user.usuario}</code>
                        </div>
                        <div>
                            <span style="color: #94a3b8; font-size: 0.8rem; display: block; margin-bottom: 2px;">Nivel de Acceso:</span>
                            ${nivelAccesoBadge}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Meta / Timestamp -->
        <div style="margin-top: 18px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.8rem; color: #64748b; display: flex; justify-content: flex-end; align-items: center; flex-wrap: wrap; gap: 8px;">
            <span>Fecha de consulta: <strong style="color: #94a3b8;">${fechaHoy}</strong></span>
        </div>

        <!-- Acciones del Modal -->
        <div class="modal-actions" style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 12px;">
            <button class="btn-danger" onclick="cerrarModal('modal-detalles-usuario')" style="max-width: 140px; padding: 10px 18px;">Cerrar</button>
            <button class="btn-success-modal" onclick="descargarPDFDetallesUsuario('${user.usuario}')" style="padding: 10px 22px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-weight: 600; cursor: pointer;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Confirmar y Descargar PDF
            </button>
        </div>
    `;

    const contenedor = document.getElementById('modal-detalles-usuario-box');
    if (contenedor) {
        contenedor.innerHTML = modalHTML;
    }
    const modalEl = document.getElementById('modal-detalles-usuario');
    if (modalEl) {
        modalEl.style.display = 'flex';
    }
}

function descargarPDFDetallesUsuario(usuarioId) {
    const user = (usuariosGlobal || []).find(u => u.usuario === usuarioId);
    if (!user) return;

    const dp = user.datos_perfil || {};
    const rol = user.rol;
    const isProv = rol === 'proveedores';
    const isCorp = rol === 'corporativos';
    const carpeta = isProv ? 'logos_proveedores' : (rol === 'administracion' ? 'foto_administracion' : 'foto_corporativos');
    const fotoSrc = dp.foto_ruta ? `/static/${carpeta}/${dp.foto_ruta}` : 'https://via.placeholder.com/150/ffffff/000000?text=Foto';

    let subTituloDoc = isProv ? 'EXPEDIENTE DE USUARIO - PROVEEDOR' : (isCorp ? 'EXPEDIENTE DE USUARIO - DIRECCIÓN CORPORATIVA' : 'EXPEDIENTE DE USUARIO - AUTOMOTRIZ');
    let nivelAccesoColor = isProv ? '#10b981' : (isCorp ? '#8b5cf6' : '#f59e0b');
    let nivelAccesoTexto = isProv ? 'Proveedor' : (isCorp ? 'Corporativo' : (dp.subrol || 'Administración'));
    let ciudadCopeTexto = dp.ciudad ? (dp.cope ? `${dp.ciudad} / ${dp.cope}` : dp.ciudad) : 'No especificada';

    let detallesDocHTML = '';
    if (isProv) {
        detallesDocHTML = `
            <div class="pdf-section-title">■ DATOS DE LA EMPRESA</div>
            <div class="pdf-line"><strong>Razón Social:</strong> ${dp.nombre_proveedor || 'N/A'}</div>
            <div class="pdf-line"><strong>Descripción:</strong> <span class="texto-largo">${dp.descripcion || 'Sin descripción'}</span></div>
            <div class="pdf-line"><strong>Usuario Sistema:</strong> ${user.usuario}</div>
            <br>
            <div class="pdf-section-title">■ INFORMACIÓN DE CONTACTO</div>
            <div class="pdf-line"><strong>Encargado Principal:</strong> ${dp.encargado || 'N/A'}</div>
            <div class="pdf-line"><strong>Resp. en Turno:</strong> ${dp.responsable || 'N/A'}</div>
            <div class="pdf-line"><strong>Ciudad Base:</strong> <span style="color:#0284c7; font-weight:bold;">${dp.ciudad || 'No especificada'}</span></div>
            <div class="pdf-line"><strong>Teléfono:</strong> ${dp.telefono || 'N/A'}</div>
            <div class="pdf-line"><strong>Correo:</strong> ${dp.correo || 'N/A'}</div>
            <div class="pdf-line"><strong>Dirección:</strong> <span class="texto-largo">${dp.direccion || 'N/A'} (C.P. ${dp.codigo_postal || 'N/A'})</span></div>
            <br>
            <div class="pdf-section-title">■ CREDENCIALES DEL SISTEMA</div>
            <div class="pdf-line"><strong>Usuario Asignado:</strong> ${user.usuario}</div>
            <div class="pdf-line"><strong>Nivel de Acceso:</strong> <span style="color:${nivelAccesoColor}; font-weight:bold;">${nivelAccesoTexto}</span></div>
        `;
    } else {
        detallesDocHTML = `
            <div class="pdf-section-title">■ INFORMACIÓN DEL EMPLEADO</div>
            <div class="pdf-line"><strong>Nombre Completo:</strong> ${dp.nombres || ''} ${dp.apellido_paterno || ''} ${dp.apellido_materno || ''}</div>
            <div class="pdf-line"><strong>No. de Empleado:</strong> ${dp.num_empleado || 'N/A'}</div>
            <div class="pdf-line"><strong>Ciudad Base:</strong> <span style="color:#0284c7; font-weight:bold;">${ciudadCopeTexto}</span></div>
            <div class="pdf-line"><strong>Área Asignada:</strong> ${dp.area || 'N/A'}</div>
            <div class="pdf-line"><strong>Correo Electrónico:</strong> ${dp.correo || 'No registrado'}</div>
            <br>
            <div class="pdf-section-title">■ CREDENCIALES DEL SISTEMA</div>
            <div class="pdf-line"><strong>Usuario Asignado:</strong> ${user.usuario}</div>
            <div class="pdf-line"><strong>Nivel de Acceso:</strong> <span style="color:${nivelAccesoColor}; font-weight:bold;">${nivelAccesoTexto}</span></div>
        `;
    }

    const opcionesFecha = { year: 'numeric', month: 'long', day: 'numeric' };
    const fechaTexto = new Date().toLocaleDateString('es-MX', opcionesFecha);

    const docCompleto = `
        <div class="pdf-sheet">
            <div class="pdf-header-doc">
                <h2>EXPEDIENTE DE USUARIO</h2>
                <p>${subTituloDoc}</p>
            </div>
            <div class="pdf-body">
                <img src="${fotoSrc}" class="pdf-photo-doc" style="object-fit:${isProv ? 'contain' : 'cover'}; ${isProv ? 'background:#fff; padding:4px;' : ''}" onerror="this.src='https://via.placeholder.com/150/ffffff/000000?text=Foto'">
                <div class="pdf-details">
                    ${detallesDocHTML}
                </div>
            </div>
            <div class="pdf-footer">Documento extraído de la Base de Datos Central el: ${fechaTexto}</div>
        </div>
    `;

    const nuevaPestana = window.open('', '_blank');
    if (!nuevaPestana) {
        alert('Por favor, permite ventanas emergentes en tu navegador para ver el expediente en una pestaña nueva.');
        return;
    }

    nuevaPestana.document.open();
    nuevaPestana.document.write(`<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expediente de Usuario</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\/script>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 0;
            background: #0f172a;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .toolbar {
            position: sticky;
            top: 0;
            width: 100%;
            background: #112641;
            border-bottom: 1px solid #1f395a;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            z-index: 1000;
        }
        .toolbar-title {
            color: #ffffff;
            font-size: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .toolbar-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn-tool {
            padding: 9px 18px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: none;
            transition: all 0.2s;
            font-family: inherit;
        }
        .btn-print { background: #0284c7; color: #ffffff; }
        .btn-print:hover { background: #0369a1; }
        .btn-download { background: #2d6a4f; color: #ffffff; }
        .btn-download:hover { background: #1b4332; }
        .btn-close { background: #475569; color: #ffffff; }
        .btn-close:hover { background: #334155; }
        .document-wrapper {
            padding: 35px 20px 50px;
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .pdf-sheet {
            background: #ffffff;
            color: #000000;
            width: 100%;
            max-width: 800px;
            padding: 45px 50px;
            border-radius: 6px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
            font-family: Arial, sans-serif;
            position: relative;
        }
        .pdf-header-doc {
            text-align: center;
            border-bottom: 2px solid #112641;
            padding-bottom: 16px;
            margin-bottom: 25px;
        }
        .pdf-header-doc h2 {
            margin: 0;
            font-size: 22px;
            color: #112641;
            font-family: 'Times New Roman', serif;
            letter-spacing: 0.5px;
        }
        .pdf-header-doc p {
            margin: 6px 0 0 0;
            font-size: 13px;
            color: #475569;
            font-style: italic;
            font-weight: bold;
        }
        .pdf-body {
            display: flex;
            gap: 25px;
            margin-bottom: 25px;
            align-items: flex-start;
        }
        .pdf-photo-doc {
            width: 130px;
            height: 130px;
            object-fit: cover;
            border: 2px solid #112641;
            border-radius: 4px;
        }
        .pdf-details { flex: 1; }
        .pdf-section-title {
            background: #f1f5f9;
            padding: 7px 12px;
            font-weight: bold;
            margin-bottom: 12px;
            border-left: 4px solid #112641;
            font-size: 13.5px;
            color: #112641;
        }
        .pdf-line {
            margin-bottom: 8px;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
        }
        .pdf-line strong {
            font-weight: 700;
            color: #0f172a;
        }
        .pdf-footer {
            border-top: 1px solid #cbd5e1;
            padding-top: 15px;
            text-align: center;
            font-size: 11px;
            color: #64748b;
            margin-top: 35px;
        }
        @media print {
            .no-print { display: none !important; }
            body { background: #ffffff !important; padding: 0 !important; }
            .document-wrapper { padding: 0 !important; }
            .pdf-sheet {
                box-shadow: none !important;
                max-width: 100% !important;
                padding: 10mm 15mm !important;
            }
            @page {
                size: letter portrait;
                margin: 10mm;
            }
        }
    </style>
</head>
<body>
    <div class="toolbar no-print">
        <div class="toolbar-title">
            <span>📄</span> Expediente Oficial de Usuario
        </div>
        <div class="toolbar-actions">
            <button class="btn-tool btn-print" onclick="window.print()">
                🖨️ Imprimir / Guardar como PDF
            </button>
            <button class="btn-tool btn-download" onclick="descargarComoPDF()">
                📥 Descargar PDF (.pdf)
            </button>
            <button class="btn-tool btn-close" onclick="window.close()">
                ✖️ Cerrar
            </button>
        </div>
    </div>
    
    <div class="document-wrapper">
        <div id="documento-impresion">
            ${docCompleto}
        </div>
    </div>

    <script>
        function descargarComoPDF() {
            const element = document.getElementById('documento-impresion');
            const opt = {
                margin: [10, 10, 10, 10],
                filename: 'Perfil_Usuario.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true, logging: false },
                jsPDF: { unit: 'mm', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        }
    <\/script>
</body>
</html>`);
    nuevaPestana.document.close();
}

function descargarPDFUsuario() {
    // Mantener como compatibilidad si se llamaba en algún otro contexto
    descargarPDF();
}

function cargarListaUsuarios(rolBuscado, idTabla) {
    fetch('/api/accesos').then(res => res.json()).then(data => {
        usuariosGlobal = data.usuarios || [];
        const tbody = document.getElementById(idTabla);
        tbody.innerHTML = '';

        let filtrados = usuariosGlobal.filter(u => u.rol === rolBuscado && u.datos_perfil);

        let subrolActualElement = document.getElementById('subrol-actual');
        let ciudadActualElement = document.getElementById('ciudad-actual');
        let subrolActual = subrolActualElement ? subrolActualElement.value : '';
        let miCiudad = ciudadActualElement ? ciudadActualElement.value : '';

        if (filtrados.length === 0) { tbody.innerHTML = `<tr><td colspan="12" style="text-align:center;">No hay usuarios en esta sección</td></tr>`; return; }

        filtrados.forEach(u => {
            const dp = u.datos_perfil;
            const carpeta = (rolBuscado === 'proveedores') ? 'logos_proveedores' : ((rolBuscado === 'administracion') ? 'foto_administracion' : 'foto_corporativos');
            const img = `<img src="/static/${carpeta}/${dp.foto_ruta}" class="mini-profile-pic" onerror="this.src='https://via.placeholder.com/40/112641/40916c?text=X'">`;

            const ciudad = dp.ciudad ? `${dp.ciudad} <br><small style="color:#f59e0b;">${dp.cope || ''}</small>` : 'No especificada';

            const btnAcciones = `
                <div class="acciones-td" style="flex-direction: column;">
                    <button class="btn-info" style="background-color: #0284c7; margin-bottom: 5px; width: 100%; font-weight: 600;" onclick="abrirModalDetallesUsuario('${u.usuario}')">Ver Detalles</button>
                    <div style="display:flex; gap:5px; width:100%;">
                        <button class="btn-success" onclick="abrirModalEditar('${u.usuario}')" style="flex:1; background-color: #10b981;">Editar</button>
                        ${subrolActual !== 'Supervisor' ? `<button class="btn-danger-sm" onclick="eliminarUsuario('${u.usuario}', '${rolBuscado}')" style="flex:1;">Eliminar</button>` : ''}
                    </div>
                </div>`;

            if (rolBuscado === 'proveedores') {
                tbody.innerHTML += `<tr><td>${img}</td><td><strong>${dp.nombre_proveedor}</strong></td><td style="color:#40916c">${u.usuario}</td><td>${dp.encargado}</td><td>${dp.responsable || 'N/A'}</td><td>${dp.telefono}</td><td>${dp.correo}</td><td>${dp.direccion}</td><td>${dp.codigo_postal}</td><td><div style="min-width: 400px; width: 400px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4;">${dp.descripcion}</div></td><td>${btnAcciones}</td></tr>`;
            } else if (rolBuscado === 'administracion') {
                let subrolText = dp.subrol ? `<span style="color:#f59e0b; font-weight:bold;">${dp.subrol}</span>` : '<span style="color:#ef4444; font-weight:bold;">N/A</span>';
                tbody.innerHTML += `<tr><td>${img}</td><td><strong>${dp.nombres} ${dp.apellido_paterno} ${dp.apellido_materno || ''}</strong><br><small style="color:#a3b1c6;">${dp.correo || ''}</small></td><td style="color:#40916c">${u.usuario}</td><td>${dp.num_empleado}</td><td><span style="color:#0ea5e9; font-weight:bold;">${ciudad}</span></td><td>${dp.area || 'N/A'}</td><td>${subrolText}</td><td>${btnAcciones}</td></tr>`;
            } else {
                let areaYRol = dp.subrol ? `${dp.area} <br><small style="color:#f59e0b; font-weight:bold;">[${dp.subrol}]</small>` : (dp.area || 'N/A');
                tbody.innerHTML += `<tr><td>${img}</td><td><strong>${dp.nombres} ${dp.apellido_paterno} ${dp.apellido_materno || ''}</strong><br><small style="color:#a3b1c6;">${dp.correo || ''}</small></td><td style="color:#40916c">${u.usuario}</td><td>${dp.num_empleado}</td><td><span style="color:#0ea5e9; font-weight:bold;">${ciudad}</span></td><td>${areaYRol}</td><td>${btnAcciones}</td></tr>`;
            }
        });
    });
}

function eliminarUsuario(usuarioId, rol) {
    if (confirm(`⚠️ ATENCIÓN ⚠️\n¿Eliminar COMPLETAMENTE a este usuario? Esta acción no se puede deshacer.`)) {
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
        camposHtml += `<div class="input-group full-width"><label>Nombre(s)</label><input type="text" name="nombres" value="${dp.nombres}" required></div><div class="input-group"><label>Apellido Paterno</label><input type="text" name="apellido_paterno" value="${dp.apellido_paterno}" required></div><div class="input-group"><label>Apellido Materno</label><input type="text" name="apellido_materno" value="${dp.apellido_materno || ''}"></div>${htmlCiudadCope}<div class="input-group"><label>Núm. Empleado</label><input type="text" name="num_empleado" value="${dp.num_empleado}" required></div><div class="input-group"><label>Área</label><input type="text" name="area" value="${dp.area}" required></div><div class="input-group"><label>Correo Alertas</label><input type="email" name="correo" value="${dp.correo || ''}" required></div><div class="input-group"><label>Puesto</label><select name="subrol" class="input-form" required><option value="Jefatura" ${dp.subrol === 'Jefatura' ? 'selected' : ''}>Jefatura</option><option value="Supervisor" ${dp.subrol === 'Supervisor' ? 'selected' : ''}>Supervisor</option><option value="Administrador" ${dp.subrol === 'Administrador' ? 'selected' : ''}>Administrador</option></select></div>`;
    } else if (user.rol === 'corporativos') {
        camposHtml += `<div class="input-group full-width"><label>Nombre(s)</label><input type="text" name="nombres" value="${dp.nombres}" required></div><div class="input-group"><label>Apellido Paterno</label><input type="text" name="apellido_paterno" value="${dp.apellido_paterno}" required></div><div class="input-group"><label>Apellido Materno</label><input type="text" name="apellido_materno" value="${dp.apellido_materno || ''}"></div>${htmlCiudadCope}<div class="input-group"><label>Núm. Empleado</label><input type="text" name="num_empleado" value="${dp.num_empleado}" required></div><div class="input-group"><label>Área</label><input type="text" name="area" value="${dp.area}" required></div><div class="input-group full-width"><label>Correo Electrónico</label><input type="email" name="correo" value="${dp.correo || ''}" required></div>`;
    }

    document.getElementById('edit-campos-dinamicos').innerHTML = camposHtml;
    if (document.getElementById('edit-ciudad')) {
        actualizarCopeSelect('edit-ciudad', 'edit-cope', dp.cope);
    }
    guardarEstadoInicialEdicion();
    document.getElementById('modal-editar').style.display = 'flex';
}

function guardarEstadoInicialEdicion() {
    const form = document.getElementById('form-editar');
    if (!form) return;
    const inputs = form.querySelectorAll('input:not([type="file"]):not([type="hidden"]), select, textarea');
    const estado = {};
    inputs.forEach(el => {
        const clave = el.name || el.id;
        if (clave) {
            estado[clave] = (el.value || '').trim();
        }
    });
    window.estadoInicialEdicionUsuario = estado;
}

function procesarEdicion() {
    const fotoInput = document.getElementById('edit-foto');
    const tieneNuevaFoto = Boolean(fotoInput && fotoInput.files && fotoInput.files.length > 0);

    const form = document.getElementById('form-editar');
    const inputs = form ? form.querySelectorAll('input:not([type="file"]):not([type="hidden"]), select, textarea') : [];
    let huboCambios = tieneNuevaFoto;

    if (!huboCambios && window.estadoInicialEdicionUsuario) {
        for (const el of inputs) {
            const clave = el.name || el.id;
            if (!clave) continue;
            const valActual = (el.value || '').trim();
            const valInicial = window.estadoInicialEdicionUsuario[clave] !== undefined ? window.estadoInicialEdicionUsuario[clave] : '';
            if (valActual !== valInicial) {
                huboCambios = true;
                break;
            }
        }
    }

    if (!huboCambios) {
        alert("No se ha modificado ningún dato.");
        return;
    }

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

                let rolTexto = user.rol;
                if (user.rol === 'administracion' && user.datos_perfil.subrol) {
                    rolTexto = `Administración (${user.datos_perfil.subrol})`;
                }

                let rolYNombre = `<span style="text-transform: capitalize; font-weight:bold; color:#0284c7;">${rolTexto}</span><br><small style="color:#a3b1c6;">${nombreCompleto}</small>`;

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
    const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
    const fechaTexto = new Date().toLocaleDateString('es-MX', opciones);
    
    const dateSpan = document.getElementById('pdf-fecha');
    const displaySpan = document.getElementById('perfil-fecha-display');
    if (dateSpan) dateSpan.innerText = fechaTexto;
    if (displaySpan) displaySpan.innerText = fechaTexto;
    
    const modal = document.getElementById('modal-mi-perfil');
    if (modal) modal.style.display = 'flex';
}

function descargarPDF() {
    const elemento = document.getElementById('pdf-content');
    if (!elemento) return;
    
    // Abrir una nueva pestaña para visualizar y descargar el documento oficial
    const nuevaPestana = window.open('', '_blank');
    if (!nuevaPestana) {
        alert('Por favor, permite ventanas emergentes en tu navegador para ver el expediente en una pestaña nueva.');
        return;
    }
    
    const opcionesFecha = { year: 'numeric', month: 'long', day: 'numeric' };
    const fechaTexto = new Date().toLocaleDateString('es-MX', opcionesFecha);
    
    const dateSpan = elemento.querySelector('#pdf-fecha');
    if (dateSpan) dateSpan.innerText = fechaTexto;

    const contenidoHTML = elemento.innerHTML;
    
    nuevaPestana.document.open();
    nuevaPestana.document.write(`<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expediente de Usuario</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\/script>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 0;
            background: #0f172a;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .toolbar {
            position: sticky;
            top: 0;
            width: 100%;
            background: #112641;
            border-bottom: 1px solid #1f395a;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            z-index: 1000;
        }
        .toolbar-title {
            color: #ffffff;
            font-size: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .toolbar-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn-tool {
            padding: 9px 18px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: none;
            transition: all 0.2s;
            font-family: inherit;
        }
        .btn-print {
            background: #0284c7;
            color: #ffffff;
        }
        .btn-print:hover { background: #0369a1; }
        .btn-download {
            background: #2d6a4f;
            color: #ffffff;
        }
        .btn-download:hover { background: #1b4332; }
        .btn-close {
            background: #475569;
            color: #ffffff;
        }
        .btn-close:hover { background: #334155; }
        .document-wrapper {
            padding: 35px 20px 50px;
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .pdf-sheet {
            background: #ffffff;
            color: #000000;
            width: 100%;
            max-width: 800px;
            padding: 45px 50px;
            border-radius: 6px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
            font-family: Arial, sans-serif;
            position: relative;
        }
        .pdf-header-doc {
            text-align: center;
            border-bottom: 2px solid #112641;
            padding-bottom: 16px;
            margin-bottom: 25px;
        }
        .pdf-header-doc h2 {
            margin: 0;
            font-size: 22px;
            color: #112641;
            font-family: 'Times New Roman', serif;
            letter-spacing: 0.5px;
        }
        .pdf-header-doc p {
            margin: 6px 0 0 0;
            font-size: 13px;
            color: #475569;
            font-style: italic;
            font-weight: bold;
        }
        .pdf-body {
            display: flex;
            gap: 25px;
            margin-bottom: 25px;
            align-items: flex-start;
        }
        .pdf-photo-doc {
            width: 130px;
            height: 130px;
            object-fit: cover;
            border: 2px solid #112641;
            border-radius: 4px;
        }
        .pdf-details {
            flex: 1;
        }
        .pdf-section-title {
            background: #f1f5f9;
            padding: 7px 12px;
            font-weight: bold;
            margin-bottom: 12px;
            border-left: 4px solid #112641;
            font-size: 13.5px;
            color: #112641;
        }
        .pdf-line {
            margin-bottom: 8px;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
        }
        .pdf-line strong {
            font-weight: 700;
            color: #0f172a;
        }
        .pdf-footer {
            border-top: 1px solid #cbd5e1;
            padding-top: 15px;
            text-align: center;
            font-size: 11px;
            color: #64748b;
            margin-top: 35px;
        }
        @media print {
            .no-print { display: none !important; }
            body { background: #ffffff !important; padding: 0 !important; }
            .document-wrapper { padding: 0 !important; }
            .pdf-sheet {
                box-shadow: none !important;
                max-width: 100% !important;
                padding: 10mm 15mm !important;
            }
            @page {
                size: letter portrait;
                margin: 10mm;
            }
        }
    </style>
</head>
<body>
    <div class="toolbar no-print">
        <div class="toolbar-title">
            <span>📄</span> Expediente Oficial de Usuario
        </div>
        <div class="toolbar-actions">
            <button class="btn-tool btn-print" onclick="window.print()">
                🖨️ Imprimir / Guardar como PDF
            </button>
            <button class="btn-tool btn-download" onclick="descargarComoPDF()">
                📥 Descargar PDF (.pdf)
            </button>
            <button class="btn-tool btn-close" onclick="window.close()">
                ✖️ Cerrar
            </button>
        </div>
    </div>
    
    <div class="document-wrapper">
        <div id="documento-para-descargar" class="pdf-sheet">
            ${contenidoHTML}
        </div>
    </div>

    <script>
        function descargarComoPDF() {
            const elem = document.getElementById('documento-para-descargar');
            const opt = {
                margin: 0.4,
                filename: 'Perfil_Usuario.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(elem).save();
        }
    <\/script>
</body>
</html>`);
    nuevaPestana.document.close();
}

// --- INICIALIZACION ROBUSTA ESPERANDO A QUE CARGUEN TODOS LOS SCRIPTS ---
window.addEventListener('load', function() {
    let rolActual = document.getElementById('rol-actual') ? document.getElementById('rol-actual').value : '';
    let subrolActual = document.getElementById('subrol-actual') ? document.getElementById('subrol-actual').value.trim() : '';

    if (rolActual === 'administracion' || subrolActual !== '' || document.getElementById('vista-pendientes') || document.getElementById('vista-cotizaciones-10k')) { 
        let savedView = localStorage.getItem('activeViewAdmin');
        if (savedView) {
            if (savedView === 'cotizaciones-10k') {
                if (typeof verCotizacionesMas10000 === 'function') {
                    verCotizacionesMas10000();
                } else {
                    cambiarVistaAdmin('cotizaciones-10k');
                }
            } else {
                cambiarVistaAdmin(savedView);
            }
        } else {
            if (subrolActual === 'Jefatura') {
                cambiarVistaAdmin('pendientes');
            } else if (subrolActual === 'Supervisor') {
                cambiarVistaAdmin('reportes');
            } else if (subrolActual === 'Administrador') {
                if (typeof verCotizacionesMas10000 === 'function') {
                    verCotizacionesMas10000();
                } else {
                    cambiarVistaAdmin('cotizaciones-10k');
                }
            } else {
                cambiarVistaAdmin('reportes'); 
            }
        }
    }
    if (document.getElementById('vista-reportes-prov')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }
    }
    if (document.getElementById('vista-cotizaciones-corp')) { 
        let savedView = localStorage.getItem('activeViewCorp');
        cambiarVistaCorp(savedView ? savedView : 'cotizaciones'); 
    }
});
// --- EFECTO DE SELECCION GLOBAL PARA FILAS DE TABLA ---
document.addEventListener('click', function (e) {
    let tr = e.target.closest('tbody tr');
    if (!tr) return;
    let tbody = tr.closest('tbody');
    if (!tbody) return;
    let rows = tbody.querySelectorAll('tr');
    rows.forEach(r => r.classList.remove('selected-row'));
    tr.classList.add('selected-row');
});

// --- MARCADOR ACTIVO EN MENU LATERAL ---
document.addEventListener('click', function (e) {
    let btn = e.target.closest('.btn-sidebar');
    if (!btn) return;
    let nav = btn.closest('.nav-menu') || btn.closest('.sidebar');
    if (!nav) return;
    let buttons = nav.querySelectorAll('.btn-sidebar');
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
});


// ==========================================
// GESTION DE TIEMPO / GARANTIA POR TALLER (JEFATURA Y PROVEEDORES)
// ==========================================

function formatTiempoTexto(dias, horas, minutos, segundos) {
    let partes = [];
    if (dias > 0) partes.push(`${dias} día${dias !== 1 ? 's' : ''}`);
    if (horas > 0) partes.push(`${horas} hora${horas !== 1 ? 's' : ''}`);
    if (minutos > 0) partes.push(`${minutos} minuto${minutos !== 1 ? 's' : ''}`);
    if (segundos > 0 || partes.length === 0) partes.push(`${segundos} segundo${segundos !== 1 ? 's' : ''}`);
    return partes.join(', ');
}

async function cargarTiempoGarantiaJefatura() {
    const tbody = document.getElementById('tabla-tiempo-garantia');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#94a3b8;">Cargando tiempos de garantía de talleres...</td></tr>';

    try {
        const res = await fetch('/api/garantia/talleres_tiempo');
        const data = await res.json();
        if (data.status !== 'success' || !data.talleres || data.talleres.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#94a3b8;">No hay talleres registrados.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        data.talleres.forEach(t => {
            const tr = document.createElement('tr');
            
            let fotoSrc = '';
            if (t.foto_ruta) {
                fotoSrc = (t.foto_ruta.startsWith('/') || t.foto_ruta.startsWith('http')) 
                    ? t.foto_ruta 
                    : '/static/logos_proveedores/' + t.foto_ruta;
            }

            const logoHtml = fotoSrc 
                ? `<img src="${fotoSrc}" alt="Logo" style="width:36px; height:36px; border-radius:8px; object-fit:cover; border:1px solid #1f395a;" onerror="this.onerror=null; this.parentElement.innerHTML='<div style=\'width:36px; height:36px; border-radius:8px; background:#1e293b; display:flex; align-items:center; justify-content:center; font-size:1.1rem; border:1px solid #334155;\'>🔧</div>';">`
                : `<div style="width:36px; height:36px; border-radius:8px; background:#1e293b; display:flex; align-items:center; justify-content:center; font-size:1.1rem; border:1px solid #334155;">🔧</div>`;

            const textoTiempoPill = t.tiempo_formateado || (t.dias_garantia + ' días');
            const badgeGarantia = `<span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; font-weight: 700; padding: 4px 12px; border-radius: 9999px; font-size: 0.88rem; display: inline-flex; align-items: center; gap: 5px;">⏱️ ${textoTiempoPill}</span>`;

            const estadoHtml = t.garantia_configurada
                ? `<span style="color: #34d399; font-size: 0.82rem; font-weight: 600;">✅ Notificado por taller</span><br><small style="color: #64748b; font-size: 0.75rem;">${t.fecha_actualizacion || ''}</small>`
                : `<span style="color: #f59e0b; font-size: 0.82rem; font-weight: 600;">⏳ Base por defecto</span><br><small style="color: #64748b; font-size: 0.75rem;">30 días estándar</small>`;

            const escapedUsuario = (t.usuario || '').replace(/'/g, "\'");
            const escapedNombre = (t.nombre_proveedor || '').replace(/'/g, "\'");

            const diasVal = t.dias_garantia !== undefined ? t.dias_garantia : 30;
            const horasVal = t.horas_garantia || 0;
            const minsVal = t.minutos_garantia || 0;
            const segsVal = t.segundos_garantia || 0;

            tr.innerHTML = `
                <td style="text-align:center;">${logoHtml}</td>
                <td><strong>${t.nombre_proveedor}</strong><br><small style="color:#94a3b8;">Usuario: ${t.usuario}</small></td>
                <td>${t.encargado || 'N/A'}</td>
                <td><div>📞 ${t.telefono || 'N/A'}</div><small style="color:#94a3b8;">✉️ ${t.correo || 'N/A'}</small></td>
                <td>${t.ciudad || 'N/A'} / ${t.cope || 'N/A'}</td>
                <td style="text-align:center;">${badgeGarantia}</td>
                <td>${estadoHtml}</td>
                <td style="text-align:center;">
                    <button type="button" class="btn-primary" style="padding: 6px 12px; font-size: 0.82rem; background: #0284c7; border: none; border-radius: 6px; color: white; cursor: pointer; font-weight: 700; display: inline-flex; align-items: center; gap: 5px;" onclick="abrirModalAjustarGarantiaJefatura('${escapedUsuario}', '${escapedNombre}', ${diasVal}, ${horasVal}, ${minsVal}, ${segsVal})">
                        ⚙️ Ajustar Tiempo
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error al cargar tiempos de garantía:', err);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#ef4444;">Error al cargar la información de garantías.</td></tr>';
    }
}
window.cargarTiempoGarantiaJefatura = cargarTiempoGarantiaJefatura;

function setValoresGarantiaJefatura(d, h, m, s) {
    if (document.getElementById('ajuste-taller-dias')) document.getElementById('ajuste-taller-dias').value = d;
    if (document.getElementById('ajuste-taller-horas')) document.getElementById('ajuste-taller-horas').value = h;
    if (document.getElementById('ajuste-taller-minutos')) document.getElementById('ajuste-taller-minutos').value = m;
    if (document.getElementById('ajuste-taller-segundos')) document.getElementById('ajuste-taller-segundos').value = s;
    actualizarPreviewAjusteJefatura();
}
window.setValoresGarantiaJefatura = setValoresGarantiaJefatura;

function actualizarPreviewAjusteJefatura() {
    const d = parseInt(document.getElementById('ajuste-taller-dias')?.value || 0, 10) || 0;
    const h = parseInt(document.getElementById('ajuste-taller-horas')?.value || 0, 10) || 0;
    const m = parseInt(document.getElementById('ajuste-taller-minutos')?.value || 0, 10) || 0;
    const s = parseInt(document.getElementById('ajuste-taller-segundos')?.value || 0, 10) || 0;
    
    const prev = document.getElementById('ajuste-taller-preview');
    if (prev) {
        const texto = formatTiempoTexto(d, h, m, s);
        prev.innerHTML = `<strong>Tiempo total:</strong> ${texto}`;
    }
}
window.actualizarPreviewAjusteJefatura = actualizarPreviewAjusteJefatura;

function abrirModalAjustarGarantiaJefatura(usuario, nombre, dias, horas, minutos, segundos) {
    const modal = document.getElementById('modal-ajustar-garantia-jefatura');
    if (!modal) return;
    document.getElementById('ajuste-taller-usuario').value = usuario;
    document.getElementById('ajuste-taller-nombre').textContent = nombre;
    document.getElementById('ajuste-taller-dias').value = dias !== undefined ? dias : 30;
    document.getElementById('ajuste-taller-horas').value = horas || 0;
    document.getElementById('ajuste-taller-minutos').value = minutos || 0;
    document.getElementById('ajuste-taller-segundos').value = segundos || 0;
    actualizarPreviewAjusteJefatura();
    modal.style.display = 'flex';
}
window.abrirModalAjustarGarantiaJefatura = abrirModalAjustarGarantiaJefatura;

async function guardarAjusteGarantiaJefatura() {
    const usuario = document.getElementById('ajuste-taller-usuario').value;
    const nombre = document.getElementById('ajuste-taller-nombre').textContent || 'Taller';
    const dias = parseInt(document.getElementById('ajuste-taller-dias').value || 0, 10) || 0;
    const horas = parseInt(document.getElementById('ajuste-taller-horas').value || 0, 10) || 0;
    const minutos = parseInt(document.getElementById('ajuste-taller-minutos').value || 0, 10) || 0;
    const segundos = parseInt(document.getElementById('ajuste-taller-segundos').value || 0, 10) || 0;

    if (!usuario) {
        alert('Taller no identificado.');
        return;
    }

    const totalSegundos = dias * 86400 + horas * 3600 + minutos * 60 + segundos;
    if (totalSegundos <= 0) {
        alert('Por favor ingrese un tiempo de garantía mayor a 0 segundos.');
        return;
    }
    if (dias > 365) {
        alert('El tiempo de garantía no puede exceder 365 días.');
        return;
    }

    const tiempoTexto = formatTiempoTexto(dias, horas, minutos, segundos);

    // CONFIRMACION ANTES DE GUARDAR
    const confirmado = confirm(`¿Estás seguro de que deseas guardar y aplicar este tiempo de garantía para "${nombre}"?

Tiempo asignado: ${tiempoTexto}`);
    if (!confirmado) {
        return;
    }

    try {
        const res = await fetch('/api/garantia/taller/actualizar_dias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                usuario: usuario, 
                dias_garantia: dias,
                horas_garantia: horas,
                minutos_garantia: minutos,
                segundos_garantia: segundos
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Tiempo de garantía actualizado exitosamente.');
            cerrarModal('modal-ajustar-garantia-jefatura');
            cargarTiempoGarantiaJefatura();
        } else {
            alert('Error: ' + (data.message || 'No se pudo actualizar el tiempo de garantía.'));
        }
    } catch (err) {
        console.error('Error al guardar ajuste de garantía:', err);
        alert('Ocurrió un error al guardar el ajuste de garantía.');
    }
}
window.guardarAjusteGarantiaJefatura = guardarAjusteGarantiaJefatura;

// ==========================================
// MODAL TIEMPO / GARANTIA DEL TALLER (PROVEEDORES)
// ==========================================
function setValoresGarantiaProv(d, h, m, s) {
    if (document.getElementById('input-dias-garantia-prov')) document.getElementById('input-dias-garantia-prov').value = d;
    if (document.getElementById('input-horas-garantia-prov')) document.getElementById('input-horas-garantia-prov').value = h;
    if (document.getElementById('input-minutos-garantia-prov')) document.getElementById('input-minutos-garantia-prov').value = m;
    if (document.getElementById('input-segundos-garantia-prov')) document.getElementById('input-segundos-garantia-prov').value = s;
    actualizarPreviewGarantiaProv();
}
window.setValoresGarantiaProv = setValoresGarantiaProv;

function actualizarPreviewGarantiaProv() {
    const d = parseInt(document.getElementById('input-dias-garantia-prov')?.value || 0, 10) || 0;
    const h = parseInt(document.getElementById('input-horas-garantia-prov')?.value || 0, 10) || 0;
    const m = parseInt(document.getElementById('input-minutos-garantia-prov')?.value || 0, 10) || 0;
    const s = parseInt(document.getElementById('input-segundos-garantia-prov')?.value || 0, 10) || 0;
    
    const prev = document.getElementById('preview-garantia-prov');
    if (prev) {
        const texto = formatTiempoTexto(d, h, m, s);
        prev.innerHTML = `<strong>Tiempo ofrecido:</strong> ${texto}`;
    }
}
window.actualizarPreviewGarantiaProv = actualizarPreviewGarantiaProv;

function abrirModalGarantiaProveedor() {
    const modal = document.getElementById('modal-garantia-proveedor');
    if (modal) {
        actualizarPreviewGarantiaProv();
        modal.style.display = 'flex';
    }
}
window.abrirModalGarantiaProveedor = abrirModalGarantiaProveedor;

async function guardarGarantiaProveedor() {
    const dias = parseInt(document.getElementById('input-dias-garantia-prov')?.value || 0, 10) || 0;
    const horas = parseInt(document.getElementById('input-horas-garantia-prov')?.value || 0, 10) || 0;
    const minutos = parseInt(document.getElementById('input-minutos-garantia-prov')?.value || 0, 10) || 0;
    const segundos = parseInt(document.getElementById('input-segundos-garantia-prov')?.value || 0, 10) || 0;

    const totalSegundos = dias * 86400 + horas * 3600 + minutos * 60 + segundos;
    if (totalSegundos <= 0) {
        alert('Por favor ingresa un tiempo de garantía mayor a 0 segundos.');
        return;
    }
    if (dias > 365) {
        alert('El tiempo de garantía no puede exceder 365 días.');
        return;
    }

    const tiempoTexto = formatTiempoTexto(dias, horas, minutos, segundos);

    // CONFIRMACION ANTES DE GUARDAR
    const confirmado = confirm(`¿Estás seguro de que deseas notificar a Jefatura este tiempo de garantía?

Tiempo total ofrecido: ${tiempoTexto}`);
    if (!confirmado) {
        return;
    }

    const btn = document.getElementById('btn-guardar-garantia-prov');
    const txtOriginal = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '⏳ Guardando...';
    }

    try {
        const res = await fetch('/api/proveedor/actualizar_garantia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                dias_garantia: dias,
                horas_garantia: horas,
                minutos_garantia: minutos,
                segundos_garantia: segundos
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Tiempo de garantía notificado a Jefatura con éxito.');
            cerrarModal('modal-garantia-proveedor');
        } else {
            alert('Error: ' + (data.message || 'No se pudo guardar la garantía.'));
        }
    } catch (err) {
        console.error('Error al guardar garantía:', err);
        alert('Ocurrió un error al notificar el tiempo de garantía.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = txtOriginal;
        }
    }
}
window.guardarGarantiaProveedor = guardarGarantiaProveedor;

// ==========================================
// FILTRADO INTERACTIVO DE RUTAS EN DIAGRAMA DE FLUJO
// ==========================================
function filtrarRutaFlujo(tipo) {
    const tabs = document.querySelectorAll('.btn-flujo-tab');
    tabs.forEach(t => {
        t.classList.remove('active');
        t.style.background = 'transparent';
    });

    const activeBtn = document.getElementById('btn-flujo-' + tipo);
    if (activeBtn) {
        activeBtn.classList.add('active');
        if (tipo === 'todos') activeBtn.style.background = 'rgba(56, 189, 248, 0.2)';
        if (tipo === 'menor10k') activeBtn.style.background = 'rgba(16, 185, 129, 0.2)';
        if (tipo === 'mayor10k') activeBtn.style.background = 'rgba(245, 158, 11, 0.2)';
        if (tipo === 'garantia') activeBtn.style.background = 'rgba(168, 85, 247, 0.2)';
    }

    const steps = document.querySelectorAll('.flujo-step-box');
    const connectors = document.querySelectorAll('.flujo-flecha-conector, .flujo-arrow-v, .flujo-connector, .flujo-connector-garantia');

    if (tipo === 'todos') {
        steps.forEach(s => {
            s.style.display = 'block';
            s.style.opacity = '1';
        });
        connectors.forEach(c => c.style.opacity = '1');
        const rMenor = document.querySelector('.flujo-rama-menor10k');
        const rMayor = document.querySelector('.flujo-rama-mayor10k');
        if (rMenor) rMenor.style.opacity = '1';
        if (rMayor) rMayor.style.opacity = '1';
        return;
    }

    steps.forEach(s => {
        if (s.classList.contains('flujo-step-' + tipo)) {
            s.style.display = 'block';
            s.style.opacity = '1';
        } else {
            s.style.opacity = '0.2';
        }
    });

    // Enfoque en bifurcacion paso 4
    const rMenor = document.querySelector('.flujo-rama-menor10k');
    const rMayor = document.querySelector('.flujo-rama-mayor10k');
    if (rMenor && rMayor) {
        if (tipo === 'menor10k') {
            rMenor.style.opacity = '1';
            rMayor.style.opacity = '0.15';
            const f4 = document.getElementById('etapa-4-bifurcacion');
            if (f4) f4.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else if (tipo === 'mayor10k') {
            rMayor.style.opacity = '1';
            rMenor.style.opacity = '0.15';
            const f4 = document.getElementById('etapa-4-bifurcacion');
            if (f4) f4.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            rMenor.style.opacity = '1';
            rMayor.style.opacity = '1';
        }
    }

    if (tipo === 'garantia') {
        const fGarantia = document.getElementById('etapa-11-garantia');
        if (fGarantia) fGarantia.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
window.filtrarRutaFlujo = filtrarRutaFlujo;

// =========================================================
// FUNCIÓN PARA DESCARGAR DIAGRAMA DE FLUJO EN FORMATO PDF
// SIN CORTES LATERALES Y PAGINADO NATURAL POR PARTES
// =========================================================

// =========================================================
// ENFOCAR PASO DEL DIAGRAMA CON SCROLL SUAVE Y RESALTE
// =========================================================
function enfocarPasoFlujo(idEtapa, ev) {
    if (ev) ev.preventDefault();
    const el = document.getElementById(idEtapa);
    if (!el) return;

    // Si la etapa está oculta por un filtro de pestañas, restablecer a 'todos'
    if (el.style.display === 'none') {
        if (typeof filtrarRutaFlujo === 'function') {
            filtrarRutaFlujo('todos');
        }
    }

    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.add('flujo-step-highlight');
    setTimeout(() => {
        el.classList.remove('flujo-step-highlight');
    }, 1800);
}

function descargarDiagramaFlujo() {
    // 1. Confirmación obligatoria al usuario
    if (!confirm("¿Deseas generar y descargar el Diagrama de Flujo de Trabajo en formato PDF (1 hoja compacta)?")) {
        return;
    }

    // 2. Asegurar que todas las etapas del diagrama estén visibles antes de exportar
    if (typeof filtrarRutaFlujo === 'function') {
        filtrarRutaFlujo('todos');
    }

    const contenedorOriginal = document.querySelector('.flujo-contenedor-principal');
    if (!contenedorOriginal) {
        alert("No se encontró el contenedor del diagrama de flujo.");
        return;
    }

    const btn = document.getElementById('btn-descargar-flujo');
    const textoOriginal = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">⏳</span><span>Generando 1 hoja...</span>';
        btn.disabled = true;
        btn.style.opacity = '0.7';
    }

    // 3. Ocultar temporalmente los botones del mapa de navegación de etapas
    const mapaEtapas = contenedorOriginal.querySelector('.mapa-etapas-contenedor');
    const estadoMapa = mapaEtapas ? mapaEtapas.style.display : '';
    if (mapaEtapas) {
        mapaEtapas.style.display = 'none';
    }

    // 4. Activar modo compacto temporal (oculta descripciones largas <p> para una sola hoja compacta)
    contenedorOriginal.classList.add('flujo-modo-pdf-compacto');

    // 5. Insertar encabezado institucional sin nombres exclusivos de empresas
    const headerPdf = document.createElement('div');
    headerPdf.id = 'flujo-pdf-temp-header';
    headerPdf.style.textAlign = 'center';
    headerPdf.style.padding = '8px 10px 16px 10px';
    headerPdf.style.marginBottom = '18px';
    headerPdf.style.borderBottom = '2px solid #1f395a';
    headerPdf.innerHTML = `
        <div style="font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
            SISTEMA INTEGRAL DE FLOTA AUTOMOTRIZ • DIAGRAMA DE FLUJO DE TRABAJO
        </div>
        <div style="font-size: 0.86rem; color: #94a3b8; margin-top: 4px;">
            Procedimiento Operativo Oficial de Gestión y Liquidación de Tickets de Servicio
        </div>
        <div style="font-size: 0.74rem; color: #38bdf8; margin-top: 4px; font-weight: 700;">
            Fecha de emisión: ${new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </div>
    `;
    contenedorOriginal.insertBefore(headerPdf, contenedorOriginal.firstChild);

    // 6. Insertar pie de página institucional sin nombres exclusivos de empresas
    const footerPdf = document.createElement('div');
    footerPdf.id = 'flujo-pdf-temp-footer';
    footerPdf.style.textAlign = 'center';
    footerPdf.style.padding = '14px 10px 8px 10px';
    footerPdf.style.marginTop = '20px';
    footerPdf.style.borderTop = '1px solid #1f395a';
    footerPdf.innerHTML = `
        <div style="font-size: 0.72rem; color: #64748b; font-weight: 700;">
            Documento de control interno institucional • Flujo completo de autorización, reparación, fiscalización y garantía automotriz
        </div>
    `;
    contenedorOriginal.appendChild(footerPdf);

    // Recordar posición previa de scroll y desplazar a la parte superior para calibrar el lienzo
    const scrollPrevio = window.scrollY;
    window.scrollTo(0, 0);

    const fechaHoy = new Date().toISOString().slice(0, 10);
    const nombreArchivo = `Diagrama_Flujo_Trabajo_Operativo_${fechaHoy}.pdf`;

    // 7. CALCULAR DIMENSIONES DINÁMICAS EXACTAS PARA 1 SOLA HOJA COMPACTA
    const anchoPulgadas = 8.5;
    const margenHoriz = 0.25; // 0.25 in cada lado
    const margenVert = 0.30;  // 0.30 in arriba y abajo
    const anchoImprimible = anchoPulgadas - (margenHoriz * 2); // 8.0 in

    const anchoRealPx = contenedorOriginal.offsetWidth || 1000;
    const altoRealPx = contenedorOriginal.offsetHeight || 1600;

    // Altura proporcional del contenido en pulgadas
    const altoContenidoIn = anchoImprimible * (altoRealPx / anchoRealPx);
    // Altura total de la página: incluye márgenes + 0.35 in de margen de seguridad para garantizar 1 sola página
    const altoTotalIn = parseFloat((altoContenidoIn + (margenVert * 2) + 0.35).toFixed(2));

    const opciones = {
        margin: [margenVert, margenHoriz, margenVert, margenHoriz],
        filename: nombreArchivo,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: '#081322'
        },
        jsPDF: { 
            unit: 'in', 
            format: [anchoPulgadas, altoTotalIn], 
            orientation: 'portrait' 
        }
    };

    const cleanup = () => {
        contenedorOriginal.classList.remove('flujo-modo-pdf-compacto');
        if (mapaEtapas) mapaEtapas.style.display = estadoMapa;
        if (headerPdf && headerPdf.parentNode) headerPdf.parentNode.removeChild(headerPdf);
        if (footerPdf && footerPdf.parentNode) footerPdf.parentNode.removeChild(footerPdf);
        window.scrollTo(0, scrollPrevio);
        if (btn) {
            btn.innerHTML = textoOriginal;
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    };

    // Pausa de 120ms para asegurar que el navegador aplique los estilos compactos antes de renderizar
    setTimeout(() => {
        if (typeof html2pdf !== 'undefined') {
            html2pdf().set(opciones).from(contenedorOriginal).save().then(() => {
                cleanup();
                if (btn) {
                    btn.innerHTML = '<span style="font-size:0.95rem; line-height:1;">✅</span><span>¡1 Hoja Descargada!</span>';
                    setTimeout(() => {
                        btn.innerHTML = textoOriginal;
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }, 2500);
                }
            }).catch(err => {
                console.error("Error al generar PDF con html2pdf:", err);
                cleanup();
                imprimirDiagramaDirecto();
            });
        } else {
            cleanup();
            imprimirDiagramaDirecto();
        }
    }, 120);
}

function imprimirDiagramaDirecto() {
    const contenedor = document.querySelector('.flujo-contenedor-principal');
    if (!contenedor) return;

    const ventana = window.open('', '_blank');
    if (!ventana) {
        alert("Por favor permite las ventanas emergentes para imprimir o guardar el diagrama como PDF.");
        return;
    }
    ventana.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Diagrama de Flujo de Trabajo Operativo - Flota Automotriz</title>
            <style>
                body {
                    background: #081322;
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    padding: 15px;
                    margin: 0;
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    max-width: 100% !important;
                }
                * { box-sizing: border-box; }
                a, .nav-rapida-paso, .mapa-etapas-contenedor, button, p { display: none !important; }
                .flujo-box { padding: 9px 12px !important; margin-bottom: 0 !important; }
                .flujo-box h4, .flujo-box h5 { margin: 0 !important; font-size: 0.92rem !important; }
                .lane-cotizacion { min-width: 0 !important; flex: 1 !important; padding: 10px 8px !important; }
                .flujo-flecha-conector { margin: 2px 0 !important; }
                .flujo-flecha-linea { height: 7px !important; }
                .etapa-header-bar { padding: 7px 12px !important; margin: 10px 0 6px 0 !important; }
                @page {
                    size: letter portrait;
                    margin: 8mm;
                }
                @media print {
                    body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
                    .flujo-box, .etapa-header-bar, .lane-cotizacion, .flujo-flecha-conector {
                        page-break-inside: avoid !important;
                        break-inside: avoid !important;
                    }
                }
            </style>
        </head>
        <body>
            <div style="text-align: center; margin-bottom: 18px; border-bottom: 2px solid #1f395a; padding-bottom: 10px;">
                <h1 style="color: #ffffff; margin: 0 0 5px 0; font-size: 1.45rem;">SISTEMA INTEGRAL DE FLOTA AUTOMOTRIZ • DIAGRAMA DE FLUJO DE TRABAJO</h1>
                <p style="display:block !important; margin: 0; color: #94a3b8; font-size: 0.88rem;">Procedimiento Operativo Oficial de Gestión y Liquidación de Tickets de Servicio</p>
            </div>
            ${contenedor.innerHTML}
            <script>
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 500);
                };
            <\/script>
        </body>
        </html>
    `);
    ventana.document.close();
}

window.descargarDiagramaFlujo = descargarDiagramaFlujo;
window.imprimirDiagramaDirecto = imprimirDiagramaDirecto;


window.actualizarBadgeRetrabajoProveedor = async function() {
    try {
        const res = await fetch('/api/garantia/proveedor/lista');
        const data = await res.json();
        const retrabajos = data.retrabajos || [];
        const badgeProv = document.getElementById('badge-retrabajo-prov');
        if (badgeProv) {
            if (retrabajos.length > 0) {
                badgeProv.innerText = retrabajos.length;
                badgeProv.style.display = 'inline-block';
            } else {
                badgeProv.style.display = 'none';
            }
        }
    } catch(e) {}
};
