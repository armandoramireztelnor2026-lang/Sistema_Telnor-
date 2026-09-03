// =========================================================
// ARCHIVO: static/facturas_pdf.js
// PROPÓSITO: Generación y diseño de los PDFs
// =========================================================

function previsualizarFactura() {
    if (dtCotizacion.files.length === 0 || dtEvidencia.files.length === 0) { alert("Por favor, asegúrate de subir al menos una cotización y una evidencia."); return; }

    let numReporte = '';
    if(document.getElementById('hidden_numero_reporte')) numReporte = document.getElementById('hidden_numero_reporte').value;
    
    if(numReporte && numReporte !== "" && document.getElementById('pdf-seccion-reporte')) {
        let r = reportesGlobal.find(x => String(x.id) === String(numReporte)) || reporteSeleccionado;
        if(r) {
            document.getElementById('pdf-seccion-reporte').style.display = 'block';
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "No proporcionado";
            document.getElementById('prev-rep-ticket').innerText = r.id; 
            document.getElementById('prev-rep-fecha').innerText = r.fecha; 
            document.getElementById('prev-rep-unidad').innerText = "8090-" + r.unidad;
            document.getElementById('prev-rep-marca').innerText = r.marca + " " + r.modelo;
            document.getElementById('prev-rep-mantenimiento').innerText = r.mantenimiento;
            document.getElementById('prev-rep-empleado').innerText = r.empleado; 
            document.getElementById('prev-rep-celular').innerText = r.celular; 
            document.getElementById('prev-rep-email').innerText = emailStatus; 
            document.getElementById('prev-rep-depto').innerText = r.departamento; 
            document.getElementById('prev-rep-km').innerText = r.kilometraje;
            
            let ciudadStatus = r.ciudad || "No especificada";
            let copeStatus = r.cope || "No especificado";
            if(document.getElementById('prev-rep-ciudad')) {
                document.getElementById('prev-rep-ciudad').innerText = `${ciudadStatus} - ${copeStatus}`;
            }

            if (r.numero_cotizacion_asignacion && document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'block';
                document.getElementById('prev-rep-cotizacion').innerText = r.numero_cotizacion_asignacion;
            } else if (document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'none';
            }
            
            document.getElementById('prev-rep-falla').innerText = r.falla;
            
            if (r.firma_chofer && document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'block';
                document.getElementById('prev-rep-firma-img').src = r.firma_chofer;
            } else if (document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'none';
            }
        }
    } else {
        if(document.getElementById('pdf-seccion-reporte')) document.getElementById('pdf-seccion-reporte').style.display = 'none';
    }

    document.getElementById('prev-unidad').innerText = "8090-" + document.querySelector('input[name="unidad"]').value; document.getElementById('prev-responsable').innerText = document.querySelector('input[name="responsable"]').value; document.getElementById('prev-telefono').innerText = document.querySelector('input[name="telefono"]').value; document.getElementById('prev-fecha').innerText = document.querySelector('input[name="fecha"]').value; document.getElementById('prev-titulo').innerText = document.querySelector('input[name="titulo"]').value; document.getElementById('prev-retro').innerText = document.querySelector('textarea[name="retro"]').value; document.getElementById('prev-diagnostico').innerText = document.querySelector('textarea[name="diagnostico"]').value; document.getElementById('prev-trabajo-realizar').innerText = document.querySelector('textarea[name="trabajo_realizar"]').value; document.getElementById('prev-mantenimiento').innerText = document.querySelector('select[name="mantenimiento"]').value;
    let precioIngresado = document.querySelector('input[name="precio"]').value; document.getElementById('prev-precio').innerText = formatearMoneda(precioIngresado.replace(/[^0-9.]/g, ''));
    
    const contCotizacion = document.getElementById('prev-cotizaciones-container'); const contEvidencia = document.getElementById('prev-evidencias-container');
    contCotizacion.innerHTML = ''; contEvidencia.innerHTML = ''; 
    const renderizarAnexo = (archivos, etiqueta, contenedor) => { Array.from(archivos).forEach(file => { const divInfo = document.createElement('div'); divInfo.className = 'pdf-image-container'; if (file.type.startsWith('image/')) { divInfo.innerHTML = `<img src="${URL.createObjectURL(file)}" class="pdf-anexo-img"><p class="pdf-anexo-label">${etiqueta}: ${file.name}</p>`; } else if (file.name.endsWith('.pdf')) { divInfo.innerHTML = `<div style="font-size:40px; color:#ef4444; margin-bottom:10px;">📄</div><p class="pdf-anexo-label">${etiqueta} (PDF Adjunto): ${file.name}</p>`; } contenedor.appendChild(divInfo); }); };
    renderizarAnexo(dtCotizacion.files, 'Cotización', contCotizacion); renderizarAnexo(dtEvidencia.files, 'Evidencia del Trabajo', contEvidencia);

    document.getElementById('modal-nueva-factura').style.display = 'none'; document.getElementById('modal-previsualizacion-factura').style.display = 'flex';
}

function generarPDFSilencioso(idFactura) {
    const f = facturasGlobal.find(x => String(x.id) === String(idFactura)); if(!f) return;
    let idReporte = obtenerIdReporte(f);

    if(idReporte && document.getElementById('pdf-seccion-reporte')) {
        let r = reportesGlobal.find(x => String(x.id) === String(idReporte));
        if(r) {
            document.getElementById('pdf-seccion-reporte').style.display = 'block';
            let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "No proporcionado";
            document.getElementById('prev-rep-ticket').innerText = r.id; 
            document.getElementById('prev-rep-fecha').innerText = r.fecha; 
            document.getElementById('prev-rep-unidad').innerText = "8090-" + r.unidad;
            document.getElementById('prev-rep-marca').innerText = r.marca + " " + r.modelo;
            document.getElementById('prev-rep-mantenimiento').innerText = r.mantenimiento;
            document.getElementById('prev-rep-empleado').innerText = r.empleado; 
            document.getElementById('prev-rep-celular').innerText = r.celular; 
            document.getElementById('prev-rep-email').innerText = emailStatus; 
            document.getElementById('prev-rep-depto').innerText = r.departamento; 
            document.getElementById('prev-rep-km').innerText = r.kilometraje;
            
            let ciudadStatus = r.ciudad || "No especificada";
            let copeStatus = r.cope || "No especificado";
            if(document.getElementById('prev-rep-ciudad')) {
                document.getElementById('prev-rep-ciudad').innerText = `${ciudadStatus} - ${copeStatus}`;
            }

            if (r.numero_cotizacion_asignacion && document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'block';
                document.getElementById('prev-rep-cotizacion').innerText = r.numero_cotizacion_asignacion;
            } else if (document.getElementById('pdf-line-cotizacion')) {
                document.getElementById('pdf-line-cotizacion').style.display = 'none';
            }
            
            document.getElementById('prev-rep-falla').innerText = r.falla;

            if (r.firma_chofer && document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'block';
                document.getElementById('prev-rep-firma-img').src = r.firma_chofer;
            } else if (document.getElementById('prev-rep-firma-container')) {
                document.getElementById('prev-rep-firma-container').style.display = 'none';
            }
        }
    } else if(document.getElementById('pdf-seccion-reporte')) {
        document.getElementById('pdf-seccion-reporte').style.display = 'none';
    }

    document.getElementById('prev-unidad').innerText = f.unidad; document.getElementById('prev-responsable').innerText = f.responsable; document.getElementById('prev-telefono').innerText = f.telefono; document.getElementById('prev-fecha').innerText = f.fecha; document.getElementById('prev-titulo').innerText = f.titulo; 
    document.getElementById('prev-retro').innerText = limpiarRetro(f.retro); 
    document.getElementById('prev-diagnostico').innerText = f.diagnostico || 'Sin especificar'; document.getElementById('prev-trabajo-realizar').innerText = f.trabajo_realizar || 'Sin especificar'; document.getElementById('prev-mantenimiento').innerText = f.mantenimiento; document.getElementById('prev-precio').innerText = formatearMoneda(f.precio);
    
    const contCotizacion = document.getElementById('prev-cotizaciones-container'); const contEvidencia = document.getElementById('prev-evidencias-container');
    contCotizacion.innerHTML = ''; contEvidencia.innerHTML = ''; 
    f.fotos_cotizacion.forEach(foto => { let ruta = `/static/facturas_archivos/${foto}`; if(foto.endsWith('.pdf')) { contCotizacion.innerHTML += `<div class="pdf-image-container"><div style="font-size:40px; color:#ef4444; margin-bottom:10px;">📄</div><p class="pdf-anexo-label">Cotización PDF: ${foto}</p></div>`; } else { contCotizacion.innerHTML += `<div class="pdf-image-container"><img src="${ruta}" class="pdf-anexo-img"><p class="pdf-anexo-label">Cotización: ${foto}</p></div>`; } });
    f.fotos_evidencia.forEach(foto => { let ruta = `/static/facturas_archivos/${foto}`; contEvidencia.innerHTML += `<div class="pdf-image-container"><img src="${ruta}" class="pdf-anexo-img"><p class="pdf-anexo-label">Evidencia: ${foto}</p></div>`; });

    const overlay = document.createElement('div'); overlay.style.position = 'fixed'; overlay.style.top = '0'; overlay.style.left = '0'; overlay.style.width = '100vw'; overlay.style.height = '100vh'; overlay.style.backgroundColor = 'rgba(11, 28, 48, 0.95)'; overlay.style.zIndex = '999999'; overlay.style.display = 'flex'; overlay.style.flexDirection = 'column'; overlay.style.alignItems = 'center'; overlay.style.overflowY = 'auto'; overlay.style.padding = '40px 0';
    const titleText = document.createElement('h2'); titleText.innerText = "Vista Previa del Documento Oficial"; titleText.style.color = '#40916c'; titleText.style.marginBottom = '20px'; titleText.style.fontFamily = "'Poppins', sans-serif"; overlay.appendChild(titleText);
    const elementoOriginal = document.getElementById('hoja-factura-pdf'); let clon = elementoOriginal.cloneNode(true); clon.id = "clon-pdf-visible"; clon.style.display = 'block'; overlay.appendChild(clon);
    const btnContainer = document.createElement('div'); btnContainer.style.display = 'flex'; btnContainer.style.gap = '20px'; btnContainer.style.marginTop = '25px'; btnContainer.style.marginBottom = '40px';
    const btnCancelar = document.createElement('button'); btnCancelar.innerText = "Cancelar"; btnCancelar.className = "btn-danger"; btnCancelar.style.padding = '12px 24px'; btnCancelar.onclick = () => { document.body.removeChild(overlay); };
    const btnDescargar = document.createElement('button'); btnDescargar.innerText = "Confirmar y Descargar PDF"; btnDescargar.className = "btn-success-modal"; btnDescargar.style.padding = '12px 24px'; btnDescargar.onclick = () => {
        btnDescargar.innerText = "Generando PDF..."; btnDescargar.disabled = true; btnDescargar.style.opacity = '0.7';
        const opciones = { margin: 0.4, filename: `Factura_${f.unidad}_${f.fecha}.pdf`, image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } };
        html2pdf().set(opciones).from(clon).save().then(() => { document.body.removeChild(overlay); });
    };
    btnContainer.appendChild(btnCancelar); btnContainer.appendChild(btnDescargar); overlay.appendChild(btnContainer); document.body.appendChild(overlay);
}

function imprimirReporteTaller() {
    if(!reporteSeleccionado) return;
    const r = reporteSeleccionado;
    let emailStatus = (r.email && r.email.trim() !== "" && r.email.trim() !== "No proporcionado") ? r.email : "No proporcionado";
    let ciudadStatus = r.ciudad || "No especificada";
    let copeStatus = r.cope || "No especificado"; 
    
    let html = `
        <div class="pdf-section-title">■ DATOS TÉCNICOS DEL VEHÍCULO</div>
        <div class="pdf-line"><strong>Ticket de Servicio Asignado:</strong> ${r.id}</div>
        <div class="pdf-line"><strong>Fecha del Reporte Original:</strong> ${r.fecha}</div>
        <div class="pdf-line"><strong>Unidad asignada:</strong> 8090-${r.unidad}</div>
        ${r.compania ? `<div class="pdf-line"><strong>Compañía:</strong> <span style="color:#10b981; font-weight:bold;">${r.compania}</span></div>` : ''}
        <div class="pdf-line"><strong>Ciudad / Ubicación Base:</strong> ${ciudadStatus} - ${copeStatus}</div>
        ${r.numero_cotizacion_asignacion ? `<div class="pdf-line"><strong>No. de Solicitud de Pedido:</strong> <span>${r.numero_cotizacion_asignacion}</span></div>` : ''}
        <div class="pdf-line"><strong>Kilometraje actual:</strong> ${r.kilometraje} km</div>
        <div class="pdf-line"><strong>Marca y Modelo:</strong> ${r.marca} ${r.modelo}</div>
        <div class="pdf-line"><strong>Tipo de Mantenimiento Solicitado:</strong> ${r.mantenimiento}</div>
        <br>
        <div class="pdf-section-title">■ INFORMACIÓN DE CONTACTO DEL OPERADOR</div>
        <div class="pdf-line"><strong>Nombre del Empleado:</strong> ${r.empleado}</div>
        <div class="pdf-line"><strong>Departamento:</strong> ${r.departamento}</div>
        <div class="pdf-line"><strong>Celular:</strong> ${r.celular}</div>
        <div class="pdf-line"><strong>Correo Electrónico:</strong> ${emailStatus}</div>
        <br>
        <div class="pdf-section-title">■ DESCRIPCIÓN DEL INCIDENTE / FALLA REPORTADA</div>
        <div class="pdf-line"><div class="texto-largo" style="background: #f9f9f9; border-left: 3px solid #f59e0b; padding: 15px; font-style: italic; color: #333;">"${r.falla}"</div></div>
        ${r.firma_chofer ? `
        <br>
        <div class="pdf-section-title">■ FIRMA DEL OPERADOR / CHOFER</div>
        <div class="pdf-line" style="text-align: center;">
            <img src="${r.firma_chofer}" alt="Firma del Chofer" style="background: white; border-radius: 8px; max-width: 300px; border: 2px solid #333; padding: 5px;">
        </div>` : ''}
    `;
    
    document.getElementById('pdf-orden-cuerpo').innerHTML = html;
    const opcionesFecha = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('pdf-orden-fecha').innerText = new Date().toLocaleDateString('es-MX', opcionesFecha);
    document.getElementById('modal-ver-reporte-prov').style.display = 'none';
    document.getElementById('modal-pdf-orden-trabajo').style.display = 'flex';
}

function descargarPDFOrden() {
    const elemento = document.getElementById('pdf-orden-contenido');
    const r = reporteSeleccionado;
    if(confirm('¿¿Confirmas que deseas descargar esta Orden de Trabajo en formato PDF?')) {
        const opciones = {
            margin:       0.4,
            filename:     `Orden_Trabajo_${r.id}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        html2pdf().set(opciones).from(elemento).save();
    }
}

function volverAReporteProv() {
    document.getElementById('modal-pdf-orden-trabajo').style.display = 'none';
    document.getElementById('modal-ver-reporte-prov').style.display = 'flex';
}
