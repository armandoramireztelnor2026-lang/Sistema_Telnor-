with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

assert '👁' not in js, 'Emoji ojo still in JS'
assert '🙈' not in js, 'Emoji mono still in JS'
assert 'SVG_OJO_ABIERTO' in js, 'SVG_OJO_ABIERTO missing'
assert 'SVG_OJO_CERRADO' in js, 'SVG_OJO_CERRADO missing'

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos1 = html.find('id="cfg-codigo-emisor"')
block1 = html[pos1:pos1+1000]
assert '👁' not in block1, 'Emoji ojo still in cfg-codigo-emisor'
assert '<svg' in block1, 'SVG missing in cfg-codigo-emisor'

pos2 = html.find('id="modal-nueva-cuenta-codigo"')
block2 = html[pos2:pos2+1000]
assert '👁' not in block2, 'Emoji ojo still in modal-nueva-cuenta-codigo'
assert '<svg' in block2, 'SVG missing in modal-nueva-cuenta-codigo'

print('All assertions passed: No emojis in password toggle, clean SVG everywhere!')
