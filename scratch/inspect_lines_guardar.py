import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'window.guardarCorreoEmisor' in l:
        print("".join(lines[i:i+25]))
    if 'window.guardarNuevaCuentaCorreo' in l:
        print("".join(lines[i:i+25]))

