async function cargarAnalitica() {
    const divs = {
        llegado: document.getElementById('analitica-llegado'),
        finalizado: document.getElementById('analitica-finalizado'),
        asignado: document.getElementById('analitica-asignado'),
        caro: document.getElementById('analitica-caro'),
        reparada: document.getElementById('analitica-reparada'),
        entregada: document.getElementById('analitica-entregada'),
        rechazada: document.getElementById('analitica-rechazada'),
        fiscal: document.getElementById('analitica-fiscal')
    };

    for (let key in divs) {
        if (divs[key]) divs[key].innerHTML = 'Cargando...';
    }

    try {
        const response = await fetch('/api/analitica/ultimos');
        const data = await response.json();

        if (data.status === 'success') {
            const formatData = (item, includeTaller = false) => {
                if (!item) return '<strong style="color:#ef4444;">Sin datos registrados</strong>';
                let html = `
                    <div style="margin-bottom:5px;"><strong>🎟️ Ticket:</strong> <span style="color:#0ea5e9; font-weight:bold;">${item.ticket}</span></div>
                    <div style="margin-bottom:5px;"><strong>👨‍✈️ Chofer:</strong> ${item.chofer}</div>
                `;
                if (includeTaller) {
                    html += `<div style="margin-bottom:5px;"><strong>🔧 Taller:</strong> ${item.taller}</div>`;
                }
                html += `
                    <div style="margin-bottom:5px;"><strong>👔 Admin:</strong> ${item.administrador}</div>
                    <div style="margin-bottom:5px;"><strong>📋 Super:</strong> ${item.supervisor}</div>
                    <div style="margin-bottom:5px;"><strong>🏢 Jefatura:</strong> ${item.jefatura}</div>
                `;
                return html;
            };

            if (divs.llegado) divs.llegado.innerHTML = formatData(data.ultimo_llegado, false);
            if (divs.finalizado) divs.finalizado.innerHTML = formatData(data.ultimo_finalizado, false);
            if (divs.asignado) divs.asignado.innerHTML = formatData(data.ultimo_asignado, true);
            if (divs.caro) divs.caro.innerHTML = formatData(data.ultimo_caro, true);
            if (divs.reparada) divs.reparada.innerHTML = formatData(data.ultima_reparada, true);
            if (divs.entregada) divs.entregada.innerHTML = formatData(data.ultima_entregada, true);
            if (divs.rechazada) divs.rechazada.innerHTML = formatData(data.ultima_rechazada, true);
            if (divs.fiscal) divs.fiscal.innerHTML = formatData(data.ultima_fiscal, true);
        } else {
            for (let key in divs) {
                if (divs[key]) divs[key].innerHTML = '<span style="color:#ef4444;">Error al cargar datos</span>';
            }
        }
    } catch (error) {
        console.error("Error cargando analitica:", error);
        for (let key in divs) {
            if (divs[key]) divs[key].innerHTML = '<span style="color:#ef4444;">Error de red</span>';
        }
    }
}
