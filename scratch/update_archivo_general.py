import re

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\facturas_principal.js", "r", encoding="utf-8") as f:
    js = f.read()

# We need to find where f.estado === 'Archivado' starts
# Find:
start_block = js.find("if (f.estado === 'Archivado' || (rolUsuario === 'proveedores' && f.validacion_fiscal === 'Aprobada') || (rolUsuario === 'corporativos' && confirmadaTotal)) {")

end_block = js.find("return; // Skip rendering in active trays", start_block)
end_block = js.find("}", end_block) + 1

new_block = """if (f.estado === 'Archivado' || (rolUsuario === 'proveedores' && f.validacion_fiscal === 'Aprobada') || (rolUsuario === 'corporativos' && confirmadaTotal)) {
                    
                    let numCots = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones.length : 1;
                    
                    let doc50Html = '';
                    let folioHtml = '';
                    let provHtml = '';
                    let tituloHtml = '';
                    let precioHtml = '';

                    for (let idx = 0; idx < numCots; idx++) {
                        let cot = (f.cotizaciones && f.cotizaciones.length > 0) ? f.cotizaciones[idx] : null;
                        let bStyle = (idx < numCots - 1) ? 'border-bottom:1px solid #334155; margin-bottom:5px; padding-bottom:5px;' : '';
                        let label = numCots > 1 ? `<strong style="color:#a3b1c6; font-size:0.8em; display:block;">Opción ${idx+1}:</strong>` : '';

                        let doc50 = cot ? (cot.numero_doc50 || 'Pendiente') : (f.numero_doc50 || 'Pendiente');
                        let folio = cot ? (cot.factura_folio || 'Pendiente') : (f.factura_folio || 'Pendiente');
                        let prov = f.proveedor || 'S/T';
                        let tit = cot ? (cot.titulo || 'Sin Título') : (f.titulo || 'Sin Título');
                        let prRaw = cot ? (cot.precio || 0) : (f.precio_estimado || f.precio || 0);
                        let prFmt = parseFloat(prRaw).toLocaleString('en-US');

                        doc50Html += `<div style="${bStyle}">${label}<strong>${doc50}</strong></div>`;
                        folioHtml += `<div style="${bStyle}">${label}<span style="color:#10b981; font-weight:bold;">${folio}</span></div>`;
                        provHtml += `<div style="${bStyle}">${label}<strong>${prov}</strong></div>`;
                        tituloHtml += `<div style="${bStyle}">${label}<strong>${tit}</strong></div>`;
                        precioHtml += `<div style="${bStyle}">${label}$${prFmt} MXN</div>`;
                    }

                    if (f.estado === 'Archivado' && tbodyArchivo && rolUsuario === 'administracion') {
                        let btnVerExp = `<div style="display:flex; flex-direction:column; gap:5px; width:100%;">
                            <button class="btn-info" style="font-size:0.8em; padding:8px 10px; background:#0284c7; border:none; color:white; margin:0; width:100%;" onclick="abrirDetalles('${f.id}')">Ver Detalles del Ticket</button>
                            <div class="dropdown-container" style="position:relative;">
                                <button class="btn-dropdown-toggle btn-info" style="font-size:0.8em; padding:8px 10px; background:#f59e0b; border:none; color:#111; margin:0; width:100%;" onclick="toggleDropdownFixed(event, this)">✏️ Editar Sección ▼</button>
                                <div class="dropdown-menu-fixed">
                                    <button onclick="abrirModalEditarAdmin('${f.id}', 1)">1. Reporte de Incidencia</button>
                                    <button onclick="abrirModalEditarAdmin('${f.id}', 2)">2. Diagnóstico y Cotización</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'orden')">3. Orden de Pedido</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'factura')">4. Factura Fiscal</button>
                                    <button onclick="abrirModalEdicionSeccion('${f.id}', 'doc_contable')">5. Documento Contable</button>
                                </div>
                            </div>
                            <button class="btn-danger-sm" style="width:100%; background:#ef4444; border:none; color:white; margin:0; padding:8px 10px; font-size:0.8em;" onclick="eliminarFacturaSilenciosa('${f.id}')">Eliminar</button>
                        </div>`;
                        let idReporteAsociado = obtenerIdReporte(f) || 'N/A';
                        tbodyArchivo.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#0ea5e9; font-weight:bold;">${idReporteAsociado}</span></td><td style="vertical-align:top;">${doc50Html}</td><td style="vertical-align:top;">${folioHtml}</td><td style="vertical-align:top;">${f.unidad}</td><td style="vertical-align:top;">${provHtml}</td><td style="vertical-align:top;">${precioHtml}</td><td style="vertical-align:top;">${btnVerExp}</td></tr>`;
                        countArchivo++;
                    }

                    if (tbodyArchivoProv && rolUsuario === 'proveedores' && f.proveedor === nombreProveedorActual) {
                        let idRepArchProv = obtenerIdReporte(f) || 'S/T';
                        let btnVerExp = `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoProv.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#0ea5e9; font-weight:bold;">${idRepArchProv}</span></td><td style="vertical-align:top;">${folioHtml}</td><td style="vertical-align:top;">${f.unidad}</td><td style="vertical-align:top;">${tituloHtml}</td><td style="vertical-align:top;">${precioHtml}</td><td style="vertical-align:top;">${btnVerExp}</td></tr>`;
                        countArchivoProv++;
                    }

                    if (tbodyArchivoCorp && rolUsuario === 'corporativos') {
                        let idRepArchCorp = obtenerIdReporte(f) || 'S/T';
                        let btnVerExp = `<button class="btn-info" style="font-size:0.8em; padding:8px 10px; margin:0;" onclick="abrirDetalles('${f.id}')">Ver Detalles</button>`;
                        tbodyArchivoCorp.innerHTML += `<tr><td style="vertical-align:top;"><span style="color:#0ea5e9; font-weight:bold;">${idRepArchCorp}</span></td><td style="vertical-align:top;">${folioHtml}</td><td style="vertical-align:top;">${f.unidad}</td><td style="vertical-align:top;">${provHtml}</td><td style="vertical-align:top;">${tituloHtml}</td><td style="vertical-align:top;">${precioHtml}</td><td style="vertical-align:top;">${btnVerExp}</td></tr>`;
                        countArchivoCorp++;
                    }
                    return; // Skip rendering in active trays
                }"""

js = js[:start_block] + new_block + js[end_block:]

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\facturas_principal.js", "w", encoding="utf-8") as f:
    f.write(js)
