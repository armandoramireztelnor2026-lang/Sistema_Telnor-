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

        // Fetch Charts
        const responseCharts = await fetch('/api/analitica/charts');
        const dataCharts = await responseCharts.json();

        if (dataCharts.status === 'success') {
            const chartColors = [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
                '#06b6d4', '#f97316', '#14b8a6', '#6366f1', '#ec4899'
            ];

            // Destroy existing charts if they exist to prevent hover issues on reload
            if(window.chartPieEstados) window.chartPieEstados.destroy();
            if(window.chartPieMant) window.chartPieMant.destroy();
            if(window.chartPieCopes) window.chartPieCopes.destroy();
            if(window.chartBarMeses) window.chartBarMeses.destroy();
            if(window.chartBarTalleres) window.chartBarTalleres.destroy();
            if(window.chartBarMarcas) window.chartBarMarcas.destroy();

            // Pie 1: Estados
            const ctxPieEstados = document.getElementById('chart-pie-estados').getContext('2d');
            window.chartPieEstados = new Chart(ctxPieEstados, {
                type: 'pie',
                data: {
                    labels: dataCharts.pie_estados.labels,
                    datasets: [{
                        data: dataCharts.pie_estados.data,
                        backgroundColor: chartColors
                    }]
                }
            });

            // Pie 2: Mantenimiento
            const ctxPieMant = document.getElementById('chart-pie-mant').getContext('2d');
            window.chartPieMant = new Chart(ctxPieMant, {
                type: 'doughnut',
                data: {
                    labels: dataCharts.pie_mantenimiento.labels,
                    datasets: [{
                        data: dataCharts.pie_mantenimiento.data,
                        backgroundColor: chartColors.slice(2).concat(chartColors)
                    }]
                }
            });

            // Pie 3: COPEs
            const ctxPieCopes = document.getElementById('chart-pie-copes').getContext('2d');
            window.chartPieCopes = new Chart(ctxPieCopes, {
                type: 'pie',
                data: {
                    labels: dataCharts.pie_copes.labels,
                    datasets: [{
                        data: dataCharts.pie_copes.data,
                        backgroundColor: chartColors.slice(4).concat(chartColors)
                    }]
                }
            });

            // Bar 1: Meses
            const ctxBarMeses = document.getElementById('chart-bar-meses').getContext('2d');
            window.chartBarMeses = new Chart(ctxBarMeses, {
                type: 'bar',
                data: {
                    labels: dataCharts.bar_meses.labels,
                    datasets: [{
                        label: 'Tickets',
                        data: dataCharts.bar_meses.data,
                        backgroundColor: '#3b82f6',
                        borderRadius: 6
                    }]
                },
                options: { scales: { y: { beginAtZero: true } } }
            });

            // Bar 2: Talleres Dinero
            const ctxBarTalleres = document.getElementById('chart-bar-talleres').getContext('2d');
            window.chartBarTalleres = new Chart(ctxBarTalleres, {
                type: 'bar',
                data: {
                    labels: dataCharts.bar_talleres.labels,
                    datasets: [{
                        label: 'Facturación ($)',
                        data: dataCharts.bar_talleres.data,
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    }]
                },
                options: { scales: { y: { beginAtZero: true } } }
            });

            // Bar 3: Marcas/Modelos Fallas
            const ctxBarMarcas = document.getElementById('chart-bar-marcas').getContext('2d');
            window.chartBarMarcas = new Chart(ctxBarMarcas, {
                type: 'bar',
                data: {
                    labels: dataCharts.bar_marcas.labels,
                    datasets: [{
                        label: 'Tickets',
                        data: dataCharts.bar_marcas.data,
                        backgroundColor: '#f59e0b',
                        borderRadius: 6
                    }]
                },
                options: { scales: { y: { beginAtZero: true } }, indexAxis: 'y' }
            });
        }

    } catch (error) {
        console.error("Error cargando analitica:", error);
        for (let key in divs) {
            if (divs[key] && divs[key].innerHTML === 'Cargando...') divs[key].innerHTML = '<span style="color:#ef4444;">Error de red</span>';
        }
    }
}
