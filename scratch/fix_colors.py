import re
import os

files = [
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\administracion.html",
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\corporativos.html",
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\proveedores.html"
]

# We need to find the <strong style="color:..."> that is inside the accordion div.
# The accordion div structure looks like:
# <div style="padding:15px; cursor:pointer; display:flex; justify-content:space-between; align-items:center;" onclick="var p = this.nextElementSibling...
#         <strong style="color:#f59e0b;">Tickets de Trabajo:</strong>

pattern = re.compile(
    r'(<div style="padding:15px; cursor:pointer; display:flex; justify-content:space-between; align-items:center;" onclick="var p = this\.nextElementSibling;.*?">)\s*'
    r'<strong style="color:[^"]+;">(.*?)</strong>',
    re.DOTALL
)

def replacer(match):
    div_start = match.group(1)
    title = match.group(2)
    return f'{div_start}\n        <strong style="color:white;">{title}</strong>'

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content, count = pattern.subn(replacer, content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {count} colors in {os.path.basename(filepath)}")
    else:
        print(f"No matches found in {os.path.basename(filepath)}")
