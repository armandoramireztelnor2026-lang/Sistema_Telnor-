import re

# 1. Update proveedores.html
with open('templates/proveedores.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_button_block = '''                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv('retrabajo')" style="display: flex; align-items: center; justify-content: space-between; padding-left: 20px; padding-right: 15px;">
                        <span>Retrabajo</span>
                        <span id="badge-retrabajo-prov" style="display: none; background: #ef4444; color: white; padding: 2px 7px; border-radius: 10px; font-size: 0.72rem; font-weight: 800; min-width: 18px; text-align: center; line-height: 1;">0</span>
                    </button>'''

new_button_block = '''                    <button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv('retrabajo')">Retrabajo</button>'''

if old_button_block in html:
    html = html.replace(old_button_block, new_button_block)
    print("Replaced button block in proveedores.html")
else:
    # Regex fallback if whitespace differs
    pattern = r'<button class="btn-sidebar btn-sidebar-retrabajo"[^>]*>[\s\S]*?<span>Retrabajo</span>[\s\S]*?<span id="badge-retrabajo-prov"[\s\S]*?</button>'
    html, count = re.subn(pattern, '<button class="btn-sidebar btn-sidebar-retrabajo" title="Garantía" type="button" onclick="cambiarVistaProv(\'retrabajo\')">Retrabajo</button>', html)
    print(f"Regex replaced count: {count}")

# Bump script.js version to v=1000036
html = re.sub(r'src="/static/script\.js\?v=\d+"', 'src="/static/script.js?v=1000036"', html)

with open('templates/proveedores.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated proveedores.html successfully")

