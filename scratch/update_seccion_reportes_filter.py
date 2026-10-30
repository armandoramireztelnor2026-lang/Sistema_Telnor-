# -*- coding: utf-8 -*-
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Row attribute data-retrabajo
target1 = """        let badgeColorEstado = '#0ea5e9';
        let textColorEstado = 'white';
        if (estado === 'En Asignacion/Retrabajo') {
            badgeColorEstado = '#eab308';
            textColorEstado = '#0b1c30';
        } else if (estado === 'Retrabajo') {
            badgeColorEstado = '#ef4444';
            textColorEstado = 'white';
        }

        let rowHtml = `
            <tr data-ticket="${ticket}" data-eco="${cleanEco}" data-prov="${cleanProv}" data-ciudad="${cleanCiudad}" data-cope="${cleanCope}" data-estado="${estado}" data-fecha="${fechaISO}" data-costo="${ticketGasto}" data-pend-doc50="${isRowPendDoc50 ? '1' : '0'}" data-pend-oc="${isRowPendOC ? '1' : '0'}" data-reactivado="${f.reactivado_desde_caras ? '1' : '0'}">"""

repl1 = """        let badgeColorEstado = '#0ea5e9';
        let textColorEstado = 'white';
        if (estado === 'En Asignacion/Retrabajo') {
            badgeColorEstado = '#eab308';
            textColorEstado = '#0b1c30';
        } else if (estado === 'Retrabajo') {
            badgeColorEstado = '#ef4444';
            textColorEstado = 'white';
        }

        // Evaluar si el ticket está o estuvo en garantía/retrabajo
        let rawRetLower = rawRetrabajo.toLowerCase();
        let estRowLower = String(estado || f.estado || '').toLowerCase();
        let isRowRetrabajo = false;
        if (numRet > 0 ||
            rawRetLower === 'sí' || rawRetLower === 'si' || rawRetLower === 'pendiente' || rawRetLower === 'reasignado' ||
            estRowLower === 'retrabajo' || estRowLower === 'en asignacion/retrabajo' ||
            rawEstRet === 'reasignado' || rawEstRet === 'pendiente' || rawEstRet === 'finalizado' ||
            Boolean(fechaRetRaw) || tieneReingreso) {
            if (rawRetLower !== 'cancelado' || numRet > 0) {
                isRowRetrabajo = true;
            }
        }

        let rowHtml = `
            <tr data-ticket="${ticket}" data-eco="${cleanEco}" data-prov="${cleanProv}" data-ciudad="${cleanCiudad}" data-cope="${cleanCope}" data-estado="${estado}" data-fecha="${fechaISO}" data-costo="${ticketGasto}" data-pend-doc50="${isRowPendDoc50 ? '1' : '0'}" data-pend-oc="${isRowPendOC ? '1' : '0'}" data-reactivado="${f.reactivado_desde_caras ? '1' : '0'}" data-retrabajo="${isRowRetrabajo ? '1' : '0'}">"""

# 2. Filter condition 7
target2 = """        // 6. Filtro Reactivadas de Cotizaciones Caras (botón toggle)
        if (match && window.filtroReactivadasCarasActivo) {
            let esReactivado = tr.getAttribute('data-reactivado') === '1';
            if (!esReactivado) {
                match = false;
            }
        }"""

repl2 = """        // 6. Filtro Reactivadas de Cotizaciones Caras (botón toggle)
        if (match && window.filtroReactivadasCarasActivo) {
            let esReactivado = tr.getAttribute('data-reactivado') === '1';
            if (!esReactivado) {
                match = false;
            }
        }

        // 7. Filtro Garantía / Retrabajo (botón toggle)
        if (match && window.filtroGarantiaRetrabajoActivo) {
            let esRetrabajo = tr.getAttribute('data-retrabajo') === '1';
            if (!esRetrabajo) {
                match = false;
            }
        }"""

# 3. Toggle function and global var
target3 = """window.filtroReactivadasCarasActivo = false;

function toggleFiltroReactivadas() {"""

repl3 = """window.filtroReactivadasCarasActivo = false;
window.filtroGarantiaRetrabajoActivo = false;

function toggleFiltroGarantia() {
    window.filtroGarantiaRetrabajoActivo = !window.filtroGarantiaRetrabajoActivo;
    let btn = document.getElementById('btn-filtro-garantia');
    if (btn) {
        if (window.filtroGarantiaRetrabajoActivo) {
            btn.style.background = '#f59e0b';
            btn.style.color = '#0f172a';
            btn.style.borderColor = '#d97706';
            btn.style.boxShadow = '0 0 10px rgba(245, 158, 11, 0.4)';
            btn.innerHTML = '<span style="font-size:1.1em;">🛡️</span> Garantía / Retrabajo';
        } else {
            btn.style.background = '#334155';
            btn.style.color = '#cbd5e1';
            btn.style.borderColor = '#475569';
            btn.style.boxShadow = 'none';
            btn.innerHTML = '<span style="font-size:1.1em;">🛡️</span> Garantía / Retrabajo';
        }
    }
    aplicarFiltrosReportes();
}

function toggleFiltroReactivadas() {"""

# 4. Limpiar filtros
target4 = """    window.filtroReactivadasCarasActivo = false;
    let btn = document.getElementById('btn-filtro-reactivadas');
    if (btn) {
        btn.style.background = '#334155';
        btn.style.color = '#cbd5e1';
        btn.style.borderColor = '#475569';
        btn.style.boxShadow = 'none';
        btn.innerHTML = '<span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras';
    }"""

repl4 = """    window.filtroReactivadasCarasActivo = false;
    let btn = document.getElementById('btn-filtro-reactivadas');
    if (btn) {
        btn.style.background = '#334155';
        btn.style.color = '#cbd5e1';
        btn.style.borderColor = '#475569';
        btn.style.boxShadow = 'none';
        btn.innerHTML = '<span style="font-size:1.1em;">⚠️</span> Reactivadas C/Caras';
    }

    window.filtroGarantiaRetrabajoActivo = false;
    let btnGar = document.getElementById('btn-filtro-garantia');
    if (btnGar) {
        btnGar.style.background = '#334155';
        btnGar.style.color = '#cbd5e1';
        btnGar.style.borderColor = '#475569';
        btnGar.style.boxShadow = 'none';
        btnGar.innerHTML = '<span style="font-size:1.1em;">🛡️</span> Garantía / Retrabajo';
    }"""

# Normalize CRLF for matching
is_crlf = '\r\n' in text
text_norm = text.replace('\r\n', '\n')

def do_replace(content, t, r, name):
    t_n = t.replace('\r\n', '\n')
    r_n = r.replace('\r\n', '\n')
    if t_n in content:
        print(f"Match found for {name}")
        return content.replace(t_n, r_n, 1)
    else:
        print(f"FAILED to match {name}")
        return content

text_norm = do_replace(text_norm, target1, repl1, "Step 1: data-retrabajo")
text_norm = do_replace(text_norm, target2, repl2, "Step 2: filter condition 7")
text_norm = do_replace(text_norm, target3, repl3, "Step 3: toggle function")
text_norm = do_replace(text_norm, target4, repl4, "Step 4: limpiar filtros")

if is_crlf:
    final_text = text_norm.replace('\n', '\r\n')
else:
    final_text = text_norm

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(final_text)

print("Done writing static/seccion_reportes.js")

