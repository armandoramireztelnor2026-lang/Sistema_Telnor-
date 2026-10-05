import re

def update_rutas_facturas():
    with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if 'detalles = f"--- DETALLES DEL TICKET ---\\n\\n"' in line:
            start_idx = i - 1  # include comment '# 1. Crear el txt con los detalles'
            break
            
    for i in range(start_idx, len(lines)):
        if 'zf.writestr(f"Ticket_{ticket_id}_Detalles_con_Doc50.txt"' in lines[i]:
            end_idx = i + 1
            break
            
    if start_idx != -1 and end_idx != -1:
        new_code = '''        # 1. Crear el HTML con los detalles
        reportes = leer_json('reportes.json').get('reportes', [])
        reporte = None
        
        ticket_id = factura.get("id_reporte") or factura.get("numero_reporte") or "N/A"
        match = re.search(r"\\[TICKET:(.*?)\\]", factura.get("retro", ""))
        if match: ticket_id = match.group(1).strip()
        
        for r in reportes:
            if str(r.get('id')) == ticket_id:
                reporte = r
                break
        
        r = reporte or {}
        email_status = r.get('email', 'No proporcionado')
        if not email_status.strip(): email_status = 'No proporcionado'
        
        prRaw = factura.get('precio') or factura.get('precio_estimado') or 0
        doc50 = factura.get('numero_doc50', 'No registrado')
        folio_fact = factura.get('factura_folio', 'No registrado')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Expediente de Ticket - {ticket_id}</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; background: #f3f4f6; color: #1e293b; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ border-bottom: 3px solid #1e40af; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
                .title {{ font-size: 24px; font-weight: bold; color: #1e40af; margin: 0; }}
                .badge {{ background: #ef4444; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }}
                .section-title {{ background: #1e293b; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; margin-bottom: 15px; margin-top: 30px; }}
                .line {{ margin-bottom: 10px; font-size: 15px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 5px; }}
                .line strong {{ color: #475569; width: 250px; display: inline-block; }}
                .falla-box {{ background: #f8fafc; border-left: 4px solid #f59e0b; padding: 15px; font-style: italic; margin-top: 10px; color: #334155; }}
                .doc-box {{ background: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin-top: 30px; text-align: center; }}
                .doc-box h3 {{ margin-top: 0; color: #047857; margin-bottom: 15px; }}
                .doc-val {{ font-size: 20px; font-weight: bold; color: #1e293b; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1 class="title">REPORTE DE TALLER TELNOR</h1>
                        <p style="margin:5px 0 0 0; color:#64748b;">Expediente Histórico</p>
                    </div>
                    <div class="badge">Ticket: {ticket_id}</div>
                </div>

                <div class="section-title">■ DATOS TÉCNICOS DEL VEHÍCULO</div>
                <div class="line"><strong>Unidad asignada:</strong> 8090-{r.get('unidad', factura.get('unidad', 'N/A'))}</div>
                <div class="line"><strong>Compañía:</strong> {r.get('compania', 'N/A')}</div>
                <div class="line"><strong>Ciudad / Ubicación Base:</strong> {r.get('ciudad', 'N/A')} - {r.get('cope', 'N/A')}</div>
                <div class="line"><strong>Kilometraje actual:</strong> {r.get('kilometraje', 'N/A')} km</div>
                <div class="line"><strong>Marca y Modelo:</strong> {r.get('marca', 'N/A')} {r.get('modelo', 'N/A')}</div>
                <div class="line"><strong>Tipo de Mantenimiento:</strong> {r.get('mantenimiento', 'N/A')}</div>
                
                <div class="section-title">■ INFORMACIÓN DE CONTACTO DEL OPERADOR</div>
                <div class="line"><strong>Nombre del Empleado:</strong> {r.get('empleado', 'N/A')}</div>
                <div class="line"><strong>Departamento:</strong> {r.get('departamento', 'N/A')}</div>
                <div class="line"><strong>Celular:</strong> {r.get('celular', 'N/A')}</div>
                <div class="line"><strong>Correo Electrónico:</strong> {email_status}</div>

                <div class="section-title">■ DESCRIPCIÓN DEL INCIDENTE / FALLA REPORTADA</div>
                <div class="falla-box">"{r.get('falla', factura.get('diagnostico', 'Sin descripción'))}"</div>

                <div class="section-title">■ DATOS DEL TALLER Y FACTURACIÓN</div>
                <div class="line"><strong>Proveedor Asignado:</strong> {factura.get('proveedor', 'N/A')}</div>
                <div class="line"><strong>Costo Autorizado:</strong> <span style="color:#10b981; font-weight:bold;">${prRaw} MXN</span></div>
                <div class="line"><strong>Estado Final del Ticket:</strong> {factura.get('estado', 'N/A')}</div>
                <div class="line"><strong>Fecha de Cierre:</strong> {factura.get('fecha_cierre', 'N/A')}</div>

                <div class="doc-box">
                    <h3>■ DOCUMENTACIÓN CONTABLE FINAL ■</h3>
                    <div class="doc-val">Número de Documento (50): <span style="color:#ef4444;">{doc50}</span></div>
                    <div class="doc-val" style="font-size:16px;">Folio de Factura del Taller: <span style="color:#3b82f6;">{folio_fact}</span></div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 2. Agregar el HTML al ZIP
        zf.writestr(f"Ticket_{ticket_id}_Detalles_con_Doc50.html", html_content.encode('utf-8'))
'''
        lines[start_idx:end_idx] = [new_code]
        with open('rutas_facturas.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Updated!")
    else:
        print("Lines not found")

update_rutas_facturas()
