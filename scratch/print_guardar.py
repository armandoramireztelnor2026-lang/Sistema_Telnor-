import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos1 = js.find('window.guardarCorreoEmisor')
print(js[pos1:pos1+600])

pos2 = js.find('window.guardarNuevaCuentaCorreo')
print(js[pos2:pos2+600])
