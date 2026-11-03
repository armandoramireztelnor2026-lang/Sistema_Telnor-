import re

with open('rutas_configuracion.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add es_usuario_autorizado helper
helper_code = """
def es_usuario_autorizado():
    u = session.get("usuario")
    if not isinstance(u, dict):
        return False
    return u.get("rol") == "administracion"
"""

if 'def es_usuario_autorizado():' not in code:
    code = code.replace(
        '# =========================================================================\n# RUTAS DE CONSULTA Y EDICIÓN DE CONFIGURACIÓN',
        helper_code + '\n# =========================================================================\n# RUTAS DE CONSULTA Y EDICIÓN DE CONFIGURACIÓN'
    )

# Replace all if "usuario" not in session or session["usuario"].get("rol") != "administracion":
code = re.sub(
    r'if\s+"usuario"\s+not\s+in\s+session\s+or\s+session\["usuario"\]\.get\("rol"\)\s*!=\s*"administracion":',
    'if not es_usuario_autorizado():',
    code
)

with open('rutas_configuracion.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("rutas_configuracion.py updated with robust es_usuario_autorizado check")

