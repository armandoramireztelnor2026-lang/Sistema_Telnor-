with open('templates/reporte.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update enviarReporte guard
old_enviar = """        function enviarReporte() {
            const marca = document.getElementById('marca-input').value;
            if (marca === '' || marca === 'UNIDAD INACTIVA') {"""

new_enviar = """        function enviarReporte() {
            const marca = document.getElementById('marca-input').value;
            if (marca.includes('REASIGNACIÓN') || marca.includes('GARANTÍA')) {
                alert("⚠️ ATENCIÓN: La unidad seleccionada se encuentra actualmente en proceso de reasignación / garantía y no puede ser reportada hasta que sea reparada nuevamente por el taller.");
                return;
            }
            if (marca === '' || marca === 'UNIDAD INACTIVA') {"""

if old_enviar in content:
    content = content.replace(old_enviar, new_enviar)
    print("Replaced enviarReporte guard (LF)")
else:
    oe_crlf = old_enviar.replace('\n', '\r\n')
    ne_crlf = new_enviar.replace('\n', '\r\n')
    if oe_crlf in content:
        content = content.replace(oe_crlf, ne_crlf)
        print("Replaced enviarReporte guard (CRLF)")
    else:
        print("Warning: old_enviar not found in reporte.html")

# 2. Remove old duplicate listener block lines 695-725
old_duplicate_block = """    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            let unidadesData = {};
            try {
                const res = await fetch('/api/unidades');
                unidadesData = await res.json();
            } catch(e) {
                console.error("Error cargando unidades:", e);
            }
            
            const unidadInput = document.getElementById('unidad-input');
            const marcaInput = document.getElementById('marca-input');
            const modeloInput = document.getElementById('modelo-input');
            
            if (unidadInput && marcaInput && modeloInput) {
                unidadInput.addEventListener('input', () => {
                    // Remover maxLength temporalmente si el usuario dijo que podía ser más largo, pero el form actual tiene , lo respetamos.
                    // (Actually the user JSON has IDs like "80901231" which are 8 digits!)
                    // Let's remove the  in case they have longer IDs.
                    const val = unidadInput.value.trim();
                    if (unidadesData[val]) {
                        marcaInput.value = unidadesData[val].Marca || '';
                        modeloInput.value = unidadesData[val].Modelo || '';
                    } else {
                        marcaInput.value = '';
                        modeloInput.value = '';
                    }
                });
            }
        });
    </script>"""

if old_duplicate_block in content:
    content = content.replace(old_duplicate_block, "")
    print("Removed duplicate block (LF)")
else:
    odb_crlf = old_duplicate_block.replace('\n', '\r\n')
    if odb_crlf in content:
        content = content.replace(odb_crlf, "")
        print("Removed duplicate block (CRLF)")
    else:
        print("Warning: old_duplicate_block not found in reporte.html")

# 3. Update checkAutoFill function
old_autofill = """        function checkAutoFill() {
            const unidadInput = document.getElementById('unidad-input');
            const marcaInput = document.getElementById('marca-input');
            const modeloInput = document.getElementById('modelo-input');
            const btnSubmit = document.getElementById('btn-enviar-reporte');
            
            if (!unidadInput || !marcaInput || !modeloInput) return;
            
            const rawVal = unidadInput.value.trim();
            const val = "8090" + rawVal;
            
            if (globalUnidadesData[val]) {
                const info = globalUnidadesData[val];
                if (info.Juridicos === true) {
                    marcaInput.value = 'UNIDAD EN JURÍDICOS';
                    modeloInput.value = 'BLOQUEADA';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'Unidad Inhabilitada (Jurídicos)';
                        btnSubmit.style.background = '#6d28d9';
                    }
                } else if (info.Estado === 'Inactiva') {
                    marcaInput.value = 'UNIDAD INACTIVA';
                    modeloInput.value = 'NO DISPONIBLE';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'Unidad Inactiva';
                        btnSubmit.style.background = '#6b7280';
                    }
                } else if (info.activa_en_taller === true) {
                    marcaInput.value = info.Marca || '';
                    modeloInput.value = info.Modelo || '';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'La unidad ya tiene un ticket activo';
                        btnSubmit.style.background = '#ef4444';
                    }
                } else {
                    marcaInput.value = info.Marca || '';
                    modeloInput.value = info.Modelo || '';
                    if(btnSubmit) {
                        btnSubmit.disabled = false;
                        btnSubmit.innerText = 'Enviar Reporte al Sistema';
                        btnSubmit.style.background = '';
                    }
                }
            } else {
                marcaInput.value = '';
                modeloInput.value = '';
                if(btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerText = 'Enviar Reporte al Sistema';
                    btnSubmit.style.background = '';
                }
            }
        }"""

new_autofill = """        window.lastAlertEcoGarantia = null;

        function checkAutoFill() {
            const unidadInput = document.getElementById('unidad-input');
            const marcaInput = document.getElementById('marca-input');
            const modeloInput = document.getElementById('modelo-input');
            const btnSubmit = document.getElementById('btn-enviar-reporte');
            
            if (!unidadInput || !marcaInput || !modeloInput) return;
            
            const rawVal = unidadInput.value.trim();
            const val = "8090" + rawVal;

            if (rawVal.length < 4) {
                window.lastAlertEcoGarantia = null;
            }
            
            if (globalUnidadesData[val]) {
                const info = globalUnidadesData[val];
                if (info.activa_en_garantia === true || info.estado_operativo === 'En Garantía') {
                    marcaInput.value = 'UNIDAD EN REASIGNACIÓN (GARANTÍA)';
                    modeloInput.value = 'BLOQUEADA';
                    if (btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'Unidad en Reasignación (Garantía)';
                        btnSubmit.style.background = '#f59e0b';
                    }
                    if (rawVal.length === 4 && window.lastAlertEcoGarantia !== val) {
                        window.lastAlertEcoGarantia = val;
                        alert("⚠️ ATENCIÓN: La unidad 8090-" + rawVal + " se encuentra actualmente en proceso de reasignación / garantía y no puede ser reportada hasta que sea reparada nuevamente por el taller.");
                    }
                } else if (info.Juridicos === true) {
                    marcaInput.value = 'UNIDAD EN JURÍDICOS';
                    modeloInput.value = 'BLOQUEADA';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'Unidad Inhabilitada (Jurídicos)';
                        btnSubmit.style.background = '#6d28d9';
                    }
                } else if (info.Estado === 'Inactiva') {
                    marcaInput.value = 'UNIDAD INACTIVA';
                    modeloInput.value = 'NO DISPONIBLE';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'Unidad Inactiva';
                        btnSubmit.style.background = '#6b7280';
                    }
                } else if (info.activa_en_taller === true) {
                    marcaInput.value = info.Marca || '';
                    modeloInput.value = info.Modelo || '';
                    if(btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerText = 'La unidad ya tiene un ticket activo';
                        btnSubmit.style.background = '#ef4444';
                    }
                } else {
                    marcaInput.value = info.Marca || '';
                    modeloInput.value = info.Modelo || '';
                    if(btnSubmit) {
                        btnSubmit.disabled = false;
                        btnSubmit.innerText = 'Enviar Reporte al Sistema';
                        btnSubmit.style.background = '';
                    }
                }
            } else {
                marcaInput.value = '';
                modeloInput.value = '';
                if(btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerText = 'Enviar Reporte al Sistema';
                    btnSubmit.style.background = '';
                }
            }
        }"""

if old_autofill in content:
    content = content.replace(old_autofill, new_autofill)
    print("Replaced checkAutoFill (LF)")
else:
    oaf_crlf = old_autofill.replace('\n', '\r\n')
    naf_crlf = new_autofill.replace('\n', '\r\n')
    if oaf_crlf in content:
        content = content.replace(oaf_crlf, naf_crlf)
        print("Replaced checkAutoFill (CRLF)")
    else:
        print("Warning: old_autofill not found in reporte.html")

with open('templates/reporte.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated templates/reporte.html successfully")

