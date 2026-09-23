import os
import re

file_path = r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\rutas_facturas.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_helper = """def obtener_ciudad_de_factura(f):
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

    unidad = str(f.get("unidad", ""))
    unidad_corta = unidad.replace("8090-", "")
    
    reportes = leer_json("reportes.json").get("reportes", [])
    for r in reversed(reportes):
        r_uni = str(r.get("unidad", ""))
        if r_uni == unidad_corta or f"8090-{r_uni}" == unidad:
            if r.get("ciudad"):
                return r.get("ciudad")

    if os.path.exists("archivo_reportes.json"):
        archivos = leer_json("archivo_reportes.json").get("reportes", [])
        for r in reversed(archivos):
            r_uni = str(r.get("unidad", ""))
            if r_uni == unidad_corta or f"8090-{r_uni}" == unidad:
                if r.get("ciudad"):
                    return r.get("ciudad")

    return unidad"""

# Encontrar el helper viejo y reemplazarlo
pattern = r"def obtener_ciudad_de_factura\(f\):.*?return f\.get\(\"unidad\", \"\"\)"
content = re.sub(pattern, new_helper, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Parche mejorado aplicado exitosamente.")
