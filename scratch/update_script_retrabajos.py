# -*- coding: utf-8 -*-

with open('static/script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update abrirDetalleRetrabajo button state
target_btn = """        const btnReasig = document.getElementById('btn-reasignar-retrabajo');
        if (btnReasig) {
            btnReasig.setAttribute('data-ticket', ticketId);
        }"""

repl_btn = """        const btnReasig = document.getElementById('btn-reasignar-retrabajo');
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
        }"""

if target_btn in c:
    c = c.replace(target_btn, repl_btn, 1)
    print("OK: Replaced target_btn (LF)")
elif target_btn.replace('\n', '\r\n') in c:
    c = c.replace(target_btn.replace('\n', '\r\n'), repl_btn.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_btn (CRLF)")
else:
    print("Warning: target_btn not found")

# 2. Update badge inside cargarRetrabajosProveedor
target_badge = """        const res = await fetch('/api/garantia/proveedor/lista');
        const data = await res.json();
        const retrabajos = data.retrabajos || [];

        if (retrabajos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:25px; color:#94a3b8;">No tienes órdenes de retrabajo o garantía pendientes de atender.</td></tr>';
            return;
        }"""

repl_badge = """        const res = await fetch('/api/garantia/proveedor/lista');
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
        }"""

if target_badge in c:
    c = c.replace(target_badge, repl_badge, 1)
    print("OK: Replaced target_badge (LF)")
elif target_badge.replace('\n', '\r\n') in c:
    c = c.replace(target_badge.replace('\n', '\r\n'), repl_badge.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_badge (CRLF)")
else:
    print("Warning: target_badge not found")

# 3. Add actualizarBadgeRetrabajoProveedor and hook it up on load
addon_func = """
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
"""

target_load = """    if (document.getElementById('vista-reportes-prov')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
    }"""

repl_load = """    if (document.getElementById('vista-reportes-prov')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }
    }"""

if target_load in c:
    c = c.replace(target_load, repl_load, 1)
    print("OK: Replaced target_load (LF)")
elif target_load.replace('\n', '\r\n') in c:
    c = c.replace(target_load.replace('\n', '\r\n'), repl_load.replace('\n', '\r\n'), 1)
    print("OK: Replaced target_load (CRLF)")
else:
    print("Warning: target_load not found")

c += addon_func

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Actualizado static/script.js")

