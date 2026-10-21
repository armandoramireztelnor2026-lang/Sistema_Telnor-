let filtroEstadoActual = null;

async function cargarUnidades() {
    try {
        console.log('Iniciando cargarUnidades...');
        const [res, resMetricas] = await Promise.all([
            fetch('/api/unidades'),
            fetch('/api/unidades/metricas')
        ]);
        const data = await res.json();
        const dataMetricas = await resMetricas.json();

        // Actualizar tarjetas de métricas si están disponibles
        if (dataMetricas && dataMetricas.totales) {
            const t = dataMetricas.totales;
            const p = dataMetricas.porcentajes;
            const setTxt = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = val;
            };
            setTxt('metrica-circulacion-unidades', t.circulacion);
            setTxt('porcentaje-circulacion-unidades', p.circulacion + '%');
            setTxt('metrica-taller-unidades', t.taller);
            setTxt('porcentaje-taller-unidades', p.taller + '%');
            setTxt('metrica-juridicos-unidades', t.juridicos);
            setTxt('porcentaje-juridicos-unidades', p.juridicos + '%');
            setTxt('metrica-inhabilitadas-unidades', t.inhabilitadas);
            setTxt('porcentaje-inhabilitadas-unidades', p.inhabilitadas + '%');
        }

        let tbody = document.getElementById('tbody-unidades');
        if (!tbody) return;

        tbody.innerHTML = '';

        let rows = '';
        for (const [idUnidad, info] of Object.entries(data)) {
            let isInShop = info.activa_en_taller;
            let isJuridico = info.Juridicos === true;
            let est = info.estado_operativo || (isInShop ? 'En Taller' : (isJuridico ? 'En Jurídicos' : (info.Estado === 'Inactiva' ? 'Inhabilitada' : 'En Circulación')));

            let estadoBadge = '';
            if (est === 'En Taller') {
                estadoBadge = '<span class="badge-taller" style="background:#0284c7; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🔧 En Taller</span>';
            } else if (est === 'En Jurídicos') {
                estadoBadge = '<span class="badge-juridicos" style="background:#6d28d9; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⚖️ En Jurídicos</span>';
            } else if (est === 'Inhabilitada') {
                estadoBadge = '<span class="badge-inhabilitada" style="background:#ef4444; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⛔ Inhabilitada (Caras)</span>';
            } else {
                estadoBadge = '<span class="badge-circulacion" style="background:#10b981; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🚗 En Circulación</span>';
            }

            let disabledAttr = (isInShop || isJuridico) ? 'disabled' : '';
            let styleOpacity = (isInShop || isJuridico) ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';
            let tooltip = isInShop ? 'title="Esta unidad tiene un ticket activo y no puede ser modificada"' : (isJuridico ? 'title="Unidad inhabilitada por estar en Jurídicos"' : '');

            let juridicoBtnText = isJuridico ? 'Quitar Jurídicos' : 'Jurídicos';
            let juridicoBtnColor = isJuridico ? '#6d28d9' : '#8b5cf6';

            let juridicoDisabledAttr = isInShop ? 'disabled' : '';
            let juridicoStyleOpacity = isInShop ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';

            rows += `
                <tr data-estado="${est}">
                    <td style="font-weight:bold; color:#0ea5e9;">${idUnidad}</td>
                    <td>${info.Marca || 'N/A'}</td>
                    <td>${info.Modelo || 'N/A'}</td>
                    <td>${estadoBadge}</td>
                    <td>
                        <button ${disabledAttr} ${tooltip} onclick="abrirModalUnidad('editar', '${idUnidad}', '${info.Marca || ''}', '${info.Modelo || ''}')" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:5px; margin-right:5px; ${styleOpacity}">Editar</button>
                        <button ${disabledAttr} ${tooltip} onclick="eliminarUnidad('${idUnidad}')" style="background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:5px; margin-right:5px; ${styleOpacity}">Eliminar</button>
                        ${info.Estado === 'Inactiva' 
                            ? `<button ${disabledAttr} ${tooltip} onclick="toggleEstadoUnidad('${idUnidad}')" style="background:#10b981; color:white; border:none; padding:5px 10px; border-radius:5px; margin-right:5px; ${styleOpacity}">Activar</button>`
                            : `<button ${disabledAttr} ${tooltip} onclick="toggleEstadoUnidad('${idUnidad}')" style="background:#f59e0b; color:white; border:none; padding:5px 10px; border-radius:5px; margin-right:5px; ${styleOpacity}">Desactivar</button>`
                        }
                        <button ${juridicoDisabledAttr} ${tooltip} onclick="verJuridicos('${idUnidad}')" style="background:${juridicoBtnColor}; color:white; border:none; padding:5px 10px; border-radius:5px; ${juridicoStyleOpacity}">${juridicoBtnText}</button>
                    </td>
                </tr>
            `;
        }

        if (rows === '') {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No hay unidades registradas.</td></tr>';
        } else {
            tbody.innerHTML = rows;
            if (filtroEstadoActual) {
                aplicarFiltroUnidades();
            }
        }
    } catch (e) {
        console.error("Error al cargar unidades:", e);
        let tbody = document.getElementById('tbody-unidades');
        if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#ef4444;">Error al cargar unidades.</td></tr>';
    }
}

function filtrarUnidadesPorEstado(estado) {
    if (filtroEstadoActual === estado) {
        filtroEstadoActual = null;
    } else {
        filtroEstadoActual = estado;
    }
    actualizarBordesTarjetasFiltro();
    aplicarFiltroUnidades();
}

function actualizarBordesTarjetasFiltro() {
    const mapClase = {
        'En Circulación': 'card-circulacion',
        'En Taller': 'card-taller',
        'En Jurídicos': 'card-juridicos',
        'Inhabilitada': 'card-inhabilitadas'
    };
    document.querySelectorAll('.card-metrica-flota').forEach(c => {
        c.style.transform = 'scale(1)';
        c.style.boxShadow = 'none';
        c.style.borderColor = '';
    });
    if (filtroEstadoActual && mapClase[filtroEstadoActual]) {
        const active = document.querySelector(`.${mapClase[filtroEstadoActual]}`);
        if (active) {
            active.style.transform = 'scale(1.02)';
            active.style.boxShadow = '0 0 15px rgba(255,255,255,0.2)';
            active.style.borderColor = '#ffffff';
        }
    }
}

function aplicarFiltroUnidades() {
    const inputSearch = document.getElementById('search-unidades');
    const q = inputSearch ? inputSearch.value.toLowerCase().trim() : '';
    const rows = document.querySelectorAll('#tbody-unidades tr');

    rows.forEach(r => {
        const est = r.getAttribute('data-estado');
        const estadoOk = !filtroEstadoActual || est === filtroEstadoActual;
        const textOk = !q || r.innerText.toLowerCase().includes(q);
        r.style.display = (estadoOk && textOk) ? '' : 'none';
    });
}

function abrirModalUnidad(modo, id = '', marca = '', modelo = '') {
    document.getElementById('unidad-modo').value = modo;
    document.getElementById('unidad-old-numero').value = id;

    document.getElementById('unidad-numero').value = id;
    document.getElementById('unidad-marca').value = marca;
    document.getElementById('unidad-modelo').value = modelo;

    if (modo === 'agregar') {
        document.getElementById('modal-unidad-title').textContent = 'Agregar Unidad';
        document.getElementById('btn-unidad-submit').textContent = 'Agregar';
    } else {
        document.getElementById('modal-unidad-title').textContent = 'Editar Unidad';
        document.getElementById('btn-unidad-submit').textContent = 'Guardar Cambios';
    }

    document.getElementById('modal-unidad').style.display = 'flex';
}

async function guardarUnidad() {
    let modo = document.getElementById('unidad-modo').value;
    let old_numero = document.getElementById('unidad-old-numero').value;
    let numero = document.getElementById('unidad-numero').value.trim();
    let marca = document.getElementById('unidad-marca').value.trim();
    let modelo = document.getElementById('unidad-modelo').value.trim();

    if (!numero) {
        alert('El número económico es obligatorio.');
        return;
    }

    let mensajeConfirm = modo === 'agregar' ? '¿Estás seguro de AGREGAR esta nueva unidad?' : '¿Estás seguro de ACTUALIZAR los datos de esta unidad?';
    if (!confirm(mensajeConfirm)) {
        return;
    }

    let fd = new FormData();
    fd.append('modo', modo);
    fd.append('old_numero', old_numero);
    fd.append('numero', numero);
    fd.append('marca', marca);
    fd.append('modelo', modelo);

    let btn = document.getElementById('btn-unidad-submit');
    let oldText = btn.textContent;
    btn.textContent = 'Guardando...';
    btn.disabled = true;

    try {
        let res = await fetch('/api/unidades/guardar', { method: 'POST', body: fd });
        let data = await res.json();
        if (data.status === 'success') {
            document.getElementById('modal-unidad').style.display = 'none';
            cargarUnidades();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al guardar la unidad.');
    } finally {
        btn.textContent = oldText;
        btn.disabled = false;
    }
}

async function eliminarUnidad(numero) {
    if (!confirm('¿Estás seguro de eliminar la unidad ' + numero + '? Esta acción no se puede deshacer.')) return;

    let fd = new FormData();
    fd.append('numero', numero);

    try {
        let res = await fetch('/api/unidades/eliminar', { method: 'POST', body: fd });
        let data = await res.json();
        if (data.status === 'success') {
            cargarUnidades();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al eliminar.');
    }
}

async function toggleEstadoUnidad(numero) {
    if (!confirm('¿Estás seguro de cambiar el estado de la unidad ' + numero + '?')) return;

    let fd = new FormData();
    fd.append('numero', numero);

    try {
        let res = await fetch('/api/unidades/toggle_estado', { method: 'POST', body: fd });
        let data = await res.json();
        if (data.status === 'success') {
            cargarUnidades();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al cambiar el estado.');
    }
}

async function verJuridicos(numero) {
    if (!confirm('¿Estás seguro de cambiar el estado jurídico de la unidad ' + numero + '?')) return;

    let fd = new FormData();
    fd.append('numero', numero);

    try {
        let res = await fetch('/api/unidades/toggle_juridicos', { method: 'POST', body: fd });
        let data = await res.json();
        if (data.status === 'success') {
            cargarUnidades();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error al cambiar el estado jurídico.');
    }
}
