// =========================================================
// ARCHIVO: static/facturas_herramientas.js
// PROPÓSITO: Utilidades y funciones de interfaz (loaders, formatos)
// =========================================================

function formatearMoneda(valor) { return parseFloat(valor || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
function formatearEnInput(input) { if(!input.value) return; let num = parseFloat(input.value.replace(/[^0-9.]/g, '')); if(isNaN(num)) return; input.value = num.toLocaleString('en-US', {style: 'currency', currency: 'USD'}).replace('$', '$ ') + ' MXN'; }
function limpiarInput(input) { input.value = input.value.replace(/[^0-9.]/g, ''); }
function validarNumeros(input) { input.value = input.value.replace(/[^0-9]/g, ''); }
function validarLetras(input) { input.value = input.value.replace(/[^a-zA-Z\sñÑáéíóúÁÉÍÓÚ]/g, ''); }
function validarDecimales(input) { input.value = input.value.replace(/[^0-9.]/g, ''); if ((input.value.match(/\./g) || []).length > 1) { input.value = input.value.substring(0, input.value.lastIndexOf('.')); } }

function abrirLightbox(src) { document.getElementById('lightbox-img').src = src; document.getElementById('lightbox-modal').style.display = 'flex'; }
function cerrarLightbox(event) { if(event.target.id === 'lightbox-modal' || event.target.className === 'lightbox-close') { document.getElementById('lightbox-modal').style.display = 'none'; document.getElementById('lightbox-img').src = ''; } }

function mostrarLoaderDinamico(textoPrincipal, textoSecundario) {
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
    document.getElementById('loader-txt-main').innerText = textoPrincipal;
    document.getElementById('loader-txt-sub').innerText = textoSecundario;
    loader.style.display = 'flex';
}

function ocultarLoaderDinamico() {
    let loader = document.getElementById('loader-confirmacion');
    if (loader) loader.style.display = 'none';
}