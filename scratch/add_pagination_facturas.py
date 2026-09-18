import re

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\facturas_principal.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update cargarFacturas()
# Find end of cargarFacturas
old_cargar = """            });
        }
    }).catch(e => console.error("Error al cargar facturas", e));
}"""

new_cargar = """            });
            // Aplicar paginación a todas las bandejas
            ['tabla-facturas', 'tabla-facturas-finales', 'tabla-doc-contables', 'tabla-archivo', 'tabla-archivo-prov', 'tabla-archivo-corp', 'tabla-archivo-cancelado', 'tabla-corporativo-ordenes', 'tabla-proveedores-ordenes'].forEach(id => {
                if (typeof aplicarPaginacion === 'function') aplicarPaginacion(id, 20, true);
            });
        }
    }).catch(e => console.error("Error al cargar facturas", e));
}"""

js = js.replace(old_cargar, new_cargar)

# 2. Update renderizarListaFlotante()
old_flotante = """        });
    }
}"""
new_flotante = """        });
    }
    if (typeof aplicarPaginacion === 'function') aplicarPaginacion('tabla-reportes', 20, true);
}"""

js = js.replace(old_flotante, new_flotante)

# 3. Update renderizarListaFlotanteTaller()
old_flotante_taller = """        });
    }
}

// Inicialización"""
new_flotante_taller = """        });
    }
    if (typeof aplicarPaginacion === 'function') aplicarPaginacion('tabla-reportes-prov', 20, true);
}

// Inicialización"""

js = js.replace(old_flotante_taller, new_flotante_taller)

with open(r"c:\Users\luisa\OneDrive\Desktop\Telnor_1\static\facturas_principal.js", "w", encoding="utf-8") as f:
    f.write(js)
