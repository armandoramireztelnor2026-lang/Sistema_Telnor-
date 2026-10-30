# scratch/patch_chat_widget_html.py
with open("templates/chat_widget.html", "r", encoding="utf-8") as f:
    code = f.read()

# 2. Update Header of #chat-vista-conversacion to add contact avatar
old_header_markup = '''        <div class="chat-header-bar">
            <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
                <button type="button" class="chat-header-btn" onclick="volverAContactosChat()" title="Volver a contactos" style="padding: 4px 6px; font-size: 1.2rem;">
                    ◀
                </button>
                <div style="min-width: 0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div id="chat-activo-nombre" style="color: #ffffff; font-size: 0.92rem; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            Contacto
                        </div>
                        <span id="chat-activo-rol-pill" class="chat-contacto-rol-pill">Rol</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                        <span id="chat-activo-presencia-badge" class="chat-header-presencia-badge offline">
                            <span id="chat-activo-presencia-dot" class="chat-mini-dot dot-offline">●</span>
                            <span id="chat-activo-presencia-texto">Desconectado</span>
                        </span>
                        <span id="chat-activo-cope" style="color: #64748b; font-size: 0.68rem;"></span>
                    </div>
                </div>
            </div>'''

new_header_markup = '''        <div class="chat-header-bar">
            <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">
                <button type="button" class="chat-header-btn" onclick="volverAContactosChat()" title="Volver a contactos" style="padding: 4px 6px; font-size: 1.2rem;">
                    ◀
                </button>
                <div class="chat-contacto-avatar-wrapper" style="width: 40px; height: 40px; flex-shrink: 0;">
                    <div id="chat-activo-avatar" class="chat-contacto-avatar" style="width: 40px; height: 40px;">
                        👤
                    </div>
                    <span id="chat-activo-avatar-dot" class="chat-avatar-status-dot status-offline"></span>
                </div>
                <div style="min-width: 0; flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div id="chat-activo-nombre" style="color: #ffffff; font-size: 0.95rem; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            Contacto
                        </div>
                        <span id="chat-activo-rol-pill" class="chat-contacto-rol-pill">Rol</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                        <span id="chat-activo-presencia-badge" class="chat-header-presencia-badge offline">
                            <span id="chat-activo-presencia-dot" class="chat-mini-dot dot-offline">●</span>
                            <span id="chat-activo-presencia-texto">Desconectado</span>
                        </span>
                        <span id="chat-activo-cope" style="color: #64748b; font-size: 0.68rem;"></span>
                    </div>
                </div>
            </div>'''

assert old_header_markup in code, "old_header_markup not found"
code = code.replace(old_header_markup, new_header_markup, 1)
print("Header markup updated successfully")

# 3. Update renderizarContactos in JS
old_render_contactos = '''        contactos.forEach(c => {
            const iconoRol = obtenerIconoRol(c.rol);
            const badgeNoLeidos = c.no_leidos > 0 ? `<span class="chat-badge-contacto">${c.no_leidos}</span>` : '';
            const ultimoMsg = c.ultimo_mensaje ? c.ultimo_mensaje : '<span style="color:#64748b; font-style:italic;">Iniciar conversación...</span>';
            const horaMsg = c.hora_corta || '';

            const estaEnLinea = !!c.en_linea;
            const textoPresencia = c.estado_presencia || (estaEnLinea ? 'En línea' : 'Desconectado');
            const claseTextoPres = estaEnLinea ? 'texto-online' : 'texto-offline';
            const claseDotPres = estaEnLinea ? 'dot-online' : 'dot-offline';
            const claseDotAvatar = estaEnLinea ? 'status-online' : 'status-offline';

            html += `
                <div class="chat-contacto-item" onclick="abrirConversacionChat('${c.usuario}')">
                    <div class="chat-contacto-avatar-wrapper">
                        <div class="chat-contacto-avatar">
                            ${iconoRol}
                        </div>
                        <span class="chat-avatar-status-dot ${claseDotAvatar}" title="${textoPresencia}"></span>
                    </div>'''

new_render_contactos = '''        contactos.forEach(c => {
            const iconoRol = obtenerIconoRol(c.rol);
            const badgeNoLeidos = c.no_leidos > 0 ? `<span class="chat-badge-contacto">${c.no_leidos}</span>` : '';
            const ultimoMsg = c.ultimo_mensaje ? c.ultimo_mensaje : '<span style="color:#64748b; font-style:italic;">Iniciar conversación...</span>';
            const horaMsg = c.hora_corta || '';

            const estaEnLinea = !!c.en_linea;
            const textoPresencia = c.estado_presencia || (estaEnLinea ? 'En línea' : 'Desconectado');
            const claseTextoPres = estaEnLinea ? 'texto-online' : 'texto-offline';
            const claseDotPres = estaEnLinea ? 'dot-online' : 'dot-offline';
            const claseDotAvatar = estaEnLinea ? 'status-online' : 'status-offline';

            let avatarHtml = '';
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

assert old_render_contactos in code, "old_render_contactos not found"
code = code.replace(old_render_contactos, new_render_contactos, 1)
print("renderizarContactos updated successfully")

# 4. Add helper actualizarHeaderActivo and update abrirConversacionChat / refrescarConversacionActual
old_abrir_conv = '''    function abrirConversacionChat(contactoId) {
        contactoActivoId = contactoId;
        cancelarRespuestaChat();
        const contacto = chatContactosGlobal.find(c => c.usuario === contactoId);
        
        document.getElementById('chat-vista-contactos').style.display = 'none';
        document.getElementById('chat-vista-conversacion').style.display = 'flex';

        if (contacto) {
            document.getElementById('chat-activo-nombre').innerText = contacto.nombre;
            const rolPill = document.getElementById('chat-activo-rol-pill');
            if (rolPill) {
                rolPill.className = `chat-contacto-rol-pill pill-rol-${contacto.rol}`;
                rolPill.innerText = `${obtenerIconoRol(contacto.rol)} ${contacto.rol}`;
            }
            const copeEl = document.getElementById('chat-activo-cope');
            if (copeEl) copeEl.innerText = contacto.cope ? `(${contacto.cope})` : '';

            // Actualizar presencia inmediata
            actualizarPresenciaHeader(contacto.en_linea, contacto.estado_presencia);
        }

        refrescarConversacionActual();
        setTimeout(() => {
            const inp = document.getElementById('chat-input-mensaje');
            if (inp) inp.focus();
        }, 150);
    }

    function volverAContactosChat() {
        contactoActivoId = null;
        cancelarRespuestaChat();
        document.getElementById('chat-vista-conversacion').style.display = 'none';
        document.getElementById('chat-vista-contactos').style.display = 'flex';
        cargarContactosChat(false);
    }

    function refrescarConversacionActual() {
        if (!contactoActivoId) return;

        fetch(`/api/chat/conversacion/${encodeURIComponent(contactoActivoId)}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    conversacionActualMensajes = data.mensajes || [];
                    renderizarMensajes(conversacionActualMensajes, data.mi_usuario);

                    if (data.contacto) {
                        actualizarPresenciaHeader(data.contacto.en_linea, data.contacto.estado_presencia);
                    }
                }
            })
            .catch(err => console.error("Error al cargar conversación:", err));
    }'''

new_abrir_conv = '''    function actualizarHeaderActivo(contacto) {
        if (!contacto) return;
        const nombreEl = document.getElementById('chat-activo-nombre');
        if (nombreEl) nombreEl.innerText = contacto.nombre;

        const rolPill = document.getElementById('chat-activo-rol-pill');
        if (rolPill) {
            rolPill.className = `chat-contacto-rol-pill pill-rol-${contacto.rol}`;
            rolPill.innerText = `${obtenerIconoRol(contacto.rol)} ${contacto.rol}`;
        }

        const copeEl = document.getElementById('chat-activo-cope');
        if (copeEl) copeEl.innerText = contacto.cope ? `(${contacto.cope})` : '';

        const avatarEl = document.getElementById('chat-activo-avatar');
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
        }

        const dotEl = document.getElementById('chat-activo-avatar-dot');
        if (dotEl) {
            dotEl.className = `chat-avatar-status-dot ${contacto.en_linea ? 'status-online' : 'status-offline'}`;
            dotEl.title = contacto.estado_presencia || (contacto.en_linea ? 'En línea' : 'Desconectado');
        }

        actualizarPresenciaHeader(contacto.en_linea, contacto.estado_presencia);
    }

    function abrirConversacionChat(contactoId) {
        contactoActivoId = contactoId;
        cancelarRespuestaChat();
        const contacto = chatContactosGlobal.find(c => c.usuario === contactoId);
        
        document.getElementById('chat-vista-contactos').style.display = 'none';
        document.getElementById('chat-vista-conversacion').style.display = 'flex';

        if (contacto) {
            actualizarHeaderActivo(contacto);
        }

        refrescarConversacionActual();
        setTimeout(() => {
            const inp = document.getElementById('chat-input-mensaje');
            if (inp) inp.focus();
        }, 150);
    }

    function volverAContactosChat() {
        contactoActivoId = null;
        cancelarRespuestaChat();
        document.getElementById('chat-vista-conversacion').style.display = 'none';
        document.getElementById('chat-vista-contactos').style.display = 'flex';
        cargarContactosChat(false);
    }

    function refrescarConversacionActual() {
        if (!contactoActivoId) return;

        fetch(`/api/chat/conversacion/${encodeURIComponent(contactoActivoId)}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    conversacionActualMensajes = data.mensajes || [];
                    renderizarMensajes(conversacionActualMensajes, data.mi_usuario);

                    if (data.contacto) {
                        actualizarHeaderActivo(data.contacto);
                    }
                }
            })
            .catch(err => console.error("Error al cargar conversación:", err));
    }'''

assert old_abrir_conv in code, "old_abrir_conv not found"
code = code.replace(old_abrir_conv, new_abrir_conv, 1)
print("actualizarHeaderActivo and conv functions updated successfully")

# 5. Update renderizarMensajes to display avatar and current sender name on remote messages
old_render_mensajes = '''            html += `
                <div class="chat-mensaje-wrapper ${esMio ? 'propio' : 'remoto'}" id="msg-wrapper-${m.id}">
                    ${barraAcciones}
                    <div class="chat-mensaje-globo ${clase} ${estaEliminado ? 'chat-msg-eliminado' : ''}" id="msg-elem-${m.id}">
                        ${htmlCita}
                        ${contenidoTexto}
                        <div class="chat-msg-hora">
                            <span>${hora}</span>
                            ${check}
                        </div>
                    </div>
                </div>
            `;'''

new_render_mensajes = '''            if (esMio) {
                html += `
                    <div class="chat-mensaje-wrapper propio" id="msg-wrapper-${m.id}">
                        ${barraAcciones}
                        <div class="chat-mensaje-globo chat-msg-propio ${estaEliminado ? 'chat-msg-eliminado' : ''}" id="msg-elem-${m.id}">
                            ${htmlCita}
                            ${contenidoTexto}
                            <div class="chat-msg-hora">
                                <span>${hora}</span>
                                ${check}
                            </div>
                        </div>
                    </div>
                `;
            } else {
                const iconoRemoto = obtenerIconoRol(m.emisor_rol);
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
                            </div>
                            <div class="chat-mensaje-globo chat-msg-remoto ${estaEliminado ? 'chat-msg-eliminado' : ''}" id="msg-elem-${m.id}">
                                <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; margin-bottom:4px; display:flex; align-items:center; gap:5px;">
                                    <span>${escapeHtml(m.emisor_nombre || 'Usuario')}</span>
                                    <span style="font-size:0.65rem; color:#94a3b8; font-weight:400;">(${m.emisor_rol || ''})</span>
                                </div>
                                ${htmlCita}
                                ${contenidoTexto}
                                <div class="chat-msg-hora">
                                    <span>${hora}</span>
                                    ${check}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }'''

assert old_render_mensajes in code, "old_render_mensajes not found"
code = code.replace(old_render_mensajes, new_render_mensajes, 1)
print("renderizarMensajes updated with avatars and names successfully")

# 6. Update verDetallesMensajeChat to show user profile photos
old_audit_avatars = '''                        <div class="chat-participante-body">
                            <div class="chat-participante-avatar">${iconoEmisor}</div>
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
                            <div class="chat-participante-avatar">${iconoReceptor}</div>'''

new_audit_avatars = '''                        <div class="chat-participante-body">
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

assert old_audit_avatars in code, "old_audit_avatars not found"
code = code.replace(old_audit_avatars, new_audit_avatars, 1)
print("Audit avatars updated successfully")

# 7. Update polling to refresh contacts when panel is open on contacts view
old_polling = '''                    // Si hay conversación abierta, refrescar mensajes
                    const panel = document.getElementById('chat-flotante-panel');
                    if (panel && panel.style.display === 'flex' && contactoActivoId) {
                        refrescarConversacionActual();
                    }'''

new_polling = '''                    // Si el panel de chat está visible, refrescar en vivo
                    const panel = document.getElementById('chat-flotante-panel');
                    if (panel && panel.style.display === 'flex') {
                        if (contactoActivoId) {
                            refrescarConversacionActual();
                        } else {
                            cargarContactosChat(false);
                        }
                    }'''

assert old_polling in code, "old_polling not found"
code = code.replace(old_polling, new_polling, 1)
print("Polling updated successfully")

with open("templates/chat_widget.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Saved templates/chat_widget.html successfully!")
