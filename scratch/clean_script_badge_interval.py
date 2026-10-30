with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_code = '''        if (!window._intervalRetrabajoProv) {
            window._intervalRetrabajoProv = setInterval(function() {
                if (typeof actualizarBadgeRetrabajoProveedor === 'function') {
                    actualizarBadgeRetrabajoProveedor();
                }
            }, 20000);
        }'''

if old_code in js:
    js = js.replace(old_code, '')
    print("Removed _intervalRetrabajoProv from script.js")

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

