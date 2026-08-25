// =========================================================
// ARCHIVO: static/facturas_archivos.js
// PROPÓSITO: Manejo de los archivos (fotos de cotización/evidencia)
// =========================================================

let dtCotizacion = new DataTransfer();
let dtEvidencia = new DataTransfer();

let dtCotizacionEdicion = new DataTransfer();
let dtEvidenciaEdicion = new DataTransfer();
let imagenesGuardadasCotizacion = [];
let imagenesGuardadasEvidencia = [];

document.addEventListener("DOMContentLoaded", function() {
    const inputCotizacion = document.getElementById('fotos_cotizacion');
    const inputEvidencia = document.getElementById('fotos_evidencia');
    if(inputCotizacion) { inputCotizacion.addEventListener('change', function() { Array.from(this.files).forEach(file => dtCotizacion.items.add(file)); renderizarMiniaturas('fotos_cotizacion', 'preview-cotizacion', dtCotizacion); }); }
    if(inputEvidencia) { inputEvidencia.addEventListener('change', function() { Array.from(this.files).forEach(file => dtEvidencia.items.add(file)); renderizarMiniaturas('fotos_evidencia', 'preview-evidencia', dtEvidencia); }); }

    const inputCotEdit = document.getElementById('edit_fotos_cotizacion_nuevas');
    const inputEviEdit = document.getElementById('edit_fotos_evidencia_nuevas');
    if(inputCotEdit) inputCotEdit.addEventListener('change', function() { Array.from(this.files).forEach(file => dtCotizacionEdicion.items.add(file)); renderizarMiniaturasEdicion('edit_fotos_cotizacion_nuevas', 'edit-preview-cotizacion-nuevas', dtCotizacionEdicion); });
    if(inputEviEdit) inputEviEdit.addEventListener('change', function() { Array.from(this.files).forEach(file => dtEvidenciaEdicion.items.add(file)); renderizarMiniaturasEdicion('edit_fotos_evidencia_nuevas', 'edit-preview-evidencia-nuevas', dtEvidenciaEdicion); });
});

function renderizarMiniaturas(inputId, previewContainerId, dataTransferObj) {
    const input = document.getElementById(inputId); const container = document.getElementById(previewContainerId); input.files = dataTransferObj.files; container.innerHTML = ''; 
    Array.from(dataTransferObj.files).forEach((file, index) => {
        const div = document.createElement('div'); div.className = 'preview-item';
        if (file.type.startsWith('image/')) { div.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="preview" onclick="abrirLightbox('${URL.createObjectURL(file)}')" style="cursor:zoom-in;"><button type="button" class="preview-remove" onclick="removerArchivo('${inputId}', '${previewContainerId}', ${index})">×</button>`; } 
        else { div.innerHTML = `<div class="file-icon" title="${file.name}">📄</div><button type="button" class="preview-remove" onclick="removerArchivo('${inputId}', '${previewContainerId}', ${index})">×</button>`; }
        container.appendChild(div);
    });
}

function removerArchivo(inputId, previewContainerId, indexABorrar) {
    let dataTransferActual = (inputId === 'fotos_cotizacion') ? dtCotizacion : dtEvidencia; let nuevoDt = new DataTransfer(); 
    Array.from(dataTransferActual.files).forEach((file, i) => { if (i !== indexABorrar) nuevoDt.items.add(file); });
    if (inputId === 'fotos_cotizacion') dtCotizacion = nuevoDt; else dtEvidencia = nuevoDt; renderizarMiniaturas(inputId, previewContainerId, (inputId === 'fotos_cotizacion') ? dtCotizacion : dtEvidencia);
}

function renderizarImagenesGuardadas() {
    const contCot = document.getElementById('edit-preview-cotizacion-guardadas'); const contEvi = document.getElementById('edit-preview-evidencia-guardadas');
    contCot.innerHTML = ''; contEvi.innerHTML = '';
    imagenesGuardadasCotizacion.forEach((foto, i) => { let div = document.createElement('div'); div.className = 'preview-item'; if(foto.endsWith('.pdf')) div.innerHTML = `<div class="file-icon">📄</div><button type="button" class="preview-remove" onclick="quitarImagenGuardada('cotizacion', ${i})">×</button>`; else div.innerHTML = `<img src="/static/facturas_archivos/${foto}"><button type="button" class="preview-remove" onclick="quitarImagenGuardada('cotizacion', ${i})">×</button>`; contCot.appendChild(div); });
    imagenesGuardadasEvidencia.forEach((foto, i) => { let div = document.createElement('div'); div.className = 'preview-item'; div.innerHTML = `<img src="/static/facturas_archivos/${foto}"><button type="button" class="preview-remove" onclick="quitarImagenGuardada('evidencia', ${i})">×</button>`; contEvi.appendChild(div); });
}

function quitarImagenGuardada(tipo, index) { if(tipo === 'cotizacion') imagenesGuardadasCotizacion.splice(index, 1); else imagenesGuardadasEvidencia.splice(index, 1); renderizarImagenesGuardadas(); }

function renderizarMiniaturasEdicion(inputId, previewContainerId, dataTransferObj) {
    const input = document.getElementById(inputId); const container = document.getElementById(previewContainerId); input.files = dataTransferObj.files; container.innerHTML = ''; 
    Array.from(dataTransferObj.files).forEach((file, index) => {
        const div = document.createElement('div'); div.className = 'preview-item';
        if (file.type.startsWith('image/')) div.innerHTML = `<img src="${URL.createObjectURL(file)}"><button type="button" class="preview-remove" onclick="removerArchivoEdicion('${inputId}', '${previewContainerId}', ${index})">×</button>`;
        else div.innerHTML = `<div class="file-icon">📄</div><button type="button" class="preview-remove" onclick="removerArchivoEdicion('${inputId}', '${previewContainerId}', ${index})">×</button>`;
        container.appendChild(div);
    });
}

function removerArchivoEdicion(inputId, previewContainerId, indexABorrar) {
    let dataTransferActual = (inputId === 'edit_fotos_cotizacion_nuevas') ? dtCotizacionEdicion : dtEvidenciaEdicion; let nuevoDt = new DataTransfer(); 
    Array.from(dataTransferActual.files).forEach((file, i) => { if (i !== indexABorrar) nuevoDt.items.add(file); });
    if (inputId === 'edit_fotos_cotizacion_nuevas') dtCotizacionEdicion = nuevoDt; else dtEvidenciaEdicion = nuevoDt; renderizarMiniaturasEdicion(inputId, previewContainerId, (inputId === 'edit_fotos_cotizacion_nuevas') ? dtCotizacionEdicion : dtEvidenciaEdicion);
}