with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Bump unidades.js version
content = content.replace('unidades.js?v=10', 'unidades.js?v=11')

target_taller_card = """                        <!-- En Taller -->
                        <div class="card-metrica-flota card-taller" onclick="filtrarUnidadesPorEstado('En Taller')" title="Clic para filtrar unidades en taller" style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(2, 132, 199, 0.05)); border: 1px solid rgba(14, 165, 233, 0.35); border-radius: 12px; padding: 16px 20px; cursor: pointer; transition: all 0.2s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 0.85em; font-weight: 700; color: #0ea5e9; text-transform: uppercase; letter-spacing: 0.5px;">En Taller</span>
                                <span style="font-size: 1.4em;">🔧</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <span id="metrica-taller-unidades" style="font-size: 2em; font-weight: 800; color: #ffffff;">--</span>
                                <span id="porcentaje-taller-unidades" style="font-size: 0.85em; color: #38bdf8; font-weight: 600; background: rgba(14, 165, 233, 0.2); padding: 2px 7px; border-radius: 6px;">--%</span>
                            </div>
                            <div style="font-size: 0.8em; color: #94a3b8; margin-top: 6px;">Desde reporte hasta entrega con código</div>
                        </div>"""

new_garantia_card = """                        <!-- En Taller -->
                        <div class="card-metrica-flota card-taller" onclick="filtrarUnidadesPorEstado('En Taller')" title="Clic para filtrar unidades en taller" style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(2, 132, 199, 0.05)); border: 1px solid rgba(14, 165, 233, 0.35); border-radius: 12px; padding: 16px 20px; cursor: pointer; transition: all 0.2s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 0.85em; font-weight: 700; color: #0ea5e9; text-transform: uppercase; letter-spacing: 0.5px;">En Taller</span>
                                <span style="font-size: 1.4em;">🔧</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <span id="metrica-taller-unidades" style="font-size: 2em; font-weight: 800; color: #ffffff;">--</span>
                                <span id="porcentaje-taller-unidades" style="font-size: 0.85em; color: #38bdf8; font-weight: 600; background: rgba(14, 165, 233, 0.2); padding: 2px 7px; border-radius: 6px;">--%</span>
                            </div>
                            <div style="font-size: 0.8em; color: #94a3b8; margin-top: 6px;">Desde reporte hasta entrega con código</div>
                        </div>

                        <!-- En Garantía / Retrabajo -->
                        <div class="card-metrica-flota card-garantia" onclick="filtrarUnidadesPorEstado('En Garantía')" title="Clic para filtrar unidades en garantía / retrabajo" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.05)); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 16px 20px; cursor: pointer; transition: all 0.2s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 0.85em; font-weight: 700; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.5px;">En Garantía</span>
                                <span style="font-size: 1.4em;">🛡️</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <span id="metrica-garantia-unidades" style="font-size: 2em; font-weight: 800; color: #ffffff;">--</span>
                                <span id="porcentaje-garantia-unidades" style="font-size: 0.85em; color: #fbbf24; font-weight: 600; background: rgba(245, 158, 11, 0.2); padding: 2px 7px; border-radius: 6px;">--%</span>
                            </div>
                            <div style="font-size: 0.8em; color: #94a3b8; margin-top: 6px;">En garantía / pendiente por reparar</div>
                        </div>"""

if target_taller_card in content:
    content = content.replace(target_taller_card, new_garantia_card)
    print("Replaced target_taller_card (LF)")
else:
    t_crlf = target_taller_card.replace('\n', '\r\n')
    n_crlf = new_garantia_card.replace('\n', '\r\n')
    if t_crlf in content:
        content = content.replace(t_crlf, n_crlf)
        print("Replaced target_taller_card (CRLF)")
    else:
        print("Warning: target_taller_card not found in administracion.html")

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated administracion.html successfully")

