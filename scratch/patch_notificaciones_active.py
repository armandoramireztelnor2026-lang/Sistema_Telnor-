import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('notificaciones.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update obtener_credenciales_correo
old_creds = """            with open(conf_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
                correo = str(conf.get("correo_emisor", "")).strip()
                codigo = str(conf.get("codigo_emisor", "")).strip()
                server = str(conf.get("servidor_smtp", "")).strip() or "smtp.gmail.com"
                port = int(conf.get("puerto_smtp", 587) or 587)
                if correo and codigo:
                    return correo, codigo, server, port"""

new_creds = """            with open(conf_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
                if conf.get("envio_automatico_activo") is False:
                    return None, None, None, None
                correo = str(conf.get("correo_emisor", "")).strip()
                codigo = str(conf.get("codigo_emisor", "")).strip()
                server = str(conf.get("servidor_smtp", "")).strip() or "smtp.gmail.com"
                port = int(conf.get("puerto_smtp", 587) or 587)
                if correo and codigo:
                    return correo, codigo, server, port
                return None, None, None, None"""

if old_creds in code:
    code = code.replace(old_creds, new_creds, 1)
    print("obtener_credenciales_correo actualizada con chequeo de envio_automatico_activo")

# 2. Update enviar_correo_generico
old_enviar = """    remitente_act, clave_act, host_smtp_act, puerto_smtp_act = obtener_credenciales_correo()

    msg = MIMEMultipart()"""

new_enviar = """    remitente_act, clave_act, host_smtp_act, puerto_smtp_act = obtener_credenciales_correo()
    if not remitente_act or not clave_act:
        print(f"Aviso: Envíos automáticos de correo desactivados por Jefatura. Correo a {destino} omitido.")
        return False, "Envíos automáticos desactivados por Jefatura"

    msg = MIMEMultipart()"""

if old_enviar in code:
    code = code.replace(old_enviar, new_enviar, 1)
    print("enviar_correo_generico actualizada con protección si envíos automáticos están desactivados")

with open('notificaciones.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("notificaciones.py guardado con éxito!")

