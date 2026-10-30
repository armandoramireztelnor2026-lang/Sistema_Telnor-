with open('static/unidades.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update metrics setting
target_metrics = """            setTxt('metrica-taller-unidades', t.taller);
            setTxt('porcentaje-taller-unidades', p.taller + '%');"""

new_metrics = """            setTxt('metrica-taller-unidades', t.taller);
            setTxt('porcentaje-taller-unidades', p.taller + '%');
            setTxt('metrica-garantia-unidades', t.garantia !== undefined ? t.garantia : 0);
            setTxt('porcentaje-garantia-unidades', (p.garantia !== undefined ? p.garantia : 0) + '%');"""

if target_metrics in content:
    content = content.replace(target_metrics, new_metrics)
    print("Replaced metrics block (LF)")
else:
    tm_crlf = target_metrics.replace('\n', '\r\n')
    nm_crlf = new_metrics.replace('\n', '\r\n')
    if tm_crlf in content:
        content = content.replace(tm_crlf, nm_crlf)
        print("Replaced metrics block (CRLF)")
    else:
        print("Warning: target_metrics not found in unidades.js")

# 2. Update loop variables, badge, and disabled state
target_loop = """            let isInShop = info.activa_en_taller;
            let isJuridico = info.Juridicos === true;
            let est = info.estado_operativo || (isInShop ? 'En Taller' : (isJuridico ? 'En Jurídicos' : (info.Estado === 'Inactiva' ? 'Inhabilitada' : 'En Circulación')));

            let estadoBadge = '';
            if (est === 'En Taller') {
                estadoBadge = '<span class="badge-taller" style="background:#0284c7; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🔧 En Taller</span>';
            } else if (est === 'En Jurídicos') {
                estadoBadge = '<span class="badge-juridicos" style="background:#6d28d9; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⚖️ En Jurídicos</span>';
            } else if (est === 'Inhabilitada') {
                estadoBadge = '<span class="badge-inhabilitada" style="background:#ef4444; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⛔ Inhabilitada (Caras)</span>';
            } else {
                estadoBadge = '<span class="badge-circulacion" style="background:#10b981; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🚗 En Circulación</span>';
            }

            let disabledAttr = (isInShop || isJuridico) ? 'disabled' : '';
            let styleOpacity = (isInShop || isJuridico) ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';
            let tooltip = isInShop ? 'title="Esta unidad tiene un ticket activo y no puede ser modificada"' : (isJuridico ? 'title="Unidad inhabilitada por estar en Jurídicos"' : '');

            let juridicoBtnText = isJuridico ? 'Quitar Jurídicos' : 'Jurídicos';
            let juridicoBtnColor = isJuridico ? '#6d28d9' : '#8b5cf6';

            let juridicoDisabledAttr = isInShop ? 'disabled' : '';
            let juridicoStyleOpacity = isInShop ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';"""

new_loop = """            let isInShop = info.activa_en_taller;
            let isJuridico = info.Juridicos === true;
            let isGarantia = info.activa_en_garantia || info.estado_operativo === 'En Garantía';
            let est = info.estado_operativo || (isGarantia ? 'En Garantía' : (isInShop ? 'En Taller' : (isJuridico ? 'En Jurídicos' : (info.Estado === 'Inactiva' ? 'Inhabilitada' : 'En Circulación'))));

            let estadoBadge = '';
            if (est === 'En Garantía') {
                estadoBadge = '<span class="badge-garantia" style="background:#f59e0b; color:#0f172a; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🛡️ En Garantía</span>';
            } else if (est === 'En Taller') {
                estadoBadge = '<span class="badge-taller" style="background:#0284c7; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🔧 En Taller</span>';
            } else if (est === 'En Jurídicos') {
                estadoBadge = '<span class="badge-juridicos" style="background:#6d28d9; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⚖️ En Jurídicos</span>';
            } else if (est === 'Inhabilitada') {
                estadoBadge = '<span class="badge-inhabilitada" style="background:#ef4444; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">⛔ Inhabilitada (Caras)</span>';
            } else {
                estadoBadge = '<span class="badge-circulacion" style="background:#10b981; color:white; padding:4px 10px; border-radius:6px; font-size:0.82em; font-weight:700; display:inline-flex; align-items:center; gap:5px;">🚗 En Circulación</span>';
            }

            let disabledAttr = (isInShop || isJuridico || isGarantia) ? 'disabled' : '';
            let styleOpacity = (isInShop || isJuridico || isGarantia) ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';
            let tooltip = isGarantia ? 'title="Unidad en proceso de garantía/retrabajo. Acciones bloqueadas hasta que el taller concluya la reparación."' : (isInShop ? 'title="Esta unidad tiene un ticket activo y no puede ser modificada"' : (isJuridico ? 'title="Unidad inhabilitada por estar en Jurídicos"' : ''));

            let juridicoBtnText = isJuridico ? 'Quitar Jurídicos' : 'Jurídicos';
            let juridicoBtnColor = isJuridico ? '#6d28d9' : '#8b5cf6';

            let juridicoDisabledAttr = (isInShop || isGarantia) ? 'disabled' : '';
            let juridicoStyleOpacity = (isInShop || isGarantia) ? 'opacity:0.4; cursor:not-allowed;' : 'cursor:pointer;';"""

if target_loop in content:
    content = content.replace(target_loop, new_loop)
    print("Replaced loop block (LF)")
else:
    tl_crlf = target_loop.replace('\n', '\r\n')
    nl_crlf = new_loop.replace('\n', '\r\n')
    if tl_crlf in content:
        content = content.replace(tl_crlf, nl_crlf)
        print("Replaced loop block (CRLF)")
    else:
        print("Warning: target_loop not found in unidades.js")

# 3. Update mapClase
target_map = """        'En Taller': 'card-taller',
        'En Jurídicos': 'card-juridicos',"""

new_map = """        'En Taller': 'card-taller',
        'En Garantía': 'card-garantia',
        'En Jurídicos': 'card-juridicos',"""

if target_map in content:
    content = content.replace(target_map, new_map)
    print("Replaced mapClase (LF)")
else:
    tmap_crlf = target_map.replace('\n', '\r\n')
    nmap_crlf = new_map.replace('\n', '\r\n')
    if tmap_crlf in content:
        content = content.replace(tmap_crlf, nmap_crlf)
        print("Replaced mapClase (CRLF)")
    else:
        print("Warning: target_map not found in unidades.js")

with open('static/unidades.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/unidades.js successfully")

