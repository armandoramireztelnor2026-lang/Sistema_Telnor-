css_font = """
/* ========================================================
   TAMAÑO DE LETRA AUMENTADO EN BANDEJA SECCION DE REPORTES
   ======================================================== */
#tabla-exportable-reportes {
    font-size: 16px !important;
}

#tabla-exportable-reportes th {
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    padding: 14px 16px !important;
}

#tabla-exportable-reportes td {
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.55 !important;
    padding: 14px 16px !important;
}

#tabla-exportable-reportes td div,
#tabla-exportable-reportes td strong,
#tabla-exportable-reportes td a,
#tabla-exportable-reportes td p {
    font-size: 15.5px !important;
}

#tabla-exportable-reportes td span {
    font-size: 14.5px !important;
}

#tabla-exportable-reportes td span[style*="border-radius:12px"],
#tabla-exportable-reportes td span[style*="border-radius: 12px"] {
    padding: 5px 12px !important;
    font-size: 14px !important;
    display: inline-block !important;
}

#tabla-exportable-reportes td button {
    font-size: 14.5px !important;
    font-weight: 600 !important;
    padding: 6px 14px !important;
}

#tabla-exportable-reportes input[type="checkbox"] {
    width: 18px !important;
    height: 18px !important;
    cursor: pointer;
}
"""

with open('static/style.css', 'a', encoding='utf-8') as f:
    f.write(css_font)
print("Appended css_font successfully")

