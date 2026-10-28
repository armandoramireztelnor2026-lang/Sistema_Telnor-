# -*- coding: utf-8 -*-
import sys

print("Applying updates: Larger chat interface and full timestamp (hora, dia, mes, año)...")

# 1. Update rutas_chat.py
with open('rutas_chat.py', 'r', encoding='utf-8') as f:
    chat_py = f.read()

target_hora = '"hora_corta": ahora.strftime("%I:%M %p"),'
new_hora = '"hora_corta": ahora.strftime("%I:%M %p"),\n        "fecha_completa": ahora.strftime("%I:%M %p • %d/%m/%Y"),'

if target_hora in chat_py and '"fecha_completa"' not in chat_py:
    chat_py = chat_py.replace(target_hora, new_hora)
    with open('rutas_chat.py', 'w', encoding='utf-8') as f:
        f.write(chat_py)
    print("Updated rutas_chat.py with fecha_completa.")
else:
    print("rutas_chat.py already updated or target not found.")

# 2. Update templates/chat_widget.html
with open('templates/chat_widget.html', 'r', encoding='utf-8') as f:
    widget_html = f.read()

# Update dimensions in CSS: larger width (480px) and height (660px)
old_dims = """    #chat-flotante-panel {
        position: fixed;
        bottom: 92px;
        right: 24px;
        z-index: 99999;
        width: 390px;
        max-width: calc(100vw - 32px);
        height: 540px;
        max-height: calc(100vh - 120px);"""

new_dims = """    #chat-flotante-panel {
        position: fixed;
        bottom: 92px;
        right: 24px;
        z-index: 99999;
        width: 490px;
        max-width: calc(100vw - 32px);
        height: 660px;
        max-height: calc(100vh - 110px);"""

if old_dims in widget_html:
    widget_html = widget_html.replace(old_dims, new_dims)
    print("Updated dimensions in chat_widget.html.")
else:
    print("Warning: old_dims not found directly.")

# Update .chat-msg-hora styling in CSS to accommodate full timestamp nicely
old_msg_hora_css = """    .chat-msg-hora {
        font-size: 0.65rem;
        margin-top: 4px;
        text-align: right;
        opacity: 0.8;
    }"""

new_msg_hora_css = """    .chat-msg-hora {
        font-size: 0.68rem;
        margin-top: 5px;
        text-align: right;
        opacity: 0.85;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 5px;
        white-space: nowrap;
    }
    .chat-mensaje-globo {
        max-width: 82%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 0.86rem;
        line-height: 1.45;
        position: relative;
        word-break: break-word;
    }"""

if old_msg_hora_css in widget_html:
    widget_html = widget_html.replace(old_msg_hora_css, new_msg_hora_css)
    print("Updated .chat-msg-hora CSS.")

# Update JavaScript to render full timestamp: Hora, Día, Mes, Año
js_formatting_fn = """
    function formatearTiempoCompletoChat(m) {
        if (!m) return '';
        if (m.fecha_completa) return m.fecha_completa;
        
        let d = null;
        if (m.fecha) {
            const partes = m.fecha.split(' ');
            if (partes.length === 2) {
                const fPartes = partes[0].split('-');
                const hPartes = partes[1].split(':');
                d = new Date(parseInt(fPartes[0]), parseInt(fPartes[1]) - 1, parseInt(fPartes[2]), parseInt(hPartes[0]), parseInt(hPartes[1]), parseInt(hPartes[2] || 0));
            } else {
                d = new Date(m.fecha);
            }
        } else if (m.timestamp) {
            d = new Date(m.timestamp * 1000);
        }

        if (!d || isNaN(d.getTime())) {
            return m.fecha || m.hora_corta || '';
        }

        const hora = d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true });
        const dia = String(d.getDate()).padStart(2, '0');
        const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        const mes = meses[d.getMonth()];
        const anio = d.getFullYear();

        return `${hora} • ${dia} ${mes} ${anio}`;
    }
"""

if 'function formatearTiempoCompletoChat' not in widget_html:
    widget_html = widget_html.replace('function renderizarMensajes(mensajes, miId) {',
                                      js_formatting_fn + '\n    function renderizarMensajes(mensajes, miId) {')
    print("Added formatearTiempoCompletoChat function.")

# Replace line that assigns const hora in renderizarMensajes
old_hora_line = "const hora = m.hora_corta || (m.fecha ? m.fecha.split(' ')[1]?.slice(0, 5) : '');"
new_hora_line = "const hora = formatearTiempoCompletoChat(m);"

if old_hora_line in widget_html:
    widget_html = widget_html.replace(old_hora_line, new_hora_line)
    print("Replaced hora formatting in renderizarMensajes with full timestamp.")

# Also update existing messages in chat_mensajes.json to have fecha_completa if missing
with open('templates/chat_widget.html', 'w', encoding='utf-8') as f:
    f.write(widget_html)

print("Updated templates/chat_widget.html successfully.")

