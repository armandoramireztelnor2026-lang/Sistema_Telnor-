import os

template_path = 'templates/administracion.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

pos_vista = content.find('id="vista-configuraciones"')
pos_admin_container = content.find('<div class="admin-container"', pos_vista)
pos_modal = content.find('id="modal-agregar-cuenta-correo"')

print("vista-configuraciones pos:", pos_vista)
print("admin-container pos:", pos_admin_container)
print("modal-agregar pos:", pos_modal)

vista_block = content[pos_admin_container:pos_modal]
print("\n--- FIRST 200 CHARS OF BLOCK ---")
print(vista_block[:200])
print("\n--- LAST 200 CHARS OF BLOCK ---")
print(vista_block[-200:])

