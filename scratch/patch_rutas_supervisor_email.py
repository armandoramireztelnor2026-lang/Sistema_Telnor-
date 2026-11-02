with open('rutas_reportes.py', 'r', encoding='utf-8', newline='') as f:
    text = f.read()

old = '''    # 2. Al Supervisor de respaldo con su código de respaldo
    correo_supervisor = encontrado.get("supervisor_correo")
    nombre_supervisor = encontrado.get("supervisor_asignado") or "Supervisor"
    if not correo_supervisor:
        usuarios_data = leer_json("usuarios.json")
        sup_target = encontrado.get("supervisor_usuario")
        for u in usuarios_data.get("usuarios", []):
            if (sup_target and u.get("usuario") == sup_target) or (u.get("rol") == "administracion" and u.get("datos_perfil", {}).get("subrol") == "Supervisor"):
                correo_supervisor = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                nombre_supervisor = f"{u.get('datos_perfil', {}).get('nombres', '')} {u.get('datos_perfil', {}).get('apellido_paterno', '')}".strip() or nombre_supervisor
                if correo_supervisor:
                    break
    if not correo_supervisor:
        correo_supervisor = "armandoramireztelnor2026@gmail.com"'''

new = '''    # 2. Al Supervisor de respaldo con su código de respaldo
    correo_supervisor = encontrado.get("supervisor_correo")
    nombre_supervisor = encontrado.get("supervisor_asignado") or "Supervisor"
    if not correo_supervisor or "@telnor.com" in str(correo_supervisor).lower():
        usuarios_data = leer_json("usuarios.json")
        sup_target = encontrado.get("supervisor_usuario")
        for u in usuarios_data.get("usuarios", []):
            if (sup_target and u.get("usuario") == sup_target) or (u.get("rol") == "administracion" and u.get("datos_perfil", {}).get("subrol") == "Supervisor"):
                posible_correo = u.get("datos_perfil", {}).get("correo") or u.get("correo")
                if posible_correo and "@telnor.com" not in str(posible_correo).lower():
                    correo_supervisor = posible_correo
                    nombre_supervisor = f"{u.get('datos_perfil', {}).get('nombres', '')} {u.get('datos_perfil', {}).get('apellido_paterno', '')}".strip() or nombre_supervisor
                    break
    if not correo_supervisor or "@telnor.com" in str(correo_supervisor).lower():
        correo_supervisor = "armandoramireztelnor2026@gmail.com"'''

old_target = old.replace('\n', '\r\n') if '\r\n' in text else old
new_target = new.replace('\n', '\r\n') if '\r\n' in text else new

assert old_target in text, 'old text not found in rutas_reportes.py'
text = text.replace(old_target, new_target, 1)

with open('rutas_reportes.py', 'w', encoding='utf-8', newline='') as f:
    f.write(text)

print('Updated rutas_reportes.py successfully')

