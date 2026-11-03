import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

target1 = """    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación (App Password de Google).");
        return;
    }"""

replace1 = """    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación (App Password de Google).");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas guardar y actualizar las credenciales del correo emisor oficial (${correo})?`);
    if (!confirmar) return;"""

target2 = """    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación.");
        return;
    }"""

replace2 = """    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas registrar y agregar la nueva cuenta de correo "${nombre}" (${correo})?`);
    if (!confirmar) return;"""

assert target1 in js, "target1 not found"
assert target2 in js, "target2 not found"

js = js.replace(target1, replace1, 1)
js = js.replace(target2, replace2, 1)

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Confirmaciones agregadas a guardarCorreoEmisor y guardarNuevaCuentaCorreo con éxito!")

