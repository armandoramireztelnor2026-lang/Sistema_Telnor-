import re

def check_buttons(template_path):
    print(f"\n=== {template_path} ===")
    with open(template_path, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = r'<button\s+([^>]*class=["\'][^"\']*btn-sidebar[^"\']*["\'][^>]*)>([\s\S]*?)</button>'
    matches = re.findall(pattern, text)
    for attrs, label in matches:
        clean_label = re.sub(r'<[^>]+>', '', label).strip()
        onclick_match = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
        onclick = onclick_match.group(1) if onclick_match else 'NO ONCLICK'
        print(f"Label: {clean_label:<30} | OnClick: {onclick}")

check_buttons('templates/administracion.html')
check_buttons('templates/proveedores.html')
check_buttons('templates/corporativos.html')

