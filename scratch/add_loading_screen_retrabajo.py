# -*- coding: utf-8 -*-

with open('static/script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Safe fallback definition of mostrarLoaderDinamico / ocultarLoaderDinamico
loader_helpers = """
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
"""

target_reasig = """    try {
        let res = await fetch('/api/garantia/reasignar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId })
        });
        let data = await res.json();

        if (data.status === 'success') {
            alert(data.message || 'Retrabajo reasignado exitosamente al taller.');
            cerrarModal('modal-detalle-retrabajo');
            if (typeof cargarRetrabajosAdmin === 'function') cargarRetrabajosAdmin();
        } else {
            alert('Error: ' + (data.message || 'No se pudo reasignar el retrabajo.'));
        }
    } catch (err) {
        console.error('Error al reasignar retrabajo:', err);
        alert('Ocurrió un error al procesar la reasignación de garantía.');
    }"""

repl_reasig = """    if (typeof window.mostrarLoaderDinamico === 'function') {
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
    }"""

if target_reasig in c:
    c = c.replace(target_reasig, repl_reasig, 1)
    print("OK: Replaced target_reasig (LF)")
elif target_reasig.replace('\n', '\r\n') in c:
    c = c.replace(target_reasig.replace('\n', '\r\n'), repl_reasig.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_reasig (CRLF)")
else:
    print("Warning: target_reasig not found")

# Also cancel reasignacion loader
target_cancel = """    try {
        let res = await fetch('/api/garantia/cancelar_reasignacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticket: ticketId, motivo: motivo })
        });
        let data = await res.json();

        if (data.status === 'success') {
            alert(data.message || 'La reasignación ha sido cancelada y el reporte eliminado.');
            cerrarModal('modal-cancelar-reasignacion');
            cerrarModal('modal-detalle-retrabajo');
            if (typeof cargarRetrabajosAdmin === 'function') cargarRetrabajosAdmin();
        } else {
            alert('Error: ' + (data.message || 'No se pudo cancelar la reasignación.'));
        }
    } catch (err) {
        console.error('Error al cancelar reasignación:', err);
        alert('Ocurrió un error al procesar la cancelación de la reasignación.');
    }"""

repl_cancel = """    if (typeof window.mostrarLoaderDinamico === 'function') {
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
    }"""

if target_cancel in c:
    c = c.replace(target_cancel, repl_cancel, 1)
    print("OK: Replaced target_cancel (LF)")
elif target_cancel.replace('\n', '\r\n') in c:
    c = c.replace(target_cancel.replace('\n', '\r\n'), repl_cancel.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_cancel (CRLF)")
else:
    print("Warning: target_cancel not found")

# Append loader_helpers at top or bottom if not already there
if 'window.mostrarLoaderDinamico = function' not in c:
    c = loader_helpers + "\n" + c
    print("OK: Appended loader_helpers")

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Actualizado static/script.js con pantalla de carga")

