# scratch/fix_chat_avatar_sizing.py
with open("templates/chat_widget.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update CSS
old_css = '''    .chat-contacto-avatar-wrapper {
        position: relative;
        display: inline-block;
        flex-shrink: 0;
    }
    .chat-contacto-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: #112641;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        border: 2px solid #1f395a;
    }'''

new_css = '''    .chat-contacto-avatar-wrapper {
        position: relative;
        display: inline-block;
        flex-shrink: 0;
        width: 44px;
        height: 44px;
    }
    .chat-contacto-avatar {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        max-width: 44px !important;
        max-height: 44px !important;
        border-radius: 50% !important;
        background: #112641;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        border: 2px solid #1f395a;
        overflow: hidden !important;
        flex-shrink: 0;
        position: relative;
        box-sizing: border-box;
    }
    .chat-contacto-avatar img,
    .chat-avatar-img,
    .chat-msg-avatar img,
    .chat-participante-avatar img {
        width: 100% !important;
        height: 100% !important;
        min-width: 100% !important;
        min-height: 100% !important;
        max-width: 100% !important;
        max-height: 100% !important;
        object-fit: cover !important;
        border-radius: 50% !important;
        display: block !important;
        flex-shrink: 0;
    }
    .chat-avatar-fallback {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .chat-msg-avatar {
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        min-height: 34px !important;
        max-width: 34px !important;
        max-height: 34px !important;
        border-radius: 50% !important;
        overflow: hidden !important;
        flex-shrink: 0;
        border: 1.5px solid #1f395a;
        background: #112641;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2px;
        box-sizing: border-box;
    }
    .chat-participante-avatar {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        max-width: 44px !important;
        max-height: 44px !important;
        border-radius: 50% !important;
        overflow: hidden !important;
        border: 1.5px solid #1f395a;
        background: #071526;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
        box-sizing: border-box;
    }'''

assert old_css in code, "old_css not found"
code = code.replace(old_css, new_css, 1)
print("CSS styles replaced successfully")

# 2. Update renderizarContactos: inline styles on img and containers
old_contacto_item = '''            let avatarHtml = '';
            if (c.foto_ruta) {
                avatarHtml = `
                    <img src="${c.foto_ruta}" alt="${escapeHtml(c.nombre)}" class="chat-avatar-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                    <span class="chat-avatar-fallback" style="display:none;">${iconoRol}</span>
                `;
            } else {
                avatarHtml = `<span class="chat-avatar-fallback">${iconoRol}</span>`;
            }

            html += `
                <div class="chat-contacto-item" onclick="abrirConversacionChat('${c.usuario}')">
                    <div class="chat-contacto-avatar-wrapper">
                        <div class="chat-contacto-avatar">
                            ${avatarHtml}
                        </div>
                        <span class="chat-avatar-status-dot ${claseDotAvatar}" title="${textoPresencia}"></span>
                    </div>'''

new_contacto_item = '''            let avatarHtml = '';
            if (c.foto_ruta) {
                avatarHtml = `
                    <img src="${c.foto_ruta}" alt="${escapeHtml(c.nombre)}" class="chat-avatar-img" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; object-fit:cover; border-radius:50%; display:block;" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                    <span class="chat-avatar-fallback" style="display:none; width:44px; height:44px; align-items:center; justify-content:center;">${iconoRol}</span>
                `;
            } else {
                avatarHtml = `<span class="chat-avatar-fallback" style="width:44px; height:44px; display:flex; align-items:center; justify-content:center;">${iconoRol}</span>`;
            }

            html += `
                <div class="chat-contacto-item" onclick="abrirConversacionChat('${c.usuario}')">
                    <div class="chat-contacto-avatar-wrapper" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; flex-shrink:0;">
                        <div class="chat-contacto-avatar" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; border-radius:50%; overflow:hidden; flex-shrink:0;">
                            ${avatarHtml}
                        </div>
                        <span class="chat-avatar-status-dot ${claseDotAvatar}" title="${textoPresencia}"></span>
                    </div>'''

assert old_contacto_item in code, "old_contacto_item not found"
code = code.replace(old_contacto_item, new_contacto_item, 1)
print("renderizarContactos HTML replaced successfully")

# 3. Update actualizarHeaderActivo inline styles
old_header_avatar_js = '''        const avatarEl = document.getElementById('chat-activo-avatar');
        if (avatarEl) {
            const icono = obtenerIconoRol(contacto.rol);
            if (contacto.foto_ruta) {
                avatarEl.innerHTML = `
                    <img src="${contacto.foto_ruta}" alt="${escapeHtml(contacto.nombre)}" class="chat-avatar-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                    <span class="chat-avatar-fallback" style="display:none;">${icono}</span>
                `;
            } else {
                avatarEl.innerHTML = `<span class="chat-avatar-fallback">${icono}</span>`;
            }
        }'''

new_header_avatar_js = '''        const avatarEl = document.getElementById('chat-activo-avatar');
        if (avatarEl) {
            const icono = obtenerIconoRol(contacto.rol);
            if (contacto.foto_ruta) {
                avatarEl.innerHTML = `
                    <img src="${contacto.foto_ruta}" alt="${escapeHtml(contacto.nombre)}" class="chat-avatar-img" style="width:40px; height:40px; min-width:40px; min-height:40px; max-width:40px; max-height:40px; object-fit:cover; border-radius:50%; display:block;" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                    <span class="chat-avatar-fallback" style="display:none; width:40px; height:40px; align-items:center; justify-content:center;">${icono}</span>
                `;
            } else {
                avatarEl.innerHTML = `<span class="chat-avatar-fallback" style="width:40px; height:40px; display:flex; align-items:center; justify-content:center;">${icono}</span>`;
            }
        }'''

assert old_header_avatar_js in code, "old_header_avatar_js not found"
code = code.replace(old_header_avatar_js, new_header_avatar_js, 1)
print("actualizarHeaderActivo JS replaced successfully")

# 4. Update renderizarMensajes inline styles
old_msg_avatar_js = '''                const iconoRemoto = obtenerIconoRol(m.emisor_rol);
                let avatarRemotoHtml = '';
                if (m.emisor_foto) {
                    avatarRemotoHtml = `
                        <img src="${m.emisor_foto}" alt="${escapeHtml(m.emisor_nombre)}" class="chat-avatar-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                        <span class="chat-avatar-fallback" style="display:none; font-size:0.85rem;">${iconoRemoto}</span>
                    `;
                } else {
                    avatarRemotoHtml = `<span class="chat-avatar-fallback" style="font-size:0.85rem;">${iconoRemoto}</span>`;
                }

                html += `
                    <div class="chat-mensaje-wrapper remoto" id="msg-wrapper-${m.id}">
                        ${barraAcciones}
                        <div style="display:flex; align-items:flex-end; gap:8px; width:100%;">
                            <div class="chat-msg-avatar" title="${escapeHtml(m.emisor_nombre || '')}">
                                ${avatarRemotoHtml}
                            </div>'''

new_msg_avatar_js = '''                const iconoRemoto = obtenerIconoRol(m.emisor_rol);
                let avatarRemotoHtml = '';
                if (m.emisor_foto) {
                    avatarRemotoHtml = `
                        <img src="${m.emisor_foto}" alt="${escapeHtml(m.emisor_nombre)}" class="chat-avatar-img" style="width:34px; height:34px; min-width:34px; min-height:34px; max-width:34px; max-height:34px; object-fit:cover; border-radius:50%; display:block;" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                        <span class="chat-avatar-fallback" style="display:none; font-size:0.85rem; width:34px; height:34px; align-items:center; justify-content:center;">${iconoRemoto}</span>
                    `;
                } else {
                    avatarRemotoHtml = `<span class="chat-avatar-fallback" style="font-size:0.85rem; width:34px; height:34px; display:flex; align-items:center; justify-content:center;">${iconoRemoto}</span>`;
                }

                html += `
                    <div class="chat-mensaje-wrapper remoto" id="msg-wrapper-${m.id}">
                        ${barraAcciones}
                        <div style="display:flex; align-items:flex-end; gap:8px; width:100%;">
                            <div class="chat-msg-avatar" style="width:34px; height:34px; min-width:34px; min-height:34px; max-width:34px; max-height:34px; border-radius:50%; overflow:hidden; flex-shrink:0;" title="${escapeHtml(m.emisor_nombre || '')}">
                                ${avatarRemotoHtml}
                            </div>'''

assert old_msg_avatar_js in code, "old_msg_avatar_js not found"
code = code.replace(old_msg_avatar_js, new_msg_avatar_js, 1)
print("renderizarMensajes JS replaced successfully")

# 5. Update verDetallesMensajeChat inline styles
old_details_avatar = '''                        <div class="chat-participante-body">
                            <div class="chat-participante-avatar">
                                ${msg.emisor_foto ? `
                                    <img src="${msg.emisor_foto}" alt="${escapeHtml(msg.emisor_nombre)}" class="chat-avatar-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                                    <span class="chat-avatar-fallback" style="display:none;">${iconoEmisor}</span>
                                ` : `<span class="chat-avatar-fallback">${iconoEmisor}</span>`}
                            </div>
                            <div class="chat-participante-meta">
                                <div class="chat-participante-nombre" title="${escapeHtml(msg.emisor_nombre)}">
                                    ${escapeHtml(msg.emisor_nombre)}
                                </div>
                            </div>
                        </div>
                        <div class="chat-participante-rol-wrap">
                            <span class="chat-contacto-rol-pill pill-rol-${msg.emisor_rol}">${iconoEmisor} ${msg.emisor_rol}</span>
                        </div>
                    </div>

                    <!-- CONECTOR VISUAL ENTRE AMBOS -->
                    <div class="chat-participantes-conector">
                        <span>➔</span>
                    </div>

                    <!-- TARJETA RECEPTOR -->
                    <div class="chat-participante-card receptor">
                        <div class="chat-participante-tag receptor">
                            <span>●</span> Receptor (Recibe)
                        </div>
                        <div class="chat-participante-body">
                            <div class="chat-participante-avatar">
                                ${msg.receptor_foto ? `
                                    <img src="${msg.receptor_foto}" alt="${escapeHtml(msg.receptor_nombre)}" class="chat-avatar-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                                    <span class="chat-avatar-fallback" style="display:none;">${iconoReceptor}</span>
                                ` : `<span class="chat-avatar-fallback">${iconoReceptor}</span>`}
                            </div>'''

new_details_avatar = '''                        <div class="chat-participante-body">
                            <div class="chat-participante-avatar" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; border-radius:50%; overflow:hidden; flex-shrink:0;">
                                ${msg.emisor_foto ? `
                                    <img src="${msg.emisor_foto}" alt="${escapeHtml(msg.emisor_nombre)}" class="chat-avatar-img" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; object-fit:cover; border-radius:50%; display:block;" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                                    <span class="chat-avatar-fallback" style="display:none;">${iconoEmisor}</span>
                                ` : `<span class="chat-avatar-fallback">${iconoEmisor}</span>`}
                            </div>
                            <div class="chat-participante-meta">
                                <div class="chat-participante-nombre" title="${escapeHtml(msg.emisor_nombre)}">
                                    ${escapeHtml(msg.emisor_nombre)}
                                </div>
                            </div>
                        </div>
                        <div class="chat-participante-rol-wrap">
                            <span class="chat-contacto-rol-pill pill-rol-${msg.emisor_rol}">${iconoEmisor} ${msg.emisor_rol}</span>
                        </div>
                    </div>

                    <!-- CONECTOR VISUAL ENTRE AMBOS -->
                    <div class="chat-participantes-conector">
                        <span>➔</span>
                    </div>

                    <!-- TARJETA RECEPTOR -->
                    <div class="chat-participante-card receptor">
                        <div class="chat-participante-tag receptor">
                            <span>●</span> Receptor (Recibe)
                        </div>
                        <div class="chat-participante-body">
                            <div class="chat-participante-avatar" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; border-radius:50%; overflow:hidden; flex-shrink:0;">
                                ${msg.receptor_foto ? `
                                    <img src="${msg.receptor_foto}" alt="${escapeHtml(msg.receptor_nombre)}" class="chat-avatar-img" style="width:44px; height:44px; min-width:44px; min-height:44px; max-width:44px; max-height:44px; object-fit:cover; border-radius:50%; display:block;" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='flex';">
                                    <span class="chat-avatar-fallback" style="display:none;">${iconoReceptor}</span>
                                ` : `<span class="chat-avatar-fallback">${iconoReceptor}</span>`}
                            </div>'''

assert old_details_avatar in code, "old_details_avatar not found"
code = code.replace(old_details_avatar, new_details_avatar, 1)
print("verDetallesMensajeChat avatars replaced successfully")

with open("templates/chat_widget.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Saved templates/chat_widget.html successfully!")

