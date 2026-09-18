import re

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\script.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Add pagination base logic at the top of the file
pagination_logic = """
// ==========================================
// LÓGICA DE PAGINACIÓN GLOBAL
// ==========================================
window.paginacionEstado = {};

window.cambiarPagina = function(tbodyId, direccion) {
    if (!window.paginacionEstado[tbodyId]) window.paginacionEstado[tbodyId] = 1;
    window.paginacionEstado[tbodyId] += direccion;
    aplicarPaginacion(tbodyId, 20, false);
};

window.aplicarPaginacion = function(tbodyId, itemsPerPage = 20, resetPage = true) {
    // Excluir explícitamente la tabla de reportes
    if (tbodyId === 'tabla-seccion-reportes') return;
    
    if (resetPage) {
        window.paginacionEstado[tbodyId] = 1;
    }
    
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    
    const filas = Array.from(tbody.getElementsByTagName('tr')).filter(tr => {
        // Ignorar filas que dicen "No hay datos"
        if (tr.cells.length === 1 && tr.cells[0].colSpan > 1) return false;
        // Ignorar filas ocultas por el buscador
        return !tr.classList.contains('oculto-por-filtro');
    });
    
    const totalItems = filas.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
    
    let currentPage = window.paginacionEstado[tbodyId] || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;
    window.paginacionEstado[tbodyId] = currentPage;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    
    // Mostrar/Ocultar filas basadas en la página actual
    let idx = 0;
    for (let tr of tbody.getElementsByTagName('tr')) {
        if (tr.cells.length === 1 && tr.cells[0].colSpan > 1) continue;
        
        if (tr.classList.contains('oculto-por-filtro')) {
            tr.style.display = 'none';
        } else {
            if (idx >= startIndex && idx < endIndex) {
                tr.style.display = '';
            } else {
                tr.style.display = 'none';
            }
            idx++;
        }
    }
    
    // Contenedor de controles
    let pagContainer = document.getElementById('paginacion-' + tbodyId);
    if (!pagContainer) {
        pagContainer = document.createElement('div');
        pagContainer.id = 'paginacion-' + tbodyId;
        pagContainer.style.marginTop = '15px';
        pagContainer.style.display = 'flex';
        pagContainer.style.justifyContent = 'space-between';
        pagContainer.style.alignItems = 'center';
        
        let tableElement = tbody.closest('table');
        if (tableElement) {
            let wrapper = tableElement.closest('.table-responsive') || tableElement.closest('.admin-container') || tableElement.parentNode;
            if (wrapper === tableElement.parentNode) {
                tableElement.parentNode.insertBefore(pagContainer, tableElement.nextSibling);
            } else {
                wrapper.parentNode.insertBefore(pagContainer, wrapper.nextSibling);
            }
        }
    }
    
    if (totalItems <= itemsPerPage) {
        pagContainer.style.display = 'none';
    } else {
        pagContainer.style.display = 'flex';
        pagContainer.innerHTML = `
            <span style="color:#a3b1c6; font-size:0.9em; font-weight:bold;">Mostrando ${totalItems === 0 ? 0 : startIndex + 1} - ${Math.min(endIndex, totalItems)} de ${totalItems} tickets</span>
            <div style="display:flex; align-items:center;">
                <button onclick="cambiarPagina('${tbodyId}', -1)" ${currentPage === 1 ? 'disabled style="opacity:0.5; cursor:not-allowed; padding:6px 15px; margin-right:10px; font-size:0.85em; font-weight:bold; background:#334155; color:white; border:none; border-radius:6px;"' : 'style="padding:6px 15px; margin-right:10px; font-size:0.85em; font-weight:bold; background:#0ea5e9; color:white; border:none; border-radius:6px; cursor:pointer;"'}>◄ Anterior</button>
                <span style="color:white; font-size:0.9em; margin:0 15px; font-weight:bold;">Página ${currentPage} de ${totalPages}</span>
                <button onclick="cambiarPagina('${tbodyId}', 1)" ${currentPage === totalPages ? 'disabled style="opacity:0.5; cursor:not-allowed; padding:6px 15px; font-size:0.85em; font-weight:bold; background:#334155; color:white; border:none; border-radius:6px;"' : 'style="padding:6px 15px; font-size:0.85em; font-weight:bold; background:#0ea5e9; color:white; border:none; border-radius:6px; cursor:pointer;"'}>Siguiente ►</button>
            </div>
        `;
    }
};
// ==========================================
"""

# inject at the top of the file, after the first comment block or let declarations
js = pagination_logic + "\n" + js

# 2. Modify filtrarTabla
old_filter = """function filtrarTabla(inputId, tbodyId) {
    const input = document.getElementById(inputId);
    const filtro = input.value.toLowerCase();
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    const filas = tbody.getElementsByTagName('tr');

    for (let i = 0; i < filas.length; i++) {
        if (filas[i].cells.length === 1 && filas[i].cells[0].colSpan > 1) {
            continue;
        }

        const textoFila = filas[i].textContent.toLowerCase();

        if (textoFila.includes(filtro)) {
            filas[i].style.display = '';
        } else {
            filas[i].style.display = 'none';
        }
    }
}"""

new_filter = """function filtrarTabla(inputId, tbodyId) {
    const input = document.getElementById(inputId);
    const filtro = input.value.toLowerCase();
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    const filas = tbody.getElementsByTagName('tr');

    for (let i = 0; i < filas.length; i++) {
        if (filas[i].cells.length === 1 && filas[i].cells[0].colSpan > 1) {
            continue;
        }

        const textoFila = filas[i].textContent.toLowerCase();

        if (textoFila.includes(filtro)) {
            filas[i].classList.remove('oculto-por-filtro');
        } else {
            filas[i].classList.add('oculto-por-filtro');
        }
    }
    
    if (typeof aplicarPaginacion === 'function') {
        aplicarPaginacion(tbodyId, 20, true);
    } else {
        for (let i = 0; i < filas.length; i++) {
            if (filas[i].cells.length === 1 && filas[i].cells[0].colSpan > 1) continue;
            filas[i].style.display = filas[i].classList.contains('oculto-por-filtro') ? 'none' : '';
        }
    }
}"""

js = js.replace(old_filter, new_filter)

# 3. Modify cargarPendientes to call aplicarPaginacion
old_pendientes = """            tbody.innerHTML += `<tr><td><strong>${nom}</strong></td><td style="text-transform: capitalize;">${user.rol}</td><td>${id}</td>
                                <td><button class="btn-success" onclick="abrirModalDetalles('${id}')">Ver Detalles</button></td></tr>`;
        });
    });
}"""

new_pendientes = """            tbody.innerHTML += `<tr><td><strong>${nom}</strong></td><td style="text-transform: capitalize;">${user.rol}</td><td>${id}</td>
                                <td><button class="btn-success" onclick="abrirModalDetalles('${id}')">Ver Detalles</button></td></tr>`;
        });
        if (typeof aplicarPaginacion === 'function') aplicarPaginacion('tabla-pendientes', 20, true);
    });
}"""
js = js.replace(old_pendientes, new_pendientes)

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\script.js", "w", encoding="utf-8") as f:
    f.write(js)
