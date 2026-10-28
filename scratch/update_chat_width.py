# -*- coding: utf-8 -*-
with open('templates/chat_widget.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = "width: 490px;"
replacement = "width: 600px;"

if target in html:
    html = html.replace(target, replacement)
    with open('templates/chat_widget.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated width to 600px in templates/chat_widget.html.")
else:
    print("Target width: 490px; not found.")

