# -*- coding: utf-8 -*-
import sys
import os

def patch_file(filepath, replacements, desc):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    norm = content.replace("\r\n", "\n")

    for target, repl in replacements:
        t_norm = target.replace("\r\n", "\n")
        r_norm = repl.replace("\r\n", "\n")
        if r_norm in norm:
            print(f"ALREADY PATCHED: in {filepath} for {desc}")
            continue
        if t_norm not in norm:
            print(f"ERROR: Target not found in {filepath} for {desc}:\n{t_norm[:100]}...")
            return False
        norm = norm.replace(t_norm, r_norm, 1)

    final = norm.replace("\n", "\r\n") if is_crlf else norm
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final)

    print(f"SUCCESS: {filepath} patched for {desc}")
    return True


# 1. Patch static/script.js
script_replacements = [
    # cargarRetrabajosAdmin
    (
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>''',
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong><br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span></td>'''
    ),
    # cargarRetrabajosProveedor
    (
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #38bdf8;">${fechaReasig}</strong></td>''',
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong><br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span></td>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #38bdf8;">${fechaReasig}</strong></td>'''
    ),
    # cargarLiberarRetrabajosSupervisor
    (
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${fechaReasig}</td>''',
        '''            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong><br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span></td>
                    <td style="white-space: nowrap; vertical-align: middle;">${fechaReasig}</td>'''
    )
]

# 2. Patch static/seccion_reportes.js
seccion_reportes_replacements = [
    (
        '''        // Set row info for filtering
        let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';''',
        '''        // Set row info for filtering
        let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
        let badgeRetrabajo = isRowRetrabajo ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';'''
    ),
    (
        '''<td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px;"><span style="color:#0ea5e9; font-weight:bold;">${ticket}</span>${badgeCaras}</td>''',
        '''<td class="td-azul-marino col-azul-marino" style="vertical-align:top; padding-top:15px;"><span style="color:#0ea5e9; font-weight:bold;">${ticket}</span>${badgeCaras}${badgeRetrabajo}</td>'''
    )
]

# 3. Patch static/facturas_principal.js
facturas_principal_replacements = [
    # Archivo general
    (
        '''                        let idReporteAsociado = obtenerIdReporte(f) || 'N/A';
                        let badgeCarasArch = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        tbodyArchivo.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idReporteAsociado}</span>${badgeCarasArch}</td>''',
        '''                        let idReporteAsociado = obtenerIdReporte(f) || 'N/A';
                        let badgeCarasArch = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let badgeRetrabajoArch = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                        tbodyArchivo.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idReporteAsociado}</span>${badgeCarasArch}${badgeRetrabajoArch}</td>'''
    ),
    # Archivo Prov
    (
        '''                        let idRepArchProv = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasArchProv = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let btnVerExp = `<button class="btn-info" style="display:block; width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoProv.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idRepArchProv}</span>${badgeCarasArchProv}</td>''',
        '''                        let idRepArchProv = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasArchProv = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let badgeRetrabajoArchProv = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                        let btnVerExp = `<button class="btn-info" style="display:block; width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoProv.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idRepArchProv}</span>${badgeCarasArchProv}${badgeRetrabajoArchProv}</td>'''
    ),
    # Archivo Corp
    (
        '''                            let idRepArchCorp = obtenerIdReporte(f) || 'S/T';
                            let badgeCarasArchCorp = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                            let btnVerExp = `<button class="btn-info" style="display:block; width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                            tbodyArchivoCorp.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idRepArchCorp}</span>${badgeCarasArchCorp}</td>''',
        '''                            let idRepArchCorp = obtenerIdReporte(f) || 'S/T';
                            let badgeCarasArchCorp = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                            let badgeRetrabajoArchCorp = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                            let btnVerExp = `<button class="btn-info" style="display:block; width:100%; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                            tbodyArchivoCorp.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#ffffff; font-weight:bold;">${idRepArchCorp}</span>${badgeCarasArchCorp}${badgeRetrabajoArchCorp}</td>'''
    ),
    # tdTicket (Facturas principales)
    (
        '''                let idRepForTable = obtenerIdReporte(f) || 'S/T';
                let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                let tdTicket = `<td><span style="color:#ffffff; font-weight:bold;">${idRepForTable}</span>${badgeCaras}</td>`;''',
        '''                let idRepForTable = obtenerIdReporte(f) || 'S/T';
                let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                let badgeRetrabajo = (enRetrabajoBloqueo || f.estado === 'Retrabajo' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                let tdTicket = `<td><span style="color:#ffffff; font-weight:bold;">${idRepForTable}</span>${badgeCaras}${badgeRetrabajo}</td>`;'''
    ),
    # Doc Contables
    (
        '''                        let idRepTable = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasDoc = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let pFormat = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';

                        tbodyDocContables.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${idRepTable}</span>${badgeCarasDoc}</td>''',
        '''                        let idRepTable = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasDoc = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let badgeRetrabajoDoc = (enRetrabajoBloqueo || f.estado === 'Retrabajo' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                        let pFormat = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';

                        tbodyDocContables.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${idRepTable}</span>${badgeCarasDoc}${badgeRetrabajoDoc}</td>'''
    ),
    # Liberar Doc Contable
    (
        '''                        let idRepTableLib = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasDocLib = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let pFormatLib = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';

                        tbodyLiberarDoc.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${idRepTableLib}</span>${badgeCarasDocLib}</td>''',
        '''                        let idRepTableLib = obtenerIdReporte(f) || 'S/T';
                        let badgeCarasDocLib = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                        let badgeRetrabajoDocLib = (enRetrabajoBloqueo || f.estado === 'Retrabajo' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                        let pFormatLib = f.precio ? parseFloat(f.precio).toLocaleString('en-US') : '0';

                        tbodyLiberarDoc.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${idRepTableLib}</span>${badgeCarasDocLib}${badgeRetrabajoDocLib}</td>'''
    )
]

# 4. Patch static/cotizaciones_10k.js
cotizaciones_10k_replacements = [
    (
        '''                let idRepForTable = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : (f.id || 'S/T');
                let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                tbody.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idRepForTable}</span>${badgeCaras}</td>''',
        '''                let idRepForTable = typeof obtenerIdReporte === 'function' ? obtenerIdReporte(f) : (f.id || 'S/T');
                let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
                let badgeRetrabajo = (f.estado === 'Retrabajo' || f.estado_retrabajo === 'Reasignado' || f.estado_retrabajo === 'Pendiente' || f.estado_retrabajo === 'Por Liberar' || f.retrabajo === 'Sí') ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
                tbody.innerHTML += `<tr><td><span style="color:#0ea5e9; font-weight:bold;">${idRepForTable}</span>${badgeCaras}${badgeRetrabajo}</td>'''
    )
]

# 5. Patch static/facturas_pdf.js
facturas_pdf_replacements = [
    (
        '''            let badgeStr = (r.reactivado_desde_caras) ? ` <br><span style="color:#f59e0b; font-size:0.85em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
            document.getElementById('prev-rep-ticket').innerHTML = r.id + badgeStr;''',
        '''            let badgeStr = (r.reactivado_desde_caras) ? ` <br><span style="color:#f59e0b; font-size:0.85em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajo = (r.estado === 'Retrabajo' || r.retrabajo === 'Sí' || r.es_retrabajo || r.estado_retrabajo) ? ` <br><span style="color:#ef4444; font-size:0.85em; font-weight:bold;">⚠️ Retrabajo</span>` : '';
            document.getElementById('prev-rep-ticket').innerHTML = r.id + badgeStr + badgeRetrabajo;'''
    ),
    (
        '''            let badgeStr2 = (r.reactivado_desde_caras || f.reactivado_desde_caras) ? ` <br><span style="color:#f59e0b; font-size:0.85em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
            document.getElementById('prev-rep-ticket').innerHTML = r.id + badgeStr2;''',
        '''            let badgeStr2 = (r.reactivado_desde_caras || f.reactivado_desde_caras) ? ` <br><span style="color:#f59e0b; font-size:0.85em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajo2 = (r.estado === 'Retrabajo' || r.retrabajo === 'Sí' || r.es_retrabajo || r.estado_retrabajo || f.estado === 'Retrabajo' || f.estado_retrabajo || f.retrabajo === 'Sí') ? ` <br><span style="color:#ef4444; font-size:0.85em; font-weight:bold;">⚠️ Retrabajo</span>` : '';
            document.getElementById('prev-rep-ticket').innerHTML = r.id + badgeStr2 + badgeRetrabajo2;'''
    )
]

ok1 = patch_file("static/script.js", script_replacements, "script.js retrabajo tables")
ok2 = patch_file("static/seccion_reportes.js", seccion_reportes_replacements, "seccion_reportes.js")
ok3 = patch_file("static/facturas_principal.js", facturas_principal_replacements, "facturas_principal.js")
ok4 = patch_file("static/cotizaciones_10k.js", cotizaciones_10k_replacements, "cotizaciones_10k.js")
ok5 = patch_file("static/facturas_pdf.js", facturas_pdf_replacements, "facturas_pdf.js")

if ok1 and ok2 and ok3 and ok4 and ok5:
    print("\nALL FILES PATCHED SUCCESSFULLY!")
else:
    print("\nSOME PATCHES FAILED!")
    sys.exit(1)
