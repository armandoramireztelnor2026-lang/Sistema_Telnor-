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

        // Fetch Tops
        const topDivs = {
            tiempo: document.getElementById('analitica-top-tiempo'),
            averias: document.getElementById('analitica-top-averias'),
            choferes: document.getElementById('analitica-top-choferes'),
            dinero: document.getElementById('analitica-top-dinero'),
            copes: document.getElementById('analitica-top-copes')
        };
        for (let key in topDivs) {
            if (topDivs[key]) topDivs[key].innerHTML = 'Cargando...';
        }

        const responseTops = await fetch('/api/analitica/tops');
        const dataTops = await responseTops.json();

        if (dataTops.status === 'success') {
            const renderList = (list, formatItem) => {
                if (!list || list.length === 0) return '<div style="color:#94a3b8; font-style:italic;">No hay datos suficientes</div>';
                let html = '<ol style="padding-left: 20px; margin: 0;">';
                list.forEach((item, index) => {
                    html += `<li style="margin-bottom: 8px;">${formatItem(item, index)}</li>`;
                });
                html += '</ol>';
                return html;
            };

            if (topDivs.tiempo) {
                topDivs.tiempo.innerHTML = renderList(dataTops.top_tiempo_taller, (item) => `<strong>Eco: ${item.unidad}</strong> - ${item.dias} días (${item.taller})`);
            }
            if (topDivs.averias) {
                topDivs.averias.innerHTML = renderList(dataTops.top_unidades_averias, (item) => `<strong>Eco: ${item.unidad}</strong> - ${item.cantidad} tickets`);
            }
            if (topDivs.choferes) {
                topDivs.choferes.innerHTML = renderList(dataTops.top_choferes, (item) => `<strong>${item.nombre}</strong> - ${item.cantidad} reportes`);
            }
            if (topDivs.dinero) {
                topDivs.dinero.innerHTML = renderList(dataTops.top_talleres_dinero, (item) => `<strong>${item.nombre}</strong> - $${item.total.toLocaleString('es-MX')}`);
            }
            if (topDivs.copes) {
                topDivs.copes.innerHTML = renderList(dataTops.top_copes, (item) => `<strong>${item.cope}</strong> - ${item.cantidad} reportes`);
            }
        }

    } catch (error) {
        console.error("Error cargando analitica:", error);
        for (let key in divs) {
            if (divs[key] && divs[key].innerHTML === 'Cargando...') divs[key].innerHTML = '<span style="color:#ef4444;">Error de red</span>';
        }
    }
}
