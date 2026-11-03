import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Pestañas paso a paso
old_tabs_start = html.find('<!-- BARRA DE PESTA')
old_tabs_end = html.find('<!-- ==========================================\n                    SECCIÓN 1')
if old_tabs_end == -1:
    old_tabs_end = html.find('<!-- ==========================================\r\n                    SECCIÓN 1')
if old_tabs_end == -1:
    old_tabs_end = html.find('id="seccion-cfg-correo"')
    # find comment preceding it
    old_tabs_end = html.rfind('<!--', 0, old_tabs_end)

print(f"Tabs region: {old_tabs_start} to {old_tabs_end}")
print("Old tabs text preview:\n", repr(html[old_tabs_start:old_tabs_start+100]))

new_tabs_html = """<!-- PESTAÑAS PASO A PASO PARA SEPARAR LA INTERFAZ -->
                    <div style="background: #0b1523; border: 1px solid #1e293b; border-radius: 12px; padding: 6px; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px;">
                        <button type="button" id="tab-btn-cfg-correo" onclick="cambiarTabConfiguracion('correo')" style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; border: 1px solid #38bdf8; font-weight: 700; padding: 12px 16px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);">
                            <span style="background: rgba(255,255,255,0.25); color: #ffffff; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 800;">1</span>
                            <span style="font-size: 0.95rem;">📧 Correo y Códigos</span>
                        </button>
                        <button type="button" id="tab-btn-cfg-presupuesto" onclick="cambiarTabConfiguracion('presupuesto')" style="background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; font-weight: 600; padding: 12px 16px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease;">
                            <span style="background: #1e293b; color: #94a3b8; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 800;">2</span>
                            <span style="font-size: 0.95rem;">💰 Presupuesto</span>
                        </button>
                        <button type="button" id="tab-btn-cfg-limite" onclick="cambiarTabConfiguracion('limite')" style="background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; font-weight: 600; padding: 12px 16px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease;">
                            <span style="background: #1e293b; color: #94a3b8; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 800;">3</span>
                            <span style="font-size: 0.95rem;">🏷️ Cotizaciones Caras</span>
                        </button>
                    </div>

                    """

html = html[:old_tabs_start] + new_tabs_html + html[old_tabs_end:]

# 2. En Sección 1 (Correo):
# Añadir contenedor scroll a tabla-cuentas-correo si no lo tiene con max-height
old_tbl_correo = '<div class="table-responsive">\n                                <table>\n                                    <thead>\n                                        <tr style="background: #0f172a;">\n                                            <th>Nombre / Alias</th>'
if old_tbl_correo not in html:
    old_tbl_correo = '<div class="table-responsive">\r\n                                <table>\r\n                                    <thead>\r\n                                        <tr style="background: #0f172a;">\r\n                                            <th>Nombre / Alias</th>'

new_tbl_correo = '<div class="table-responsive" style="max-height: 280px; overflow-y: auto; border: 1px solid #1e293b; border-radius: 8px;">\n                                <table>\n                                    <thead>\n                                        <tr style="background: #0f172a; position: sticky; top: 0; z-index: 2;">\n                                            <th>Nombre / Alias</th>'

if old_tbl_correo in html:
    html = html.replace(old_tbl_correo, new_tbl_correo, 1)
    print("Tabla cuentas correo actualizada con scroll y cabecera pegajosa")
else:
    print("AVISO: No se encontró old_tbl_correo exacto, buscando alternativo")

# Agregar barra de navegación inferior a Sección 1 (antes del cierre de seccion-cfg-correo)
pos_sec2 = html.find('id="seccion-cfg-presupuesto"')
pos_sec1_end = html.rfind('</div>', 0, pos_sec2)
# Buscamos el cierre de seccion-cfg-correo justo antes de la cabecera de la sección 2
pos_comment_sec2 = html.rfind('<!--', 0, pos_sec2)
pos_div_sec1 = html.rfind('</div>', 0, pos_comment_sec2)

nav_sec1 = """
                        <!-- Barra de Navegación Inferior (Paso 1 -> Paso 2) -->
                        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">Paso 1 de 3: Credenciales de Correo y Códigos SMTP</span>
                            <button type="button" onclick="cambiarTabConfiguracion('presupuesto')" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 10px 22px; border-radius: 8px; font-weight: 700; font-size: 0.92rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                                <span>Siguiente: Control Presupuestal</span> <span>➡️</span>
                            </button>
                        </div>
                    """
html = html[:pos_div_sec1] + nav_sec1 + html[pos_div_sec1:]
print("Nav sección 1 insertado correctamente")

# 3. En Sección 2 (Presupuesto):
# Ocultar por defecto: display: none;
html = html.replace(
    '<div id="seccion-cfg-presupuesto" style="background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">',
    '<div id="seccion-cfg-presupuesto" style="display: none; background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
)

# Añadir contenedor scroll a tabla-cotizaciones-presupuesto
old_tbl_pres = '<div class="table-responsive">\n                                <table>\n                                    <thead>\n                                        <tr style="background: #0f172a;">\n                                            <th>Folio / Ticket</th>'
if old_tbl_pres not in html:
    old_tbl_pres = '<div class="table-responsive">\r\n                                <table>\r\n                                    <thead>\r\n                                        <tr style="background: #0f172a;">\r\n                                            <th>Folio / Ticket</th>'

new_tbl_pres = '<div class="table-responsive" style="max-height: 380px; overflow-y: auto; border: 1px solid #1e293b; border-radius: 8px;">\n                                <table>\n                                    <thead>\n                                        <tr style="background: #0f172a; position: sticky; top: 0; z-index: 2;">\n                                            <th>Folio / Ticket</th>'

if old_tbl_pres in html:
    html = html.replace(old_tbl_pres, new_tbl_pres, 1)
    print("Tabla cotizaciones presupuesto actualizada con scroll y cabecera pegajosa")
else:
    print("AVISO: No se encontró old_tbl_pres exacto")

# Agregar barra de navegación inferior a Sección 2
pos_sec3 = html.find('id="seccion-cfg-limite"')
pos_comment_sec3 = html.rfind('<!--', 0, pos_sec3)
pos_div_sec2 = html.rfind('</div>', 0, pos_comment_sec3)

nav_sec2 = """
                        <!-- Barra de Navegación Inferior (Paso 2) -->
                        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <button type="button" onclick="cambiarTabConfiguracion('correo')" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;">
                                <span>⬅️</span> <span>Anterior: Correo y Códigos</span>
                            </button>
                            <span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">Paso 2 de 3: Control Presupuestal</span>
                            <button type="button" onclick="cambiarTabConfiguracion('limite')" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #0f172a; border: none; padding: 10px 22px; border-radius: 8px; font-weight: 800; font-size: 0.92rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">
                                <span>Siguiente: Cotizaciones Caras</span> <span>➡️</span>
                            </button>
                        </div>
                    """
html = html[:pos_div_sec2] + nav_sec2 + html[pos_div_sec2:]
print("Nav sección 2 insertado correctamente")

# 4. En Sección 3 (Límite):
# Ocultar por defecto: display: none;
html = html.replace(
    '<div id="seccion-cfg-limite" style="background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">',
    '<div id="seccion-cfg-limite" style="display: none; background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
)

# Agregar barra de navegación inferior a Sección 3
pos_modal = html.find('id="modal-agregar-cuenta-correo"')
pos_comment_modal = html.rfind('<!--', 0, pos_modal)
# El final de seccion-cfg-limite es el div antes del cierre del admin-container y vista-configuraciones
# Hay 3 divs de cierre antes del comentario del modal: </div> (cierre de seccion-cfg-limite), </div> (admin-container), </div> (vista-configuraciones)
# Busquemos el cierre de seccion-cfg-limite
pos_div_sec3_end = html.rfind('</div>', 0, pos_comment_modal) # esto cierra vista-configuraciones
pos_div_sec3_end = html.rfind('</div>', 0, pos_div_sec3_end) # esto cierra admin-container
pos_div_sec3_end = html.rfind('</div>', 0, pos_div_sec3_end) # esto cierra seccion-cfg-limite

nav_sec3 = """
                        <!-- Barra de Navegación Inferior (Paso 3) -->
                        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <button type="button" onclick="cambiarTabConfiguracion('presupuesto')" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;">
                                <span>⬅️</span> <span>Anterior: Control Presupuestal</span>
                            </button>
                            <span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">Paso 3 de 3: Límite Cotizaciones Caras (+10000)</span>
                            <button type="button" onclick="cambiarTabConfiguracion('correo')" style="background: #0f172a; color: #38bdf8; border: 1px solid #0284c7; padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;">
                                <span>📧</span> <span>Volver al Paso 1: Correo</span>
                            </button>
                        </div>
                    """
html = html[:pos_div_sec3_end] + nav_sec3 + html[pos_div_sec3_end:]
print("Nav sección 3 insertado correctamente")

# 5. Cache buster
html = html.replace('configuraciones_jefatura.js?v=1', 'configuraciones_jefatura.js?v=2')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Plantilla templates/administracion.html actualizada con éxito!")

