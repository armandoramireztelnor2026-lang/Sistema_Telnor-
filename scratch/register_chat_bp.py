# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'from rutas_chat import chat_bp' not in text:
    target_import = 'from rutas_analitica import analitica_bp'
    new_import = 'from rutas_analitica import analitica_bp\nfrom rutas_chat import chat_bp'
    text = text.replace(target_import, new_import)

if 'app.register_blueprint(chat_bp)' not in text:
    target_reg = 'app.register_blueprint(analitica_bp)'
    new_reg = 'app.register_blueprint(analitica_bp)\napp.register_blueprint(chat_bp)'
    text = text.replace(target_reg, new_reg)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Registered chat_bp in app.py successfully.")

