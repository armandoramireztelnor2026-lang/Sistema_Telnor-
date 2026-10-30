import glob
import re

for fpath in glob.glob('templates/*.html') + glob.glob('static/*.js'):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f, start=1):
            if re.search(r'id=["\']unidad["\']|name=["\']unidad["\']|seleccionarUnidad|validarUnidad', line, re.I):
                print(f"{fpath}:{idx}: {line.strip()[:100]}")

