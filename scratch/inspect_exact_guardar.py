with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos1 = js.find('window.guardarCorreoEmisor')
print("guardarCorreoEmisor:\n", repr(js[pos1:pos1+300]))

pos2 = js.find('window.guardarNuevaCuentaCorreo')
print("\nguardarNuevaCuentaCorreo:\n", repr(js[pos2:pos2+300]))

