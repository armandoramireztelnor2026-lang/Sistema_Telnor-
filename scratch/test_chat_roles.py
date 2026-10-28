# -*- coding: utf-8 -*-
import json

with open('usuarios.json', 'r', encoding='utf-8') as f:
    users = json.load(f).get('usuarios', [])

def obtener_rol_chat(usuario_obj):
    if not usuario_obj: return None
    rol = usuario_obj.get('rol', '')
    if rol == 'proveedores': return 'Taller'
    if rol == 'corporativos': return 'Corporativos'
    if rol == 'administracion':
        subrol = usuario_obj.get('datos_perfil', {}).get('subrol', '')
        if subrol in ['Supervisor', 'Administrador', 'Jefatura']: return subrol
        return 'Administrador'
    return rol

def obtener_nombre_chat(usuario_obj):
    dp = usuario_obj.get('datos_perfil', {})
    if usuario_obj.get('rol') == 'proveedores':
        return dp.get('nombre_proveedor') or dp.get('encargado') or usuario_obj.get('usuario')
    nombres = (dp.get('nombres') or '').strip()
    apellido = (dp.get('apellido_paterno') or '').strip()
    if nombres or apellido:
        return f"{nombres} {apellido}".strip()
    return usuario_obj.get('usuario', 'Usuario')

print(f"{'ROL CHAT':15} | {'NOMBRE CHAT':35} | USUARIO")
print("-" * 80)
for u in users:
    r_chat = obtener_rol_chat(u)
    n_chat = obtener_nombre_chat(u)
    u_id = u.get('usuario')
    print(f"{r_chat:15} | {n_chat:35} | {u_id}")

# Permisos de mensajeria segun el usuario:
MATRIZ_CHAT_PERMISOS = {
    'Taller': ['Supervisor'],
    'Supervisor': ['Taller', 'Administrador', 'Jefatura', 'Corporativos'],
    'Corporativos': ['Supervisor'],
    'Jefatura': ['Taller', 'Supervisor', 'Administrador', 'Corporativos', 'Jefatura'],
    'Administrador': ['Supervisor', 'Jefatura']
}

print("\n--- PRUEBA DE CONTACTOS PERMITIDOS POR CADA ROL ---")
for rol_origen, permitidos in MATRIZ_CHAT_PERMISOS.items():
    contactos = [obtener_nombre_chat(u) for u in users if obtener_rol_chat(u) in permitidos]
    print(f"\n{rol_origen} puede enviar mensajes a ({len(contactos)} contactos en los roles {permitidos}):")
    for c in contactos[:3]:
        print(f"   • {c}")
    if len(contactos) > 3:
        print(f"   ... y {len(contactos)-3} más")

