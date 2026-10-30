# -*- coding: utf-8 -*-
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update button in supervisor sidebar
t_btn = """<button class="btn-sidebar btn-sidebar-retrabajo" title="Liberar/Retrabajo" type="button" onclick="abrirLiberarRetrabajoEnDesarrollo()">Liberar/Retrabajo</button>"""
r_btn = """<button class="btn-sidebar btn-sidebar-retrabajo" id="btn-sidebar-liberar-retrabajo" title="Liberar/Retrabajo" type="button" onclick="cambiarVistaAdmin('liberar-retrabajo')">Liberar/Retrabajo <span id="badge-liberar-retrabajo" style="display:none; background:#ef4444; color:white; font-size:0.75rem; padding:2px 7px; border-radius:10px; margin-left:6px; font-weight:800;">0</span></button>"""

# 2. Add vista-liberar-retrabajo right before vista-tiempo-garantia
t_vista = """            <!-- VISTA DE TIEMPO / GARANTÍA (JEFATURA: TODOS LOS TALLERES) -->
            <div id="vista-tiempo-garantia" style="display: none;">"""

r_vista = """            <!-- VISTA: LIBERAR / RETRABAJO (SUPERVISOR) -->
            <div id="vista-liberar-retrabajo" style="display: none;">
                <div class="top-bar">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.8rem;">🛡️</span>
                        <div>
                            <h2 style="margin: 0;">Liberación de Retrabajos / Garantías</h2>
                            <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 0.85rem;">Unidades marcadas como listas por el taller, en espera de validación y liberación por supervisión</p>
                        </div>
                    </div>
                </div>
                <div class="admin-container">
                    <div class="buscador-wrapper-div" style="max-width: 500px; margin-bottom: 15px;">
                        <span class="buscador-icono">&#x1F50D;</span>
                        <input type="text" id="buscador-liberar-retrabajo" class="buscador-pildora"
                            placeholder="Buscar por ticket, unidad, taller, COPE..."
                            onkeyup="filtrarTabla('buscador-liberar-retrabajo', 'tabla-liberar-retrabajo')">
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th style="white-space: nowrap;">Ticket</th>
                                    <th style="white-space: nowrap;">Fecha Reasignación</th>
                                    <th style="white-space: nowrap;">Fecha Listo (Taller)</th>
                                    <th style="white-space: nowrap;">Unidad</th>
                                    <th style="white-space: nowrap;">COPE / Edificio</th>
                                    <th style="white-space: nowrap;">Ciudad</th>
                                    <th style="white-space: nowrap;">Taller / Proveedor</th>
                                    <th style="min-width: 260px; max-width: 420px;">Motivo de Retrabajo</th>
                                    <th style="white-space: nowrap; text-align: center;">Estado</th>
                                    <th style="white-space: nowrap; text-align: center;">Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="tabla-liberar-retrabajo">
                                <tr>
                                    <td colspan="10" style="text-align: center; color: #94a3b8; padding: 25px;">
                                        No hay retrabajos listos pendientes de liberación.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- VISTA DE TIEMPO / GARANTÍA (JEFATURA: TODOS LOS TALLERES) -->
            <div id="vista-tiempo-garantia" style="display: none;">"""

is_crlf = '\r\n' in html
html_norm = html.replace('\r\n', '\n')
t_btn_norm = t_btn.replace('\r\n', '\n')
r_btn_norm = r_btn.replace('\r\n', '\n')
t_vista_norm = t_vista.replace('\r\n', '\n')
r_vista_norm = r_vista.replace('\r\n', '\n')

if t_btn_norm in html_norm:
    html_norm = html_norm.replace(t_btn_norm, r_btn_norm, 1)
    print("SUCCESS: button updated in sidebar")
else:
    print("ERROR: t_btn_norm not found")

if t_vista_norm in html_norm:
    html_norm = html_norm.replace(t_vista_norm, r_vista_norm, 1)
    print("SUCCESS: vista-liberar-retrabajo added")
else:
    print("ERROR: t_vista_norm not found")

if is_crlf:
    final_html = html_norm.replace('\n', '\r\n')
else:
    final_html = html_norm

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("administracion.html updated.")

