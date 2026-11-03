import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('window.cambiarTabConfiguracion = function')
print(js[pos:pos+1500])

