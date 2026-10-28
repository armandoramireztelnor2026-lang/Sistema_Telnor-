# -*- coding: utf-8 -*-
import sys

templates = [
    'templates/administracion.html',
    'templates/proveedores.html',
    'templates/corporativos.html'
]

include_tag = "{% include 'chat_widget.html' %}\n</body>"

for t_path in templates:
    with open(t_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'chat_widget.html' not in content:
        if '</body>' in content:
            content = content.replace('</body>', include_tag)
            with open(t_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Included chat_widget.html in {t_path}")
        else:
            print(f"Warning: </body> not found in {t_path}")
    else:
        print(f"chat_widget.html already included in {t_path}")

print("Templates update complete.")

