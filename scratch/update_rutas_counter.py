# -*- coding: utf-8 -*-
with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """            f["estado"] = "Retrabajo"
            # Se empieza a contar cuando el supervisor lo vuelve a reasignar al taller
            f["num_retrabajo"] = int(f.get("num_retrabajo", 0)) + 1
            break"""

repl = """            # Candado: no duplicar conteo si ya se encontraba en proceso activo de reasignacion
            if f.get("estado") != "Retrabajo" or f.get("estado_retrabajo") != "Reasignado":
                f["num_retrabajo"] = int(f.get("num_retrabajo", 0)) + 1
            elif not f.get("num_retrabajo"):
                f["num_retrabajo"] = 1
            f["estado"] = "Retrabajo"
            break"""

is_crlf = '\r\n' in text
text_norm = text.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
repl_norm = repl.replace('\r\n', '\n')

if target_norm in text_norm:
    text_norm = text_norm.replace(target_norm, repl_norm, 1)
    if is_crlf:
        final_text = text_norm.replace('\n', '\r\n')
    else:
        final_text = text_norm
    with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
        f.write(final_text)
    print('SUCCESS: rutas_reportes.py updated')
else:
    print('ERROR: target not found in rutas_reportes.py')

