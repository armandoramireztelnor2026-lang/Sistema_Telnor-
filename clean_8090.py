import re
import os

path = 'notificaciones.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace occurrences of 8090-{unidad} with 8090-{str(unidad).replace("8090-", "")}
content = content.replace("8090-{unidad}", "8090-{str(unidad).replace('8090-', '')}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
