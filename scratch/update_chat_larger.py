# -*- coding: utf-8 -*-
with open('templates/chat_widget.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update dimensions to 720px wide and 780px tall
old_dims = """    #chat-flotante-panel {
        position: fixed;
        bottom: 92px;
        right: 24px;
        z-index: 99999;
        width: 600px;
        max-width: calc(100vw - 32px);
        height: 660px;
        max-height: calc(100vh - 110px);"""

new_dims = """    #chat-flotante-panel {
        position: fixed;
        bottom: 92px;
        right: 24px;
        z-index: 99999;
        width: 720px;
        max-width: calc(100vw - 32px);
        height: 780px;
        max-height: calc(100vh - 105px);"""

if old_dims in html:
    html = html.replace(old_dims, new_dims)
    print("Updated dimensions to 720px width and 780px height.")
else:
    print("Warning: old_dims not found directly.")

# Improve input and bubble sizing for the generous format
old_footer = """    .chat-footer-input {
        background: #0b1c30;
        border-top: 1px solid #1f395a;
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
    }
    .chat-input-texto {
        flex: 1;
        background: #06111f;
        border: 1px solid #1f395a;
        border-radius: 20px;
        padding: 8px 14px;
        color: #ffffff;
        font-size: 0.84rem;
        outline: none;
        box-sizing: border-box;
    }
    .chat-input-texto:focus {
        border-color: #38bdf8;
    }
    .chat-btn-enviar {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border: none;
        color: #ffffff;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        cursor: pointer;
        transition: transform 0.2s, background 0.2s;
        flex-shrink: 0;
    }"""

new_footer = """    .chat-footer-input {
        background: #0b1c30;
        border-top: 1px solid #1f395a;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }
    .chat-input-texto {
        flex: 1;
        background: #06111f;
        border: 1.5px solid #1f395a;
        border-radius: 24px;
        padding: 11px 18px;
        color: #ffffff;
        font-size: 0.9rem;
        outline: none;
        box-sizing: border-box;
    }
    .chat-input-texto:focus {
        border-color: #38bdf8;
    }
    .chat-btn-enviar {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border: none;
        color: #ffffff;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        cursor: pointer;
        transition: transform 0.2s, background 0.2s;
        flex-shrink: 0;
    }"""

if old_footer in html:
    html = html.replace(old_footer, new_footer)
    print("Updated footer and input sizing.")

with open('templates/chat_widget.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved templates/chat_widget.html.")

