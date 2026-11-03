import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. En guardarCorreoEmisor: agregar confirmación
old_guardar_correo = """window.guardarCorreoEmisor = async function() {
    const correo = document.getElementById('cfg-correo-emisor')?.value.trim();
    const codigo = document.getElementById('cfg-codigo-emisor')?.value.trim();
    const servidor = document.getElementById('cfg-servidor-smtp')?.value.trim() || 'smtp.gmail.com';
    const puerto = document.getElementById('cfg-puerto-smtp')?.value.trim() || '587';

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }

    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación (16 caracteres de Google).");
        return;
    }"""

new_guardar_correo = """window.guardarCorreoEmisor = async function() {
    const correo = document.getElementById('cfg-correo-emisor')?.value.trim();
    const codigo = document.getElementById('cfg-codigo-emisor')?.value.trim();
    const servidor = document.getElementById('cfg-servidor-smtp')?.value.trim() || 'smtp.gmail.com';
    const puerto = document.getElementById('cfg-puerto-smtp')?.value.trim() || '587';

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }

    if (!codigo) {
        alert("⚠️ Por favor ingresa el código o contraseña de aplicación (16 caracteres de Google).");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas guardar y actualizar las credenciales del correo emisor oficial (${correo})?`);
    if (!confirmar) return;"""

if old_guardar_correo in js:
    js = js.replace(old_guardar_correo, new_guardar_correo, 1)
    print("Confirmación añadida a guardarCorreoEmisor")
else:
    print("Aviso: No se encontró old_guardar_correo")

# 2. En guardarNuevaCuentaCorreo: agregar confirmación
old_nueva_cuenta = """window.guardarNuevaCuentaCorreo = async function() {
    const nombre = document.getElementById('modal-nueva-cuenta-nombre')?.value.trim() || 'Cuenta Adicional';
    const correo = document.getElementById('modal-nueva-cuenta-correo')?.value.trim();
    const codigo = document.getElementById('modal-nueva-cuenta-codigo')?.value.trim();
    const servidor = document.getElementById('modal-nueva-cuenta-servidor')?.value.trim() || 'smtp.gmail.com';
    const puerto = document.getElementById('modal-nueva-cuenta-puerto')?.value.trim() || '587';

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }

    if (!codigo) {
        alert("⚠️ Por favor ingresa la contraseña o código de aplicación.");
        return;
    }"""

new_nueva_cuenta = """window.guardarNuevaCuentaCorreo = async function() {
    const nombre = document.getElementById('modal-nueva-cuenta-nombre')?.value.trim() || 'Cuenta Adicional';
    const correo = document.getElementById('modal-nueva-cuenta-correo')?.value.trim();
    const codigo = document.getElementById('modal-nueva-cuenta-codigo')?.value.trim();
    const servidor = document.getElementById('modal-nueva-cuenta-servidor')?.value.trim() || 'smtp.gmail.com';
    const puerto = document.getElementById('modal-nueva-cuenta-puerto')?.value.trim() || '587';

    if (!correo || !correo.includes('@')) {
        alert("⚠️ Por favor ingresa un correo electrónico válido.");
        return;
    }

    if (!codigo) {
        alert("⚠️ Por favor ingresa la contraseña o código de aplicación.");
        return;
    }

    const confirmar = confirm(`¿Confirmas que deseas registrar y agregar la nueva cuenta de correo "${nombre}" (${correo})?`);
    if (!confirmar) return;"""

if old_nueva_cuenta in js:
    js = js.replace(old_nueva_cuenta, new_nueva_cuenta, 1)
    print("Confirmación añadida a guardarNuevaCuentaCorreo")
else:
    print("Aviso: No se encontró old_nueva_cuenta")

# 3. Actualizar cambiarTabConfiguracion sin lógica de badgeNum
old_tab_fn = """window.cambiarTabConfiguracion = function(tabName) {
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
            shadow: '0 4px 12px rgba(2, 132, 199, 0.35)'
        },
        presupuesto: {
            activeBg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            activeBorder: '#34d399',
            color: '#ffffff',
            shadow: '0 4px 12px rgba(16, 185, 129, 0.35)'
        },
        limite: {
            activeBg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            activeBorder: '#fbbf24',
            color: '#0f172a',
            shadow: '0 4px 12px rgba(245, 158, 11, 0.35)'
        }
    };

    validTabs.forEach(t => {
        const sec = document.getElementById(`seccion-cfg-${t}`);
        const btn = document.getElementById(`tab-btn-cfg-${t}`);

        // Mostrar estrictamente solo la actividad seleccionada
        if (sec) {
            sec.style.display = (t === tabName) ? 'block' : 'none';
        }

        // Estilizar los botones de las actividades independientes
        if (btn) {
            if (t === tabName) {
                const s = tabStyles[t] || tabStyles.correo;
                btn.style.background = s.activeBg;
                btn.style.color = s.color;
                btn.style.border = `1px solid ${s.activeBorder}`;
                btn.style.boxShadow = s.shadow;
                btn.style.fontWeight = '700';
            } else {
                btn.style.background = '#0f172a';
                btn.style.color = '#94a3b8';
                btn.style.border = '1px solid #1e293b';
                btn.style.boxShadow = 'none';
                btn.style.fontWeight = '600';
            }
        }
    });

    const vistaEl = document.getElementById('vista-configuraciones');
    if (vistaEl && vistaEl.style.display !== 'none') {
        vistaEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};"""

if old_tab_fn in js:
    js = js.replace(old_tab_fn, new_tab_fn, 1)
    print("cambiarTabConfiguracion actualizado para actividades independientes")
else:
    print("Aviso: No se encontró old_tab_fn")

with open('static/configuraciones_jefatura.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("static/configuraciones_jefatura.js actualizado con éxito!")

