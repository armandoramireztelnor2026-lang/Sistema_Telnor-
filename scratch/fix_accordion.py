import re
import os

files = [
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\administracion.html",
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\corporativos.html",
    r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\templates\proveedores.html"
]

# Regex pattern to match the div blocks we want to replace
pattern = re.compile(
    r'<div style="background:#0f172a; padding:15px; border-radius:8px; border:1px solid #334155;">\s*'
    r'<strong style="color:([^"]+);">([^<]+)</strong>\s*'
    r'<p style="margin:5px 0 0 0; font-size:0\.95em;">(.*?)</p>\s*'
    r'</div>',
    re.DOTALL
)

def replacer(match):
    color = match.group(1)
    title = match.group(2)
    text = match.group(3)
    
    return f"""<div style="background:#0f172a; border-radius:8px; border:1px solid #334155; overflow:hidden;">
    <div style="padding:15px; cursor:pointer; display:flex; justify-content:space-between; align-items:center;" onclick="var p = this.nextElementSibling; if(p.style.maxHeight !== '0px' && p.style.maxHeight !== ''){{p.style.maxHeight='0px'; this.querySelector('span').innerHTML='▼';}}else{{p.style.maxHeight=p.scrollHeight+'px'; this.querySelector('span').innerHTML='▲';}}">
        <strong style="color:{color};">{title}</strong>
        <span style="color:#a3b1c6; font-size:0.8em;">▼</span>
    </div>
    <div style="max-height:0px; overflow:hidden; transition:max-height 0.3s ease-out;">
        <p style="margin:0; padding:15px; font-size:0.95em; border-top:1px solid #334155; color:#e2e8f0; background:#1e293b;">{text}</p>
    </div>
</div>"""

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply regex
    new_content, count = pattern.subn(replacer, content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {count} blocks in {os.path.basename(filepath)}")
    else:
        print(f"No matches found in {os.path.basename(filepath)}")
