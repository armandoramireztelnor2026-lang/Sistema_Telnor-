# -*- coding: utf-8 -*-

with open("rutas_reportes.py", "r", encoding="utf-8") as f:
    content = f.read()

is_crlf = "\r\n" in content
norm = content.replace("\r\n", "\n")

target_block = """    # 2. Al Taller confirmando la conclusión
    correo_taller = dp.get("correo") or session["usuario"].get("correo")
    if not correo_taller:
        usuarios_data = leer_json("usuarios.json")
        for u in usuarios_data.get("usuarios", []):
            if u.get("usuario") == session["usuario"].get("usuario"):
                correo_taller = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                break
    if not correo_taller:
        correo_taller = "armandoramireztelnor2026@gmail.com"

    try:
        enviar_correo_retrabajo_listo_taller(
            correo_taller=correo_taller,
            nombre_taller=taller_nombre,
            ticket=ticket_display,
            unidad=unidad_str,
            nombre_chofer=nombre_chofer
        )
    except Exception as e:
        print(f"Error al enviar correo de confirmación de retrabajo listo al taller: {e}")

    # 3. Al Supervisor de respaldo con su código de respaldo"""

replacement_block = """    # 2. Al Supervisor de respaldo con su código de respaldo"""

assert target_block in norm, "target_block not found in rutas_reportes.py"
norm = norm.replace(target_block, replacement_block, 1)

final = norm.replace("\n", "\r\n") if is_crlf else norm
with open("rutas_reportes.py", "w", encoding="utf-8") as f:
    f.write(final)

print("rutas_reportes.py updated: correo al taller removido.")

