# -*- coding: utf-8 -*-

with open('static/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = "window.marcarRetrabajoFinalizado = async function(ticketId) {"
if target not in code:
    print("ERROR: Target marker not found in static/script.js")
    import sys; sys.exit(1)

# Find the end of marcarRetrabajoFinalizado
marker = "function abrirModalDetalles(identificador) {"
if marker not in code:
    print("ERROR: marker abrirModalDetalles not found")
    import sys; sys.exit(1)

jefatura_js = """
window.cargarTiempoGarantiaJefatura = async function() {
    const tbody = document.getElementById('tabla-tiempo-garantia');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#94a3b8;">Cargando tiempos de garantía de talleres...</td></tr>';

    try {
        const res = await fetch('/api/garantia/talleres_tiempo');
        const data = await res.json();
        const talleres = data.talleres || [];
        window.talleresTiempoGarantiaGlobal = talleres;

        if (talleres.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:25px; color:#94a3b8;">No se encontraron talleres registrados.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        talleres.forEach(t => {
            const logoImg = t.foto_ruta ? `<img src="${t.foto_ruta}" class="mini-profile-pic" onerror="this.src='https://via.placeholder.com/40/112641/40916c?text=T'">` : `<div class="mini-profile-pic" style="display:flex;align-items:center;justify-content:center;background:#112641;color:#10b981;font-weight:bold;">T</div>`;

            const ciudadCope = t.ciudad ? `${t.ciudad} <br><small style="color:#f59e0b;">${t.cope || ''}</small>` : 'No especificada';
            const contacto = `${t.telefono || 'N/A'}<br><small style="color:#94a3b8;">${t.correo || 'N/A'}</small>`;

            tbody.innerHTML += `
                <tr>
                    <td style="text-align:center;">${logoImg}</td>
                    <td><strong>${escapeHtml(t.nombre_proveedor)}</strong><br><small style="color:#64748b;">${escapeHtml(t.usuario)}</small></td>
                    <td>${escapeHtml(t.encargado)}</td>
                    <td>${contacto}</td>
                    <td><span style="color:#0ea5e9; font-weight:bold;">${ciudadCope}</span></td>
                    <td>
                        <span style="background: rgba(16, 185, 129, 0.18); border: 1px solid #10b981; color: #34d399; font-weight: 700; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 5px;">
                            ⏱️ ${t.tiempo_formateado}
                        </span>
                    </td>
                    <td><span style="color:#94a3b8; font-size:0.78rem;">${t.fecha_actualizacion || 'Predefinido (30 días)'}</span></td>
                    <td>
                        <button class="btn-success" style="background-color: #0284c7; padding: 6px 14px; font-size: 0.82rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px;" onclick="abrirModalAjustarGarantiaJefatura('${t.usuario}', '${escapeHtml(t.nombre_proveedor).replace(/'/g, "\\\\'")}', ${t.dias_garantia}, ${t.horas_garantia}, ${t.minutos_garantia}, ${t.segundos_garantia})">
                            ⚙️ Ajustar Tiempo
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error('Error al cargar tiempos de garantía de talleres:', err);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#ef4444;">Error al cargar la información de garantías.</td></tr>';
    }
};

window.abrirModalAjustarGarantiaJefatura = function(usuario, nombre, d, h, m, s) {
    if (document.getElementById('ajuste-taller-usuario')) document.getElementById('ajuste-taller-usuario').value = usuario;
    if (document.getElementById('ajuste-taller-nombre')) document.getElementById('ajuste-taller-nombre').innerText = nombre;
    if (document.getElementById('ajuste-taller-dias')) document.getElementById('ajuste-taller-dias').value = d !== undefined ? d : 30;
    if (document.getElementById('ajuste-taller-horas')) document.getElementById('ajuste-taller-horas').value = h !== undefined ? h : 0;
    if (document.getElementById('ajuste-taller-minutos')) document.getElementById('ajuste-taller-minutos').value = m !== undefined ? m : 0;
    if (document.getElementById('ajuste-taller-segundos')) document.getElementById('ajuste-taller-segundos').value = s !== undefined ? s : 0;
    actualizarPreviewAjusteJefatura();
    const modal = document.getElementById('modal-ajustar-garantia-jefatura');
    if (modal) modal.style.display = 'flex';
};

window.actualizarPreviewAjusteJefatura = function() {
    const d = parseInt(document.getElementById('ajuste-taller-dias')?.value || 0) || 0;
    const h = parseInt(document.getElementById('ajuste-taller-horas')?.value || 0) || 0;
    const m = parseInt(document.getElementById('ajuste-taller-minutos')?.value || 0) || 0;
    const s = parseInt(document.getElementById('ajuste-taller-segundos')?.value || 0) || 0;

    const tot = d * 86400 + h * 3600 + m * 60 + s;
    const el = document.getElementById('ajuste-taller-preview');
    if (!el) return;

    if (tot <= 0) {
        el.innerText = '⚠️ Tiempo total: 0 seg (Inválido - mínimo debe ser mayor a 0)';
        el.style.color = '#f87171';
        el.style.borderColor = '#ef4444';
        return;
    }

    el.style.color = '#34d399';
    el.style.borderColor = '#10b981';
    let partes = [];
    if (d > 0) partes.push(d === 1 ? '1 día' : `${d} días`);
    if (h > 0) partes.push(h === 1 ? '1 hora' : `${h} horas`);
    if (m > 0) partes.push(m === 1 ? '1 min' : `${m} mins`);
    if (s > 0) partes.push(`${s} seg`);

    el.innerText = `Tiempo total configurado: ${partes.join(', ')}`;
};

window.setValoresGarantiaJefatura = function(d, h, m, s) {
    if (document.getElementById('ajuste-taller-dias')) document.getElementById('ajuste-taller-dias').value = d;
    if (document.getElementById('ajuste-taller-horas')) document.getElementById('ajuste-taller-horas').value = h;
    if (document.getElementById('ajuste-taller-minutos')) document.getElementById('ajuste-taller-minutos').value = m;
    if (document.getElementById('ajuste-taller-segundos')) document.getElementById('ajuste-taller-segundos').value = s;
    actualizarPreviewAjusteJefatura();
};

window.guardarAjusteGarantiaJefatura = async function() {
    const usuario = document.getElementById('ajuste-taller-usuario')?.value;
    const d = parseInt(document.getElementById('ajuste-taller-dias')?.value || 0) || 0;
    const h = parseInt(document.getElementById('ajuste-taller-horas')?.value || 0) || 0;
    const m = parseInt(document.getElementById('ajuste-taller-minutos')?.value || 0) || 0;
    const s = parseInt(document.getElementById('ajuste-taller-segundos')?.value || 0) || 0;

    const tot = d * 86400 + h * 3600 + m * 60 + s;
    if (tot <= 0) {
        alert("El tiempo de garantía debe ser mayor a 0 segundos.");
        return;
    }

    try {
        const res = await fetch('/api/garantia/taller/actualizar_dias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario: usuario,
                dias_garantia: d,
                horas_garantia: h,
                minutos_garantia: m,
                segundos_garantia: s
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message || 'Tiempo de garantía actualizado con éxito.');
            cerrarModal('modal-ajustar-garantia-jefatura');
            cargarTiempoGarantiaJefatura();
        } else {
            alert('Error: ' + (data.message || 'No se pudo actualizar'));
        }
    } catch (err) {
        console.error('Error al guardar ajuste de garantía:', err);
        alert('No se pudo conectar con el servidor.');
    }
};

"""

code = code.replace(marker, jefatura_js + "\n" + marker)

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("static/script.js actualizado con funciones de Jefatura para Tiempo/Garantía.")

