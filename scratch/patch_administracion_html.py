# scratch/patch_administracion_html.py
with open("templates/administracion.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Event card for Ultima Garantia
card_fiscal_end = '''                            <div id="analitica-fiscal" class="analitica-card-body">
                                Cargando...
                            </div>
                        </div>'''

new_event_card = '''                            <div id="analitica-fiscal" class="analitica-card-body">
                                Cargando...
                            </div>
                        </div>

                        <!-- Ultima Garantia / Retrabajo Reasignado -->
                        <div class="analitica-card analitica-card-amber" style="border-left: 4px solid #f59e0b;">
                            <div class="analitica-card-header">
                                <div class="analitica-icon-badge" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b;">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                                </div>
                                <h3 class="analitica-card-title">Última Unidad a Garantía</h3>
                            </div>
                            <div id="analitica-garantia" class="analitica-card-body">
                                Cargando...
                            </div>
                        </div>'''

if card_fiscal_end in content:
    content = content.replace(card_fiscal_end, new_event_card, 1)
    print("Event card replaced successfully")
else:
    print("ERROR: card_fiscal_end not found")

# 2. Subtitle update
sub_old = '<p>Censo vehicular en tiempo real de unidades en circulación, taller, jurídicos e inhabilitadas.</p>'
sub_new = '<p>Censo vehicular en tiempo real de unidades en circulación, taller, garantía/retrabajo, jurídicos e inhabilitadas.</p>'
if sub_old in content:
    content = content.replace(sub_old, sub_new, 1)
    print("Subtitle replaced successfully")
else:
    print("Warning: subtitle not found")

# 3. Fleet metric card for Garantia
taller_card_end = '''                                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 6px;">
                                    Desde reporte hasta entrega con código
                                </div>
                            </div>
                        </div>'''

new_fleet_card = '''                                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 6px;">
                                    Desde reporte hasta entrega con código
                                </div>
                            </div>
                        </div>

                        <!-- Garantía / Retrabajo -->
                        <div class="analitica-card analitica-card-amber">
                            <div class="analitica-card-header">
                                <div class="analitica-icon-badge" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b;">
                                    🛡️
                                </div>
                                <h3 class="analitica-card-title">Garantía / Retrabajo</h3>
                            </div>
                            <div class="analitica-card-body" style="padding-top: 5px;">
                                <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                    <span id="analitica-flota-garantia" style="font-size: 2.2em; font-weight: 800; color: #ffffff;">--</span>
                                    <span id="analitica-flota-garantia-pct" style="font-size: 0.9em; color: #fbbf24; font-weight: 700; background: rgba(245, 158, 11, 0.15); padding: 3px 8px; border-radius: 6px;">--%</span>
                                </div>
                                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 6px;">
                                    En garantía / reasignado a taller
                                </div>
                            </div>
                        </div>'''

if taller_card_end in content:
    content = content.replace(taller_card_end, new_fleet_card, 1)
    print("Fleet card replaced successfully")
else:
    print("ERROR: taller_card_end not found")

with open("templates/administracion.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved templates/administracion.html")

