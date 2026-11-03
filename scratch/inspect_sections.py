with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx_c = content.find('id="seccion-cfg-correo"')
idx_p = content.find('id="seccion-cfg-presupuesto"')
idx_l = content.find('id="seccion-cfg-limite"')
idx_m = content.find('id="modal-agregar-cuenta-correo"')

print("correo:", idx_c)
print("presupuesto:", idx_p)
print("limite:", idx_l)
print("modal:", idx_m)

print("\n--- BEFORE CORREO ---")
print(content[45149:idx_c])

print("\n--- BEFORE PRESUPUESTO ---")
print(content[idx_p-150:idx_p+80])

print("\n--- BEFORE LIMITE ---")
print(content[idx_l-150:idx_l+80])

print("\n--- BEFORE MODAL ---")
print(content[idx_m-150:idx_m])

