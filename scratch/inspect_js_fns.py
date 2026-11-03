import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("File size:", len(js))
print("Functions in file:")
import re
for m in re.finditer(r'window\.([a-zA-Z0-9_]+)\s*=', js):
    print(" -", m.group(1))

