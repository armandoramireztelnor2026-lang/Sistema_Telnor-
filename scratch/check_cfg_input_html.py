import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos1 = html.find('id="cfg-codigo-emisor"')
print(html[pos1:pos1+800])
