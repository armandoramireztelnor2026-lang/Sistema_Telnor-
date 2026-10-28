# -*- coding: utf-8 -*-

with open('templates/chat_widget.html', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = """                                <div class="chat-participante-user" title="@${msg.emisor_usuario}">
                                    @${msg.emisor_usuario}
                                </div>"""

target2 = """                                <div class="chat-participante-user" title="@${msg.receptor_usuario}">
                                    @${msg.receptor_usuario}
                                </div>"""

# Try exact match or CRLF match
if target1 in c:
    c = c.replace(target1, '')
    print("OK: Replaced target1")
else:
    c = c.replace(target1.replace('\n', '\r\n'), '')
    print("OK: Replaced target1 (CRLF)")

if target2 in c:
    c = c.replace(target2, '')
    print("OK: Replaced target2")
else:
    c = c.replace(target2.replace('\n', '\r\n'), '')
    print("OK: Replaced target2 (CRLF)")

with open('templates/chat_widget.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Actualización completada en templates/chat_widget.html")

