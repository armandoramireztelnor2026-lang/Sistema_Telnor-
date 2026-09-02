import codecs

def replace_section2(filepath):
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The section to replace starts with:
    # <div style="margin-bottom: 20px; border: 2px dashed #0284c7;
    # and ends with the closing div of prev-evidencias-container.
    # It's easier to just find the indices.
    
    start_str = '            <div class="pdf-section-title"\r\n                style="color: #0284c7; border-bottom: 1px solid #0284c7; padding-bottom: 5px;">■ SECCIÓN 2:'
    if start_str not in content:
        start_str = '            <div class="pdf-section-title"\n                style="color: #0284c7; border-bottom: 1px solid #0284c7; padding-bottom: 5px;">■ SECCIÓN 2:'

    if start_str not in content:
        print(f"Start string not found in {filepath}")
        return

    start_idx = content.find('<div\r\n            style="margin-bottom: 20px; border: 2px dashed #0284c7')
    if start_idx == -1:
        start_idx = content.find('<div\n            style="margin-bottom: 20px; border: 2px dashed #0284c7')

    if start_idx == -1:
        print(f"Could not find start of section 2 container in {filepath}")
        return

    end_str = '<div id="prev-evidencias-container"'
    end_idx = content.find(end_str, start_idx)
    if end_idx == -1:
        print(f"Could not find end of section 2 container in {filepath}")
        return
        
    # find the closing div of prev-evidencias-container
    end_div = content.find('</div>', end_idx)
    # find the closing div of the main container
    end_div_main = content.find('</div>', end_div + 6)
    
    new_content = content[:start_idx] + '<div id="pdf-cotizaciones-dinamicas"></div>\n' + content[end_div_main + 6:]
    
    with codecs.open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully patched {filepath}")

replace_section2('templates/proveedores.html')
replace_section2('templates/corporativos.html')
