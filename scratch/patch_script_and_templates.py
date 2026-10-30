import re

def update_proveedores_html():
    with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update button styling for Retrabajo
    old_btn = '<button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv(\'retrabajo\')" style="display: flex; align-items: center; justify-content: center; gap: 6px;">'
    new_btn = '<button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv(\'retrabajo\')" style="display: flex; align-items: center; justify-content: space-between; padding-left: 20px; padding-right: 15px;">'
    
    if old_btn in html:
        html = html.replace(old_btn, new_btn)
        print("Updated Retrabajo button in proveedores.html")
    else:
        print("old_btn not found in proveedores.html")

    # 2. Bump script.js cache version
    html = re.sub(r'src="/static/script\.js\?v=\d+"', 'src="/static/script.js?v=1000035"', html)

    with open('templates/proveedores.html', 'w', encoding='utf-8') as f:
        f.write(html)

def update_script_js():
    with open('static/script.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Update cambiarVistaProv to always refresh badge
    old_cambiar = '''    } else if (vista === 'retrabajo') {
        if (document.getElementById('vista-retrabajo')) {
            document.getElementById('vista-retrabajo').style.display = 'block';
        }
        if (typeof cargarRetrabajosProveedor === 'function') cargarRetrabajosProveedor();
    }
}'''

    new_cambiar = '''    } else if (vista === 'retrabajo') {
        if (document.getElementById('vista-retrabajo')) {
            document.getElementById('vista-retrabajo').style.display = 'block';
        }
        if (typeof cargarRetrabajosProveedor === 'function') cargarRetrabajosProveedor();
    }

    if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
        actualizarBadgeRetrabajoProveedor();
    }
}'''

    if old_cambiar in js:
        js = js.replace(old_cambiar, new_cambiar, 1)
        print("Updated cambiarVistaProv in script.js")
    else:
        print("old_cambiar not found in script.js")

    # 2. Update DOMContentLoaded for provider
    old_dom = '''    if (document.getElementById('vista-reportes-prov')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }
    }'''

    new_dom = '''    if (document.getElementById('vista-reportes-prov') || document.getElementById('vista-retrabajo')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }
        if (!window._intervalRetrabajoProv) {
            window._intervalRetrabajoProv = setInterval(function() {
                if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
                    actualizarBadgeRetrabajoProveedor();
                }
            }, 20000);
        }
    }'''

    if old_dom in js:
        js = js.replace(old_dom, new_dom, 1)
        print("Updated DOMContentLoaded in script.js")
    else:
        print("old_dom not found in script.js")

    # 3. Update actualizarBadgeRetrabajoProveedor styling
    old_badge = '''        if (badgeProv) {
            if (retrabajos.length > 0) {
                badgeProv.innerText = retrabajos.length;
                badgeProv.style.display = 'inline-block';
            } else {
                badgeProv.style.display = 'none';
            }
        }'''

    new_badge = '''        if (badgeProv) {
            if (retrabajos.length > 0) {
                badgeProv.innerText = retrabajos.length;
                badgeProv.style.display = 'inline-flex';
                badgeProv.style.alignItems = 'center';
                badgeProv.style.justifyContent = 'center';
            } else {
                badgeProv.style.display = 'none';
            }
        }'''

    if old_badge in js:
        js = js.replace(old_badge, new_badge)
        print("Updated badgeProv styling in script.js")
    else:
        print("old_badge not found in script.js")

    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)

update_proveedores_html()
update_script_js()

