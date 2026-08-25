// =========================================================
// ARCHIVO: static/liberacion.js
// PROPÓSITO: Módulo Front-end para Validar Códigos (Aduana)
// =========================================================

let facturaAValidar = null;

// Esta función despierta cuando haces clic en "Validar Código"
function abrirModalValidacion(idFactura, unidad) {
    facturaAValidar = idFactura;
    document.getElementById('lbl-unidad-validar').innerText = '8090-' + unidad;
    document.getElementById('input-codigo-liberacion').value = '';
    document.getElementById('modal-validar-codigo').style.display = 'flex';
}

// Esta función lee el número y va a preguntarle al servidor
function procesarValidacionCodigo() {
    const codigoIngresado = document.getElementById('input-codigo-liberacion').value.trim();
    
    if(codigoIngresado.length !== 8) {
        alert("⚠️ Por seguridad, el código debe tener exactamente 8 dígitos numéricos.");
        return;
    }

    const btn = document.getElementById('btn-verificar-codigo');
    btn.innerText = "Verificando código...";
    btn.disabled = true;

    // Viaja al backend a preguntar si el código hace match
    fetch('/api/facturas/validar_codigo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id_factura: facturaAValidar,
            codigo: codigoIngresado
        })
    })
    .then(res => res.json())
    .then(data => {
        btn.innerText = "Verificar Código";
        btn.disabled = false;

        if(data.status === 'success') {
            // ¡Match Perfecto! Cerramos ventana y actualizamos tabla
            alert("✅ ¡CÓDIGO CONFIRMADO! El vehículo ha sido liberado exitosamente.");
            cerrarModal('modal-validar-codigo');
            
            // Recargamos la tabla para que la columna "Entregado" pase mágicamente de "No" a "Sí"
            if(typeof cargarFacturas === 'function') {
                cargarFacturas();
            }
        } else {
            alert("❌ ALERTA: " + data.message);
        }
    })
    .catch(err => {
        console.error(err);
        alert("❌ Hubo un error de conexión con el servidor.");
        btn.innerText = "Verificar Código";
        btn.disabled = false;
    });
}