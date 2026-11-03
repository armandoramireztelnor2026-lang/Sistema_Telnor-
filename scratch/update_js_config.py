import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update cambiarTabConfiguracion
old_tab_fn = """window.cambiarTabConfiguracion = function(tabName) {
    const tabs = ['correo', 'presupuesto', 'limite'];
    tabs.forEach(t => {
        const sec = document.getElementById(`seccion-cfg-${t}`);
        const btn = document.getElementById(`tab-btn-cfg-${t}`);
        if (sec) sec.style.display = (tabName === 'todas' || tabName === t) ? 'block' : 'none';
        if (btn) {
            if (tabName === t || (tabName === 'todas' && t === 'correo')) {
                btn.style.background = '#0284c7';
                btn.style.color = '#ffffff';
                btn.style.borderColor = '#0284c7';
            } else {
                btn.style.background = '#1e293b';
                btn.style.color = '#94a3b8';
                btn.style.borderColor = '#334155';
            }
        }
    });
};"""

new_tab_fn = """window.cambiarTabConfiguracion = function(tabName) {
    const validTabs = ['correo', 'presupuesto', 'limite'];
    if (!validTabs.includes(tabName)) {
        tabName = 'correo';
    }

    try {
        localStorage.setItem('tabConfiguracionActiva', tabName);
    } catch (e) {}

    const tabStyles = {
        correo: {
            activeBg: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            activeBorder: '#38bdf8',
            color: '#ffffff',
            badgeBg: 'rgba(255,255,255,0.25)',
            badgeColor: '#ffffff',
            shadow: '0 4px 12px rgba(2, 132, 199, 0.35)'
        },
        presupuesto: {
            activeBg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            activeBorder: '#34d399',
            color: '#ffffff',
            badgeBg: 'rgba(255,255,255,0.25)',
            badgeColor: '#ffffff',
            shadow: '0 4px 12px rgba(16, 185, 129, 0.35)'
        },
        limite: {
            activeBg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            activeBorder: '#fbbf24',
            color: '#0f172a',
            badgeBg: '#0f172a',
            badgeColor: '#fbbf24',
            shadow: '0 4px 12px rgba(245, 158, 11, 0.35)'
        }
    };

    validTabs.forEach(t => {
        const sec = document.getElementById(`seccion-cfg-${t}`);
        const btn = document.getElementById(`tab-btn-cfg-${t}`);
        const badgeNum = btn ? btn.querySelector('span:first-child') : null;

        // Mostrar estrictamente solo la sección activa
        if (sec) {
            sec.style.display = (t === tabName) ? 'block' : 'none';
        }

        // Estilizar los botones de navegación superior
        if (btn) {
            if (t === tabName) {
                const s = tabStyles[t] || tabStyles.correo;
                btn.style.background = s.activeBg;
                btn.style.color = s.color;
                btn.style.border = `1px solid ${s.activeBorder}`;
                btn.style.boxShadow = s.shadow;
                btn.style.fontWeight = '700';
                if (badgeNum) {
                    badgeNum.style.background = s.badgeBg;
                    badgeNum.style.color = s.badgeColor;
                }
            } else {
                btn.style.background = '#0f172a';
                btn.style.color = '#94a3b8';
                btn.style.border = '1px solid #1e293b';
                btn.style.boxShadow = 'none';
                btn.style.fontWeight = '600';
                if (badgeNum) {
                    badgeNum.style.background = '#1e293b';
                    badgeNum.style.color = '#94a3b8';
                }
            }
        }
    });

    // Desplazamiento suave para centrar la sección en la pantalla
    const vistaEl = document.getElementById('vista-configuraciones');
    if (vistaEl && vistaEl.style.display !== 'none') {
        vistaEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};"""

if old_tab_fn in js:
    js = js.replace(old_tab_fn, new_tab_fn, 1)
    print("Función cambiarTabConfiguracion reemplazada con éxito")
else:
    print("AVISO: No se encontró exacto old_tab_fn, revisando...")

# 2. Add tab restoration in cargarConfiguracionesJefatura
target_end_cargar = """        if (elLimiteActual) elLimiteActual.innerText = `$ ${limVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
        if (elInputLimite) elInputLimite.value = limVal;

    } catch (err) {"""

replacement_end_cargar = """        if (elLimiteActual) elLimiteActual.innerText = `$ ${limVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
        if (elInputLimite) elInputLimite.value = limVal;

        // 1.5 Activar la sección correspondiente (Paso 1: Correo por defecto, o la guardada)
        let tabActiva = 'correo';
        try {
            const saved = localStorage.getItem('tabConfiguracionActiva');
            if (saved && ['correo', 'presupuesto', 'limite'].includes(saved)) {
                tabActiva = saved;
            }
        } catch (e) {}
        if (typeof window.cambiarTabConfiguracion === 'function') {
            window.cambiarTabConfiguracion(tabActiva);
        }

    } catch (err) {"""

if target_end_cargar in js:
    js = js.replace(target_end_cargar, replacement_end_cargar, 1)
    print("cargarConfiguracionesJefatura actualizado con activación de tab")
else:
    print("AVISO: No se encontró target_end_cargar exacto, revisando...")

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("static/configuraciones_jefatura.js actualizado con éxito!")

