with open('static/facturas_principal.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    fetch('/api/facturas/confirmar_admin', {
        method: 'POST',
        body: formData
    }).then(res => res.json()).then(data => {
        ocultarLoaderDinamico();
        alert(data.message);
        document.getElementById('modal-revision-admin').style.display = 'none';
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });"""

replacement = """    fetch('/api/facturas/confirmar_admin', {
        method: 'POST',
        body: formData
    }).then(async res => {
        const data = await res.json();
        ocultarLoaderDinamico();
        if (!res.ok || data.status === 'error') {
            alert(data.message || "Error al procesar la cotización.");
            return;
        }
        alert(data.message);
        document.getElementById('modal-revision-admin').style.display = 'none';
        cargarFacturas();
    }).catch(err => {
        ocultarLoaderDinamico();
        console.error(err);
    });"""

assert target in code, "target not found in static/facturas_principal.js"
code = code.replace(target, replacement, 1)

with open('static/facturas_principal.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("static/facturas_principal.js actualizado correctamente!")

