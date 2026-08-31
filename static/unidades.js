async function cargarUnidades() {
    try {
        console.log('Iniciando cargarUnidades...');
        const res = await fetch('/api/unidades');
        const data = await res.json();

        let tbody = document.getElementById('tbody-unidades');
        if (!tbody) return;

        tbody.innerHTML = '';

        let rows = '';
        for (const [idUnidad, info] of Object.entries(data)) {
            rows += `
                <tr>
                    <td style="font-weight:bold; color:#0ea5e9;">${idUnidad}</td>
                    <td>${info.Marca || 'N/A'}</td>
                    <td>${info.Modelo || 'N/A'}</td>
                    <td>
                        <button onclick="abrirModalUnidad('editar', '${idUnidad}', '${info.Marca || ''}', '${info.Modelo || ''}')" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer; margin-right:5px;">Editar</button>
                        <button onclick="eliminarUnidad('${idUnidad}')" style="background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">Eliminar</button>
                    </td>
                </tr>
            `;
        }

        if (rows === '') {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">No hay unidades registradas.</td></tr>';
        } else {
            tbody.innerHTML = rows;
        }
    } catch (e) {
        console.error("Error al cargar unidades:", e);
        let tbody = document.getElementById('tbody-unidades');
        if (tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#ef4444;">Error al cargar unidades.</td></tr>';
    }
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
