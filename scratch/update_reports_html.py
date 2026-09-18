html_block = """
            <div id="vista-seccion-reportes" style="display: none;">
                <div class="top-bar" style="display:flex; justify-content:space-between; align-items:center;">
                    <h2>Sección de Reportes Analíticos</h2>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-primary" onclick="exportarExcel()" style="background:#10b981; border:none; padding:8px 15px; border-radius:8px; color:white; font-weight:bold; cursor:pointer;">📊 Exportar a Excel</button>
                        <button class="btn-primary" onclick="imprimirSeleccion()" style="background:#3b82f6; border:none; padding:8px 15px; border-radius:8px; color:white; font-weight:bold; cursor:pointer;">🖨️ Imprimir Selección</button>
                    </div>
                </div>
                
                <div class="admin-container">
                    
                    <!-- KPI DASHBOARD -->
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:15px; margin-bottom:20px;">
                        <div style="background:#0f172a; padding:15px; border-radius:8px; border:1px solid #334155; text-align:center;">
                            <h4 style="margin:0; color:#94a3b8; font-size:0.9em;">Total Inversión (Mostrada)</h4>
                            <div id="kpi-total-gasto" style="font-size:1.5em; font-weight:bold; color:#10b981; margin-top:5px;">$0.00</div>
                        </div>
                        <div style="background:#0f172a; padding:15px; border-radius:8px; border:1px solid #334155; text-align:center;">
                            <h4 style="margin:0; color:#94a3b8; font-size:0.9em;">Tickets Pendientes Doc 50</h4>
                            <div id="kpi-pendientes-doc50" style="font-size:1.5em; font-weight:bold; color:#f59e0b; margin-top:5px;">0</div>
                        </div>
                        <div style="background:#0f172a; padding:15px; border-radius:8px; border:1px solid #334155; text-align:center;">
                            <h4 style="margin:0; color:#94a3b8; font-size:0.9em;">Tickets Pendientes OC</h4>
                            <div id="kpi-pendientes-oc" style="font-size:1.5em; font-weight:bold; color:#ef4444; margin-top:5px;">0</div>
                        </div>
                        <div style="background:#0f172a; padding:15px; border-radius:8px; border:1px solid #3b82f6; text-align:center; cursor:pointer; transition:all 0.3s;" onmouseover="this.style.background='#1e293b'" onmouseout="this.style.background='#0f172a'" onclick="mostrarTop10()">
                            <h4 style="margin:0; color:#60a5fa; font-size:0.9em;">🏆 Top 10 Tiempos en Taller</h4>
                            <div style="font-size:1em; color:white; margin-top:8px;">Ver Ranking</div>
                        </div>
                    </div>

                    <!-- ADVANCED FILTERS -->
                    <div style="background:#1e293b; padding:15px; border-radius:8px; border:1px solid #334155; margin-bottom:20px; display:flex; flex-wrap:wrap; gap:15px; align-items:flex-end;">
                        <div style="flex:1; min-width:150px;">
                            <label style="color:#a3b1c6; font-size:0.85em; margin-bottom:5px; display:block;">Buscar Texto</label>
                            <input type="text" id="filtro-texto-reportes" placeholder="Num. Eco, Ticket, etc..." style="width:100%; padding:8px; border-radius:5px; border:1px solid #334155; background:#0f172a; color:white;" onkeyup="aplicarFiltrosReportes()">
                        </div>
                        <div style="flex:1; min-width:150px;">
                            <label style="color:#a3b1c6; font-size:0.85em; margin-bottom:5px; display:block;">Estado del Ticket</label>
                            <select id="filtro-estado-reportes" style="width:100%; padding:8px; border-radius:5px; border:1px solid #334155; background:#0f172a; color:white;" onchange="aplicarFiltrosReportes()">
                                <option value="">Todos</option>
                                <option value="Pendiente de Cotizacion">Pendiente de Cotización</option>
                                <option value="Esperando Aprobacion">Esperando Aprobación</option>
                                <option value="Esperando Reparacion">Esperando Reparación</option>
                                <option value="Validacion y PIN">Validación y PIN</option>
                                <option value="Liberacion de Documentos">Liberación Doc</option>
                                <option value="Cierre Interno">Cierre Interno (Doc 50)</option>
                                <option value="Finalizado">Finalizado / Histórico</option>
                            </select>
                        </div>
                        <div style="flex:1; min-width:150px;">
                            <label style="color:#a3b1c6; font-size:0.85em; margin-bottom:5px; display:block;">Proveedor</label>
                            <input type="text" id="filtro-proveedor-reportes" placeholder="Taller..." style="width:100%; padding:8px; border-radius:5px; border:1px solid #334155; background:#0f172a; color:white;" onkeyup="aplicarFiltrosReportes()">
                        </div>
                        <div style="flex:1; min-width:150px;">
                            <label style="color:#a3b1c6; font-size:0.85em; margin-bottom:5px; display:block;">Ciudad Base</label>
                            <input type="text" id="filtro-ciudad-reportes" placeholder="Ciudad..." style="width:100%; padding:8px; border-radius:5px; border:1px solid #334155; background:#0f172a; color:white;" onkeyup="aplicarFiltrosReportes()">
                        </div>
                        <div>
                            <button onclick="limpiarFiltrosReportes()" style="background:#475569; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; height:35px;">Limpiar</button>
                        </div>
                    </div>

                    <div class="table-responsive" style="overflow-x: auto; max-width: 100%;">
                        <table style="min-width: 1500px; white-space: nowrap;" id="tabla-exportable-reportes">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" id="chk-all-reportes" onclick="toggleAllReportes(this)"></th>
                                    <th>TICKET</th>
                                    <th>NUM. ECO</th>
                                    <th>FECHA</th>
                                    <th>ESTADO</th>
                                    <th>STATUS UNIDAD</th>
                                    <th>COMPAÑIA</th>
                                    <th>DEPARTAMENTO</th>
                                    <th>COPE/EDIFICIO</th>
                                    <th>CIUDAD/MUNICIPIO BASE</th>
                                    <th>RETRO (PROBLEMA)</th>
                                    <th>COSTO (TOTAL)</th>
                                    <th>PROVEEDOR/TALLER</th>
                                    <th>NOMBRE/SUPERVISOR</th>
                                    <th>FECHA DE ENTRADA</th>
                                    <th>TIEMPO EN TALLER</th>
                                    <th>FECHA DE SALIDA</th>
                                    <th>NUM. PEDIDO</th>
                                    <th>PDF NUM. PEDIDO</th>
                                    <th>NUM. DE ORDEN</th>
                                    <th>NUM. FACTURA</th>
                                    <th>PDF FACTURA</th>
                                    <th>NUM DOC. CONTABLE</th>
                                    <th>COMENTARIOS</th>
                                </tr>
                            </thead>
                            <tbody id="tabla-seccion-reportes">
                                <tr>
                                    <td colspan="24" style="text-align: center; color: #a3b1c6; padding: 20px;">Cargando base de datos...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- MODAL TOP 10 -->
            <div id="modal-top10" class="modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.85); z-index:9999; justify-content:center; align-items:center;">
                <div class="modal-content" style="background:#1e293b; padding:0; border-radius:12px; width:600px; max-width:90vw; display:flex; flex-direction:column; box-shadow:0 20px 40px rgba(0,0,0,0.6); overflow:hidden;">
                    <div style="background:#3b82f6; padding:20px; display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="color:white; margin:0; font-size:1.2em;">🏆 Top 10: Unidades con más tiempo en Taller</h3>
                        <button onclick="document.getElementById('modal-top10').style.display='none'" style="background:none; border:none; color:white; font-size:1.8em; cursor:pointer; padding:0; line-height:1;">&times;</button>
                    </div>
                    <div style="padding:20px; overflow-y:auto; max-height:60vh;">
                        <ul id="lista-top10" style="list-style:none; padding:0; margin:0; color:#e2e8f0;">
                            <!-- Inyectado por JS -->
                        </ul>
                    </div>
                </div>
            </div>

"""

import re
with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\administracion.html", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = '<div id="vista-seccion-reportes" style="display: none;">'
end_marker = '<!-- ESTA VISTA LA VEN AMBOS, PERO SUPERVISOR LA VERÁ FILTRADA -->'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + html_block + "\n            " + content[end_idx:]
    with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\administracion.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Success")
else:
    print(f"Failed to find markers. Start: {start_idx}, End: {end_idx}")
