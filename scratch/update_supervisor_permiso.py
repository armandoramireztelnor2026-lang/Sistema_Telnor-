# -*- coding: utf-8 -*-
with open('rutas_chat.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_matriz = "'Supervisor': ['Taller', 'Administrador', 'Jefatura', 'Corporativos'],"
new_matriz = "'Supervisor': ['Supervisor', 'Taller', 'Administrador', 'Jefatura', 'Corporativos'],"

if old_matriz in text:
    text = text.replace(old_matriz, new_matriz)
    print("OK: Replaced in rutas_chat.py")
else:
    print("ERROR: old_matriz not found")
    import sys; sys.exit(1)

with open('rutas_chat.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Archivo guardado exitosamente.")

