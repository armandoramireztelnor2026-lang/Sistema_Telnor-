css_retro = """
/* ========================================================
   ANCHO OPTIMIZADO PARA COLUMNA RETRO (PROBLEMA)
   ======================================================== */
#tabla-exportable-reportes th.col-retro-problema,
#tabla-exportable-reportes td.col-retro-problema {
    width: 480px !important;
    min-width: 480px !important;
    max-width: 600px !important;
    white-space: normal !important;
}

#tabla-exportable-reportes td.col-retro-problema .retro-contenido,
#tabla-exportable-reportes td.col-retro-problema div {
    width: 100% !important;
    max-width: 100% !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: normal !important;
    line-height: 1.55 !important;
}
"""

with open('static/style.css', 'a', encoding='utf-8') as f:
    f.write(css_retro)
print("Appended css_retro successfully")

