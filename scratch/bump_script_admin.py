with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('src="/static/script.js?v=1000029"', 'src="/static/script.js?v=1000040"')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped script.js version in administracion.html to 1000040")

