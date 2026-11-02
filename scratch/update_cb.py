with open('templates/administracion.html', 'r', encoding='utf-8', newline='') as f:
    text = f.read()

assert 'href="/static/style.css?v=1000045"' in text
assert 'src="/static/script.js?v=1000050"' in text
assert 'src="/static/seccion_reportes.js?v=1000030"' in text

text = text.replace('href="/static/style.css?v=1000045"', 'href="/static/style.css?v=1000046"')
text = text.replace('src="/static/script.js?v=1000050"', 'src="/static/script.js?v=1000051"')
text = text.replace('src="/static/seccion_reportes.js?v=1000030"', 'src="/static/seccion_reportes.js?v=1000031"')

with open('templates/administracion.html', 'w', encoding='utf-8', newline='') as f:
    f.write(text)

print('Updated templates/administracion.html cache busters successfully')

