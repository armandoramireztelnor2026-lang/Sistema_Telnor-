import sys
import re

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Inicia parchado de leyendas de retrabajo y reactivadas c/caras ---")

# 1. static/seccion_reportes.js
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    sr_content = f.read()

target_sr = """        // Set row info for filtering
        let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
        let badgeRetrabajo = isRowRetrabajo ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
        let badgeColorEstado = '#0ea5e9';
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
        }"""

repl_sr = """        // Evaluar si el ticket está o estuvo en garantía/retrabajo
        let rawRetLower = rawRetrabajo.toLowerCase();
        let estRowLower = String(estado || f.estado || '').toLowerCase();
        let isRowRetrabajo = false;
        if (numRet > 0 ||
            rawRetLower === 'sí' || rawRetLower === 'si' || rawRetLower === 'pendiente' || rawRetLower === 'reasignado' ||
            estRowLower === 'retrabajo' || estRowLower === 'en asignacion/retrabajo' ||
            rawEstRet === 'reasignado' || rawEstRet === 'pendiente' || rawEstRet === 'por liberar' || rawEstRet === 'por_liberar' || rawEstRet === 'finalizado' ||
            Boolean(fechaRetRaw) || tieneReingreso) {
            if (rawRetLower !== 'cancelado' || numRet > 0) {
                isRowRetrabajo = true;
            }
        }

        // Set row info for filtering and badges
        let badgeCaras = f.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
        let badgeRetrabajo = isRowRetrabajo ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
        let badgeColorEstado = '#0ea5e9';
        let textColorEstado = 'white';
        if (estado === 'En Asignacion/Retrabajo') {
            badgeColorEstado = '#eab308';
            textColorEstado = '#0b1c30';
        } else if (estado === 'Retrabajo') {
            badgeColorEstado = '#ef4444';
            textColorEstado = 'white';
        }"""

if target_sr in sr_content:
    sr_content = sr_content.replace(target_sr, repl_sr, 1)
    with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
        f.write(sr_content)
    print("✓ static/seccion_reportes.js actualizado correctamente (orden TDZ corregido y badgeRetrabajo activado)")
else:
    print("! AVISO: target_sr no encontrado en static/seccion_reportes.js (posiblemente ya corregido o diferencias de whitespace)")

# 2. static/facturas_principal.js
with open('static/facturas_principal.js', 'r', encoding='utf-8') as f:
    fp_content = f.read()

target_fp_rep = """            let badgeCaras = r.reactivado_desde_caras ? `<br><span style="color:#f59e0b; font-weight:bold;">⚠️ Reactivada C/cara</span>` : '';
            tbody.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${r.id}</span>${badgeCaras}</td><td>${r.fecha}</td><td><strong>${unidadStr}</strong></td><td><strong>${choferStr}</strong></td><td><strong>${deptoStr}</strong></td>${tdFalla}<td>${r.mantenimiento}</td><td>${estadoBadge}</td><td>${btnAccion}</td></tr>`;"""

repl_fp_rep = """            let fMatch = facturasGlobal.find(f => obtenerIdReporte(f) === String(r.id));
            let isCara = Boolean(r.reactivado_desde_caras || (fMatch && fMatch.reactivado_desde_caras));
            let isRet = Boolean(
                r.retrabajo === 'Sí' || r.retrabajo === 'Si' || r.retrabajo === 'Pendiente' ||
                r.estado === 'Retrabajo' || r.estado === 'En Asignacion/Retrabajo' ||
                r.estado_retrabajo === 'Reasignado' || r.estado_retrabajo === 'Pendiente' || r.estado_retrabajo === 'Por Liberar' ||
                r.es_retrabajo ||
                (r.num_retrabajo && Number(r.num_retrabajo) > 0) ||
                (fMatch && (
                    fMatch.retrabajo === 'Sí' || fMatch.retrabajo === 'Si' || fMatch.retrabajo === 'Pendiente' ||
                    fMatch.estado === 'Retrabajo' || fMatch.estado === 'En Asignacion/Retrabajo' ||
                    fMatch.estado_retrabajo === 'Reasignado' || fMatch.estado_retrabajo === 'Pendiente' || fMatch.estado_retrabajo === 'Por Liberar' ||
                    (fMatch.num_retrabajo && Number(fMatch.num_retrabajo) > 0)
                ))
            );
            let badgeCaras = isCara ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajo = isRet ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
            tbody.innerHTML += `<tr><td><span style="color:#ffffff; font-weight:bold;">${r.id}</span>${badgeCaras}${badgeRetrabajo}</td><td>${r.fecha}</td><td><strong>${unidadStr}</strong></td><td><strong>${choferStr}</strong></td><td><strong>${deptoStr}</strong></td>${tdFalla}<td>${r.mantenimiento}</td><td>${estadoBadge}</td><td>${btnAccion}</td></tr>`;"""

if target_fp_rep in fp_content:
    fp_content = fp_content.replace(target_fp_rep, repl_fp_rep, 1)
    print("✓ static/facturas_principal.js: cargarReportes (tabla-reportes) actualizado con ambas leyendas")
else:
    print("! AVISO: target_fp_rep no encontrado en static/facturas_principal.js")

target_fp_prov = """            if (fallaP.length > 0) fallaP = fallaP.charAt(0).toUpperCase() + fallaP.slice(1);
            if (!fallaP) fallaP = rawFallaP;
            let fallaSub = fallaP.length > 35 ? (fallaP.substring(0, 35) + '...') : fallaP;
            tbody.innerHTML += `<tr><td><strong>${r.id}</strong></td><td>${r.fecha}</td><td>8090-${r.unidad}</td><td>${fallaSub}</td><td>${r.mantenimiento}</td><td>${btnAccion}</td></tr>`;"""

repl_fp_prov = """            if (fallaP.length > 0) fallaP = fallaP.charAt(0).toUpperCase() + fallaP.slice(1);
            if (!fallaP) fallaP = rawFallaP;
            let fallaSub = fallaP.length > 35 ? (fallaP.substring(0, 35) + '...') : fallaP;

            let fMatchP = facturasGlobal.find(f => obtenerIdReporte(f) === String(r.id));
            let isCaraP = Boolean(r.reactivado_desde_caras || (fMatchP && fMatchP.reactivado_desde_caras));
            let isRetP = Boolean(
                r.retrabajo === 'Sí' || r.retrabajo === 'Si' || r.retrabajo === 'Pendiente' ||
                r.estado === 'Retrabajo' || r.estado === 'En Asignacion/Retrabajo' ||
                r.estado_retrabajo === 'Reasignado' || r.estado_retrabajo === 'Pendiente' || r.estado_retrabajo === 'Por Liberar' ||
                r.es_retrabajo ||
                (r.num_retrabajo && Number(r.num_retrabajo) > 0) ||
                (fMatchP && (
                    fMatchP.retrabajo === 'Sí' || fMatchP.retrabajo === 'Si' || fMatchP.retrabajo === 'Pendiente' ||
                    fMatchP.estado === 'Retrabajo' || fMatchP.estado === 'En Asignacion/Retrabajo' ||
                    fMatchP.estado_retrabajo === 'Reasignado' || fMatchP.estado_retrabajo === 'Pendiente' || fMatchP.estado_retrabajo === 'Por Liberar' ||
                    (fMatchP.num_retrabajo && Number(fMatchP.num_retrabajo) > 0)
                ))
            );
            let badgeCarasP = isCaraP ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajoP = isRetP ? `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>` : '';
            tbody.innerHTML += `<tr><td><strong style="color:#ffffff;">${r.id}</strong>${badgeCarasP}${badgeRetrabajoP}</td><td>${r.fecha}</td><td>8090-${r.unidad}</td><td>${fallaSub}</td><td>${r.mantenimiento}</td><td>${btnAccion}</td></tr>`;"""

if target_fp_prov in fp_content:
    fp_content = fp_content.replace(target_fp_prov, repl_fp_prov, 1)
    print("✓ static/facturas_principal.js: cargarReportesProv (tabla-reportes-prov) actualizado con ambas leyendas")
else:
    print("! AVISO: target_fp_prov no encontrado en static/facturas_principal.js")

with open('static/facturas_principal.js', 'w', encoding='utf-8') as f:
    f.write(fp_content)

# 3. static/script.js
with open('static/script.js', 'r', encoding='utf-8') as f:
    sc_content = f.read()

# 3.1 cargarRetrabajosAdmin
target_sc_admin = """            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong><br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span></td>"""

repl_sc_admin = """            let yaCaraAdmin = Boolean(
                r.reactivado_desde_caras ||
                (r.seccion_1 && r.seccion_1.reactivado_desde_caras) ||
                (r.seccion_2 && r.seccion_2.reactivado_desde_caras) ||
                (typeof facturasGlobal !== 'undefined' && facturasGlobal.some(f => (obtenerIdReporte(f) === String(ticketId) || String(f.id) === String(r.factura_id)) && f.reactivado_desde_caras)) ||
                (typeof reportesGlobal !== 'undefined' && reportesGlobal.some(rep => String(rep.id) === String(ticketId) && rep.reactivado_desde_caras))
            );
            let badgeCarasAdmin = yaCaraAdmin ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajoAdmin = `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>`;

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong>${badgeCarasAdmin}${badgeRetrabajoAdmin}</td>"""

if target_sc_admin in sc_content:
    sc_content = sc_content.replace(target_sc_admin, repl_sc_admin, 1)
    print("✓ static/script.js: cargarRetrabajosAdmin actualizado con soporte dual de leyendas")
else:
    print("! AVISO: target_sc_admin no encontrado en static/script.js")

# 3.2 cargarRetrabajosProveedor
# (Now the second occurrence of target_sc_admin is for proveedor)
repl_sc_prov = """            let yaCaraProv = Boolean(
                r.reactivado_desde_caras ||
                (r.seccion_1 && r.seccion_1.reactivado_desde_caras) ||
                (r.seccion_2 && r.seccion_2.reactivado_desde_caras) ||
                (typeof facturasGlobal !== 'undefined' && facturasGlobal.some(f => (obtenerIdReporte(f) === String(ticketId) || String(f.id) === String(r.factura_id)) && f.reactivado_desde_caras)) ||
                (typeof reportesGlobal !== 'undefined' && reportesGlobal.some(rep => String(rep.id) === String(ticketId) && rep.reactivado_desde_caras))
            );
            let badgeCarasProv = yaCaraProv ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajoProv = `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>`;

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong>${badgeCarasProv}${badgeRetrabajoProv}</td>"""

if target_sc_admin in sc_content:
    sc_content = sc_content.replace(target_sc_admin, repl_sc_prov, 1)
    print("✓ static/script.js: cargarRetrabajosProveedor actualizado con soporte dual de leyendas")
else:
    print("! AVISO: target_sc_admin (proveedor) no encontrado en static/script.js")

# 3.3 cargarLiberarRetrabajosSupervisor
# (The third occurrence of target_sc_admin is for supervisor liberacion)
repl_sc_lib = """            let yaCaraLib = Boolean(
                r.reactivado_desde_caras ||
                (r.seccion_1 && r.seccion_1.reactivado_desde_caras) ||
                (r.seccion_2 && r.seccion_2.reactivado_desde_caras) ||
                (typeof facturasGlobal !== 'undefined' && facturasGlobal.some(f => (obtenerIdReporte(f) === String(ticketId) || String(f.id) === String(r.factura_id)) && f.reactivado_desde_caras)) ||
                (typeof reportesGlobal !== 'undefined' && reportesGlobal.some(rep => String(rep.id) === String(ticketId) && rep.reactivado_desde_caras))
            );
            let badgeCarasLib = yaCaraLib ? `<br><span style="color:#f59e0b; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Reactivada C/cara</span>` : '';
            let badgeRetrabajoLib = `<br><span style="color:#ef4444; font-size:0.75em; font-weight:bold; white-space:nowrap;">⚠️ Retrabajo</span>`;

            tbody.innerHTML += `
                <tr>
                    <td style="white-space: nowrap; vertical-align: middle;"><strong style="color: #f59e0b; font-size: 0.95rem;">${ticketId}</strong>${badgeCarasLib}${badgeRetrabajoLib}</td>"""

if target_sc_admin in sc_content:
    sc_content = sc_content.replace(target_sc_admin, repl_sc_lib, 1)
    print("✓ static/script.js: cargarLiberarRetrabajosSupervisor actualizado con soporte dual de leyendas")
else:
    print("! AVISO: target_sc_admin (liberar) no encontrado en static/script.js")

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(sc_content)

print("--- Parchado completado con éxito ---")

