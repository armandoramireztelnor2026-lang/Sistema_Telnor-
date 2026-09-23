import os
import re

file_path = r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\rutas_facturas.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

helper = """
def obtener_ciudad_de_factura(f):
    c = f.get("ciudad")
    if c and c.strip():
        return c
    prov_nombre = f.get("proveedor")
    if prov_nombre:
        usuarios = leer_json("usuarios.json")
        for u in usuarios.get("usuarios", []):
            if u.get("rol") == "proveedores" and u.get("datos_perfil", {}).get("nombre_proveedor") == prov_nombre:
                c_prov = u.get("datos_perfil", {}).get("ciudad")
                if c_prov:
                    return c_prov
    return f.get("unidad", "")

"""

# Insert the helper before encontrar_admin_por_ciudad if not exists
if "def obtener_ciudad_de_factura" not in content:
    content = content.replace('def encontrar_admin_por_ciudad(ciudad):', helper + 'def encontrar_admin_por_ciudad(ciudad):')

# Replace exact strings
content = content.replace('f.get("ciudad", f.get("unidad"))', 'obtener_ciudad_de_factura(f)')
content = content.replace("f.get('ciudad', f.get('unidad'))", 'obtener_ciudad_de_factura(f)')

content = content.replace('factura.get("ciudad", factura.get("unidad"))', 'obtener_ciudad_de_factura(factura)')
content = content.replace("factura.get('ciudad', factura.get('unidad'))", 'obtener_ciudad_de_factura(factura)')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Parche aplicado exitosamente.")
