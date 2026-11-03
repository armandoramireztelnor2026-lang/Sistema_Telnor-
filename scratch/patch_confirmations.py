import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. En guardarCorreoEmisor:
target_gc = "alert(\"⚠️ Por favor ingresa el código o contraseña de aplicación (16 caracteres de Google).\");\n        return;\n    }"
replace_gc = """alert("⚠️ Por favor ingresa el código o contraseña de aplicación (16 caracteres de Google).");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas guardar y actualizar las credenciales del correo emisor oficial (${correo})?`);
    if (!confirmar) return;"""

if target_gc in js:
    js = js.replace(target_gc, replace_gc, 1)
    print("Confirmación agregada a guardarCorreoEmisor")
else:
    print("Aviso: No se encontró target_gc")

# 2. En guardarNuevaCuentaCorreo:
target_nc = "alert(\"⚠️ Por favor ingresa la contraseña o código de aplicación.\");\n        return;\n    }"
replace_nc = """alert("⚠️ Por favor ingresa la contraseña o código de aplicación.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas registrar y agregar la nueva cuenta de correo "${nombre}" (${correo})?`);
    if (!confirmar) return;"""

if target_nc in js:
    js = js.replace(target_nc, replace_nc, 1)
    print("Confirmación agregada a guardarNuevaCuentaCorreo")
else:
    print("Aviso: No se encontró target_nc")

# 3. Eliminar la llamada a renderizarTablaCotizacionesPresupuesto si existe en cargarConfiguracionesJefatura
target_render_cots = "renderizarTablaCotizacionesPresupuesto(window._cotizacionesPresupuestoGlobal);"
if target_render_cots in js:
    js = js.replace(target_render_cots, "// renderizarTablaCotizacionesPresupuesto removida", 1)
    print("renderizarTablaCotizacionesPresupuesto desactivada con éxito")

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("static/configuraciones_jefatura.js actualizado completamente!")

