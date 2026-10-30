with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = '''    if (document.getElementById('vista-reportes-prov') || document.getElementById('vista-retrabajo')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }

    }
    if (document.getElementById('vista-cotizaciones-corp')) { 
        let savedView = localStorage.getItem('activeViewCorp');
        cambiarVistaCorp(savedView ? savedView : 'cotizaciones'); 
    }'''

replacement = '''    } else if (rolActual === 'proveedores' || document.getElementById('vista-reportes-prov')) { 
        let savedView = localStorage.getItem('activeViewProv');
        cambiarVistaProv(savedView ? savedView : 'reportes'); 
        if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
            actualizarBadgeRetrabajoProveedor();
        }
    } else if (rolActual === 'corporativos' || document.getElementById('vista-cotizaciones-corp')) { 
        let savedView = localStorage.getItem('activeViewCorp');
        cambiarVistaCorp(savedView ? savedView : 'cotizaciones'); 
    }'''

# Check with normalized newlines
js_norm = js.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

if target_norm in js_norm:
    js_norm = js_norm.replace(target_norm, replacement_norm, 1)
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js_norm)
    print("SUCCESS: script.js updated with else if branches.")
else:
    print("ERROR: target not found in script.js")

