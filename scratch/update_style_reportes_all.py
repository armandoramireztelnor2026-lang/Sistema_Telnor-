with open('static/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

target_marker = '/* ========================================================\n   COLUMNAS AZUL MARINO EN SECCION DE REPORTES (TICKET ORIGINAL)'
if target_marker not in content:
    target_marker = '/* ========================================================\r\n   COLUMNAS AZUL MARINO EN SECCION DE REPORTES (TICKET ORIGINAL)'

idx = content.find(target_marker)
if idx == -1:
    print("Error: target marker not found in style.css!")
else:
    base_content = content[:idx]

    new_styles = '''/* ========================================================
   SECCION DE REPORTES: COLORES DE COLUMNAS Y MARGENES DEFINIDOS
   ======================================================== */

/* 1. BLOQUE AZUL MARINO (TICKETS Y SELECCION) */
#tabla-exportable-reportes th.th-azul-marino,
#tabla-exportable-reportes th.col-azul-marino,
th.th-azul-marino,
th.col-azul-marino {
    background-color: #1e3a8a !important;
    background: linear-gradient(180deg, #1e40af 0%, #172554 100%) !important;
    color: #ffffff !important;
    border: 2px solid #2563eb !important;
    border-bottom: 3px solid #3b82f6 !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
}

#tabla-exportable-reportes td.td-azul-marino,
#tabla-exportable-reportes td.col-azul-marino,
td.td-azul-marino,
td.col-azul-marino {
    background-color: #0c1e38 !important;
    border: 1px solid #1e3a8a !important;
    color: #ffffff !important;
}

/* 2. BLOQUE VERDE (PROBLEMA, COSTO, TALLER ORIGINAL) */
#tabla-exportable-reportes th.th-verde,
#tabla-exportable-reportes th.col-verde,
th.th-verde,
th.col-verde {
    background-color: #1b4332 !important;
    background: linear-gradient(180deg, #2d6a4f 0%, #1b4332 100%) !important;
    color: #ffffff !important;
    border: 2px solid #2d6a4f !important;
    border-bottom: 3px solid #40916c !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
}

#tabla-exportable-reportes td.td-verde,
#tabla-exportable-reportes td.col-verde,
td.td-verde,
td.col-verde {
    background-color: #082016 !important;
    border: 1px solid #1b4332 !important;
    color: #ffffff !important;
}

/* 3. BLOQUE AMARILLO (RETRABAJO Y REINGRESO) */
#tabla-exportable-reportes th.th-amarillo,
#tabla-exportable-reportes th.col-amarillo,
th.th-amarillo,
th.col-amarillo {
    background-color: #854d0e !important;
    background: linear-gradient(180deg, #a16207 0%, #78350f 100%) !important;
    color: #ffffff !important;
    border: 2px solid #b45309 !important;
    border-bottom: 3px solid #f59e0b !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6) !important;
}

#tabla-exportable-reportes td.td-amarillo,
#tabla-exportable-reportes td.col-amarillo,
td.td-amarillo,
td.col-amarillo {
    background-color: #3b2807 !important;
    border: 1px solid #854d0e !important;
    color: #ffffff !important;
}

/* 4. BLOQUE NEGRO (FACTURACION Y DOCUMENTACION) */
#tabla-exportable-reportes th.th-negro,
#tabla-exportable-reportes th.col-negro,
th.th-negro,
th.col-negro {
    background-color: #000000 !important;
    background: linear-gradient(180deg, #18181b 0%, #000000 100%) !important;
    color: #ffffff !important;
    border: 2px solid #334155 !important;
    border-bottom: 3px solid #64748b !important;
    font-weight: 700 !important;
}

#tabla-exportable-reportes td.td-negro,
#tabla-exportable-reportes td.col-negro,
td.td-negro,
td.col-negro {
    background-color: #050505 !important;
    border: 1px solid #1e293b !important;
    color: #ffffff !important;
}

/* ========================================================
   SUBRAYADO Y EFECTO HOVER PARA TODA LA FILA
   ======================================================== */
#tabla-exportable-reportes tbody tr:hover td {
    border-bottom: 2px solid #38bdf8 !important;
    border-top: 1px solid rgba(56, 189, 248, 0.45) !important;
    cursor: pointer;
}

#tabla-exportable-reportes tbody tr:hover td.td-azul-marino,
#tabla-exportable-reportes tbody tr:hover td.col-azul-marino {
    background-color: #173360 !important;
}

#tabla-exportable-reportes tbody tr:hover td.td-verde,
#tabla-exportable-reportes tbody tr:hover td.col-verde {
    background-color: #0f3524 !important;
}

#tabla-exportable-reportes tbody tr:hover td.td-amarillo,
#tabla-exportable-reportes tbody tr:hover td.col-amarillo {
    background-color: #52380a !important;
}

#tabla-exportable-reportes tbody tr:hover td.td-negro,
#tabla-exportable-reportes tbody tr:hover td.col-negro {
    background-color: #18181b !important;
}

/* ========================================================
   MARCADOR VISUAL DE LINEA COMPLETA AL HACER CLICK EN UNA CELDA
   ======================================================== */
#tabla-exportable-reportes tbody tr.selected-row td,
#tabla-exportable-reportes tbody tr.fila-marcada td {
    border-top: 2px solid #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
    box-shadow: inset 0 1px 0 #38bdf8, inset 0 -1px 0 #38bdf8 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td:first-child,
#tabla-exportable-reportes tbody tr.fila-marcada td:first-child {
    border-left: 4px solid #38bdf8 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td:last-child,
#tabla-exportable-reportes tbody tr.fila-marcada td:last-child {
    border-right: 4px solid #38bdf8 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.td-azul-marino,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-azul-marino,
#tabla-exportable-reportes tbody tr.selected-row td.col-azul-marino,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-azul-marino {
    background-color: #1e3f77 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.td-verde,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-verde,
#tabla-exportable-reportes tbody tr.selected-row td.col-verde,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-verde {
    background-color: #144931 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.td-amarillo,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-amarillo,
#tabla-exportable-reportes tbody tr.selected-row td.col-amarillo,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-amarillo {
    background-color: #63430a !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.td-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-negro,
#tabla-exportable-reportes tbody tr.selected-row td.col-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-negro {
    background-color: #222226 !important;
}
'''
    final_content = base_content + new_styles
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Updated style.css successfully")

