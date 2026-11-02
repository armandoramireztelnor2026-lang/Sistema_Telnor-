import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Aplicando estilos y lógica de fijación de columna y cuadro de cruce ---")

# 1. Modificar static/style.css
with open('static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_css = """#tabla-exportable-reportes tbody tr.selected-row td.td-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-negro,
#tabla-exportable-reportes tbody tr.selected-row td.col-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-negro {
    background-color: #222226 !important;
}"""

repl_css = """#tabla-exportable-reportes tbody tr.selected-row td.td-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.td-negro,
#tabla-exportable-reportes tbody tr.selected-row td.col-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.col-negro {
    background-color: #222226 !important;
}

/* ========================================================
   FIJACIÓN VISUAL DE COLUMNA Y CUADRO DE CRUCE EN SECCIÓN DE REPORTES
   ======================================================== */
#tabla-exportable-reportes thead th:not(:first-child) {
    cursor: pointer !important;
    user-select: none !important;
    transition: filter 0.15s ease, box-shadow 0.15s ease !important;
}

#tabla-exportable-reportes thead th:not(:first-child):hover {
    filter: brightness(1.22) !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
}

#tabla-exportable-reportes thead th.columna-fijada-th {
    border-top: 3px solid #38bdf8 !important;
    border-left: 3px solid #38bdf8 !important;
    border-right: 3px solid #38bdf8 !important;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.8), inset 0 0 10px rgba(56, 189, 248, 0.4) !important;
    filter: brightness(1.3) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 35 !important;
}

#tabla-exportable-reportes tbody td.columna-fijada-td {
    border-left: 2px solid #38bdf8 !important;
    border-right: 2px solid #38bdf8 !important;
    box-shadow: inset 1px 0 0 #38bdf8, inset -1px 0 0 #38bdf8 !important;
}

#tabla-exportable-reportes tbody td.columna-fijada-td.td-azul-marino,
#tabla-exportable-reportes tbody td.columna-fijada-td.col-azul-marino {
    background-color: #17386d !important;
}

#tabla-exportable-reportes tbody td.columna-fijada-td.td-verde,
#tabla-exportable-reportes tbody td.columna-fijada-td.col-verde {
    background-color: #11422b !important;
}

#tabla-exportable-reportes tbody td.columna-fijada-td.td-amarillo,
#tabla-exportable-reportes tbody td.columna-fijada-td.col-amarillo {
    background-color: #553908 !important;
}

#tabla-exportable-reportes tbody td.columna-fijada-td.td-negro,
#tabla-exportable-reportes tbody td.columna-fijada-td.col-negro {
    background-color: #2b2b32 !important;
}

/* Cuadro en el cruce exacto entre la fila marcada y la columna fijada */
#tabla-exportable-reportes tbody tr.selected-row td.celda-cruce-marcada,
#tabla-exportable-reportes tbody tr.fila-marcada td.celda-cruce-marcada {
    border: 3px solid #f59e0b !important;
    box-shadow: inset 0 0 0 2px #fef08a, 0 0 18px rgba(245, 158, 11, 0.95), inset 0 0 12px rgba(245, 158, 11, 0.5) !important;
    position: relative !important;
    z-index: 25 !important;
    font-weight: 800 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.celda-cruce-marcada.td-azul-marino,
#tabla-exportable-reportes tbody tr.fila-marcada td.celda-cruce-marcada.td-azul-marino {
    background-color: #23477e !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.celda-cruce-marcada.td-verde,
#tabla-exportable-reportes tbody tr.fila-marcada td.celda-cruce-marcada.td-verde {
    background-color: #175237 !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.celda-cruce-marcada.td-amarillo,
#tabla-exportable-reportes tbody tr.fila-marcada td.celda-cruce-marcada.td-amarillo {
    background-color: #6d4b0d !important;
}

#tabla-exportable-reportes tbody tr.selected-row td.celda-cruce-marcada.td-negro,
#tabla-exportable-reportes tbody tr.fila-marcada td.celda-cruce-marcada.td-negro {
    background-color: #35353d !important;
}"""

if target_css in css:
    css = css.replace(target_css, repl_css, 1)
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("✓ static/style.css actualizado con estilos de columna fijada y celda de cruce")
else:
    print("! AVISO: target_css no encontrado en static/style.css")

# 2. Modificar static/seccion_reportes.js
with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    sr = f.read()

# Actualizar al final de cargarSeccionReportes
target_sr_cargar = """    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
}"""

repl_sr_cargar = """    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
    actualizarMarcadoColumnaYCruceReportes();
}"""

if target_sr_cargar in sr:
    sr = sr.replace(target_sr_cargar, repl_sr_cargar, 1)
    print("✓ static/seccion_reportes.js: hook en cargarSeccionReportes agregado")
else:
    print("! AVISO: target_sr_cargar no encontrado")

# Actualizar al final de aplicarFiltrosReportes
target_sr_filtros = """    // Reajustar la paginación según las filas que quedaron visibles
    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
}"""

repl_sr_filtros = """    // Reajustar la paginación según las filas que quedaron visibles
    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion('tabla-seccion-reportes', 20, true);
    }
    actualizarMarcadoColumnaYCruceReportes();
}"""

if target_sr_filtros in sr:
    sr = sr.replace(target_sr_filtros, repl_sr_filtros, 1)
    print("✓ static/seccion_reportes.js: hook en aplicarFiltrosReportes agregado")
else:
    print("! AVISO: target_sr_filtros no encontrado")

# Reemplazar el manejador de clic final con la lógica completa
target_sr_click = """// --- MARCADOR DE LINEA COMPLETA AL HACER CLICK EN CUALQUIER CELDA O CUADRO ---
document.addEventListener('click', function (e) {
    let tr = e.target.closest('#tabla-exportable-reportes tbody tr');
    if (!tr) return;
    let tbody = tr.parentElement;
    if (!tbody) return;
    let rows = tbody.querySelectorAll('tr');
    rows.forEach(r => {
        r.classList.remove('selected-row');
        r.classList.remove('fila-marcada');
    });
    tr.classList.add('selected-row');
    tr.classList.add('fila-marcada');
});"""

repl_sr_click = """// ========================================================
// FIJACIÓN DE COLUMNA Y CRUCE DE FILA/COLUMNA EN SECCIÓN DE REPORTES
// ========================================================
window.columnaFijadaReportesIndex = null;

function actualizarMarcadoColumnaYCruceReportes() {
    const tabla = document.getElementById('tabla-exportable-reportes');
    if (!tabla) return;

    const colIndex = window.columnaFijadaReportesIndex;

    // 1. Actualizar encabezados
    const ths = tabla.querySelectorAll('thead th');
    ths.forEach((th, idx) => {
        if (colIndex !== null && idx === colIndex) {
            th.classList.add('columna-fijada-th');
            th.setAttribute('title', 'Columna fijada (haz clic para desfijar)');
        } else {
            th.classList.remove('columna-fijada-th');
            if (idx > 0) {
                th.setAttribute('title', 'Haz clic para fijar esta columna');
            }
        }
    });

    // 2. Actualizar celdas del cuerpo (tbody)
    const rows = tabla.querySelectorAll('tbody tr');
    rows.forEach(tr => {
        if (tr.id === 'fila-sin-resultados-reportes') return;
        const isRowMarcada = tr.classList.contains('selected-row') || tr.classList.contains('fila-marcada');
        const cells = tr.children;

        for (let i = 0; i < cells.length; i++) {
            const td = cells[i];
            const isColFijada = (colIndex !== null && i === colIndex);

            if (isColFijada) {
                td.classList.add('columna-fijada-td');
            } else {
                td.classList.remove('columna-fijada-td');
            }

            // Marcar cuadro en la celda donde haya cruce entre fila y columna
            if (isColFijada && isRowMarcada) {
                td.classList.add('celda-cruce-marcada');
            } else {
                td.classList.remove('celda-cruce-marcada');
            }
        }
    });
}

// Escuchador de clic para fijar columnas y marcar filas
document.addEventListener('click', function (e) {
    // A) Clic en el encabezado de la columna (nombre de columna en thead)
    let th = e.target.closest('#tabla-exportable-reportes thead th');
    if (th) {
        // Ignorar checkbox de selección total de la primera columna
        if (th.cellIndex === 0 || e.target.id === 'chk-all-reportes' || e.target.classList.contains('chk-reporte')) {
            return;
        }

        let colIndex = th.cellIndex;
        if (window.columnaFijadaReportesIndex === colIndex) {
            // Si hace clic en la misma columna ya fijada, se desfija (toggle)
            window.columnaFijadaReportesIndex = null;
        } else {
            // Fijar la columna seleccionada
            window.columnaFijadaReportesIndex = colIndex;
        }

        actualizarMarcadoColumnaYCruceReportes();
        return;
    }

    // B) Clic en cualquier celda o renglón de la tabla (tbody)
    let tr = e.target.closest('#tabla-exportable-reportes tbody tr');
    if (tr) {
        if (tr.id === 'fila-sin-resultados-reportes') return;
        let tbody = tr.parentElement;
        if (!tbody) return;

        let rows = tbody.querySelectorAll('tr');
        rows.forEach(r => {
            r.classList.remove('selected-row');
            r.classList.remove('fila-marcada');
        });

        tr.classList.add('selected-row');
        tr.classList.add('fila-marcada');

        actualizarMarcadoColumnaYCruceReportes();
    }
});"""

if target_sr_click in sr:
    sr = sr.replace(target_sr_click, repl_sr_click, 1)
    print("✓ static/seccion_reportes.js: manejador de clic y lógica de cruce agregados")
else:
    print("! AVISO: target_sr_click no encontrado")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(sr)

# 3. Bump cache busters en administracion.html
with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    adm = f.read()

adm = adm.replace('style.css?v=1000035', 'style.css?v=1000045')
adm = adm.replace('seccion_reportes.js?v=1000025', 'seccion_reportes.js?v=1000030')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(adm)
print("✓ templates/administracion.html: cache busters actualizados a style.css?v=1000045 y seccion_reportes.js?v=1000030")

print("--- Parchado completado con éxito ---")

