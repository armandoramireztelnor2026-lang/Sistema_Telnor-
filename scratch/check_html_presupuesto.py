with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="seccion-cfg-presupuesto"' in l:
        print("Presupuesto start at line:", i+1)
        for j in range(i, min(i+100, len(lines))):
            if 'id="seccion-cfg-limite"' in lines[j]:
                print("Limite start at line:", j+1)
                print("".join(lines[i:j]))
                break

