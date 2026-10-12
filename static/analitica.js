async function cargarAnalitica() {
    const periodSelect = document.getElementById('analitica-period-select');
    
    // Si está vacío, poblar dinámicamente desde 2026 hasta el semestre actual
    if (periodSelect && periodSelect.options.length === 0) {
        const startYear = 2026;
        const currentDate = new Date();
        const currentYear = currentDate.getFullYear();
        const currentSemester = (currentDate.getMonth() + 1) <= 6 ? 'S1' : 'S2';
        
        let html = '<option value="Todos">Histórico Total</option>';
        for (let y = startYear; y <= currentYear; y++) {
            // Siempre agrega el primer semestre del año, excepto para 2026 según solicitud
            if (y !== 2026) {
                html += `<option value="${y}-S1">${y} - 1er Semestre (Ene-Jun)</option>`;
            }
            
            // Agrega el segundo semestre solo si ya es un año pasado, o si estamos en el año actual y ya empezó Julio
            if (y < currentYear || (y === currentYear && currentSemester === 'S2')) {
                html += `<option value="${y}-S2">${y} - 2do Semestre (Jul-Dic)</option>`;
            }
        }
        periodSelect.innerHTML = html;
        
        // Seleccionar por defecto el semestre actual
        periodSelect.value = `${currentYear}-${currentSemester}`;
    }

    const period = periodSelect ? periodSelect.value : 'Todos';

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
        if (divs[key]) divs[key].innerHTML = '<span style="color:#94a3b8; font-style:italic;">Cargando datos...</span>';
    }

    // Configuración global de Chart.js para el lenguaje de diseño del sistema
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Poppins', sans-serif";
        Chart.defaults.color = '#cbd5e1';
        if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
            Chart.defaults.plugins.tooltip.backgroundColor = '#0b1c30';
            Chart.defaults.plugins.tooltip.titleColor = '#40916c';
            Chart.defaults.plugins.tooltip.titleFont = { family: "'Poppins', sans-serif", weight: '600', size: 13 };
            Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';
            Chart.defaults.plugins.tooltip.bodyFont = { family: "'Poppins', sans-serif", size: 12 };
            Chart.defaults.plugins.tooltip.borderColor = '#1f395a';
            Chart.defaults.plugins.tooltip.borderWidth = 1;
            Chart.defaults.plugins.tooltip.padding = 10;
            Chart.defaults.plugins.tooltip.cornerRadius = 8;
        }
    }

    try {
        const response = await fetch(`/api/analitica/ultimos?period=${period}`);
        const data = await response.json();

        if (data.status === 'success') {
            const formatData = (item, includeTaller = false) => {
                if (!item) return '<div style="color:#ef4444; font-weight:500; font-style:italic; padding: 10px 0;">Sin datos registrados en el periodo</div>';
                
                let fechaFormateada = '';
                if (item.fecha && item.fecha !== 'N/A') {
                    try {
                        const d = new Date(item.fecha);
                        const fechaTxt = !isNaN(d.getTime()) 
                            ? d.toLocaleString('es-MX', {dateStyle: 'medium', timeStyle: 'short'})
                            : item.fecha;
                        fechaFormateada = `<div style="margin-top:10px; font-size:0.8rem; color:#94a3b8; border-top: 1px dashed #1f395a; padding-top: 8px;">📅 <span style="color:#cbd5e1;">${fechaTxt}</span></div>`;
                    } catch(e) {
                        fechaFormateada = `<div style="margin-top:10px; font-size:0.8rem; color:#94a3b8; border-top: 1px dashed #1f395a; padding-top: 8px;">📅 <span style="color:#cbd5e1;">${item.fecha}</span></div>`;
                    }
                }

                let html = `
                    <div style="margin-bottom:7px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#94a3b8; font-size:0.85em;">🎟️ Ticket:</span>
                        <span style="color:#38bdf8; font-weight:700; background:rgba(14,165,233,0.12); padding:2px 8px; border-radius:6px; border:1px solid rgba(14,165,233,0.25);">${item.ticket}</span>
                    </div>
                    <div style="margin-bottom:7px; display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8; font-size:0.85em;">👨‍✈️ Chofer:</span>
                        <span style="color:#ffffff; font-weight:500; text-align:right;">${item.chofer}</span>
                    </div>
                `;
                if (includeTaller) {
                    html += `
                        <div style="margin-bottom:7px; display:flex; justify-content:space-between;">
                            <span style="color:#94a3b8; font-size:0.85em;">🔧 Taller:</span>
                            <span style="color:#ffffff; font-weight:500; text-align:right;">${item.taller}</span>
                        </div>
                    `;
                }
                html += `
                    <div style="margin-bottom:7px; display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8; font-size:0.85em;">👔 Admin:</span>
                        <span style="color:#e0e6ed; font-weight:500; text-align:right;">${item.administrador}</span>
                    </div>
                    <div style="margin-bottom:7px; display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8; font-size:0.85em;">📋 Super:</span>
                        <span style="color:#e0e6ed; font-weight:500; text-align:right;">${item.supervisor}</span>
                    </div>
                    <div style="margin-bottom:7px; display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8; font-size:0.85em;">🏢 Jefatura:</span>
                        <span style="color:#e0e6ed; font-weight:500; text-align:right;">${item.jefatura}</span>
                    </div>
                    ${fechaFormateada}
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
            if (topDivs[key]) topDivs[key].innerHTML = '<span style="color:#94a3b8; font-style:italic;">Cargando rankings...</span>';
        }

        const responseTops = await fetch(`/api/analitica/tops?period=${period}`);
        const dataTops = await responseTops.json();

        if (dataTops.status === 'success') {
            const renderList = (list, formatItem) => {
                if (!list || list.length === 0) return '<div style="color:#64748b; font-style:italic; padding:10px 0;">No hay datos registrados</div>';
                let html = '<div class="analitica-rank-list">';
                list.forEach((item, index) => {
                    let medalla = index === 0 ? '🥇' : (index === 1 ? '🥈' : (index === 2 ? '🥉' : `#${index + 1}`));
                    html += `
                        <div class="analitica-rank-item">
                            <div style="display:flex; align-items:center; gap:8px; width:100%; justify-content:space-between;">
                                <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
                                    <span style="font-size:0.95em; min-width:22px; text-align:center;">${medalla}</span>
                                    <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${formatItem(item).label}</span>
                                </div>
                                <span class="analitica-rank-badge" style="${formatItem(item).badgeStyle}">${formatItem(item).valor}</span>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                return html;
            };

            if (topDivs.tiempo) {
                topDivs.tiempo.innerHTML = renderList(dataTops.top_tiempo_taller, (item) => ({
                    label: `<strong>Eco: ${item.unidad}</strong> <span style="color:#94a3b8; font-size:0.85em;">(${item.taller})</span>`,
                    valor: `${item.dias} días`,
                    badgeStyle: 'background:rgba(249,115,22,0.15); color:#fb923c; border:1px solid rgba(249,115,22,0.3);'
                }));
            }
            if (topDivs.averias) {
                topDivs.averias.innerHTML = renderList(dataTops.top_unidades_averias, (item) => ({
                    label: `<strong>Eco: ${item.unidad}</strong>`,
                    valor: `${item.cantidad} tickets`,
                    badgeStyle: 'background:rgba(234,179,8,0.15); color:#facc15; border:1px solid rgba(234,179,8,0.3);'
                }));
            }
            if (topDivs.choferes) {
                topDivs.choferes.innerHTML = renderList(dataTops.top_choferes, (item) => ({
                    label: `<strong>${item.nombre}</strong>`,
                    valor: `${item.cantidad} reps`,
                    badgeStyle: 'background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3);'
                }));
            }
            if (topDivs.dinero) {
                topDivs.dinero.innerHTML = renderList(dataTops.top_talleres_dinero, (item) => ({
                    label: `<strong>${item.nombre}</strong>`,
                    valor: `$${item.total.toLocaleString('es-MX')}`,
                    badgeStyle: 'background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3);'
                }));
            }
            if (topDivs.copes) {
                topDivs.copes.innerHTML = renderList(dataTops.top_copes, (item) => ({
                    label: `<strong>${item.cope}</strong>`,
                    valor: `${item.cantidad} reps`,
                    badgeStyle: 'background:rgba(139,92,246,0.15); color:#a78bfa; border:1px solid rgba(139,92,246,0.3);'
                }));
            }
        }

        // Fetch Charts
        const responseCharts = await fetch(`/api/analitica/charts?period=${period}`);
        const dataCharts = await responseCharts.json();

        if (dataCharts.status === 'success') {
            // Paleta corporativa armonizada con Telnor Green y acentos del sistema
            const corporatePalette = [
                '#40916c', // Telnor Green
                '#0ea5e9', // Sky Blue
                '#f59e0b', // Amber
                '#8b5cf6', // Purple
                '#ef4444', // Red
                '#06b6d4', // Cyan
                '#10b981', // Emerald
                '#f97316', // Orange
                '#14b8a6', // Teal
                '#ec4899'  // Pink
            ];

            // Destruir instancias previas para evitar memory leaks y parpadeos
            if(window.chartPieEstados) window.chartPieEstados.destroy();
            if(window.chartPieMant) window.chartPieMant.destroy();
            if(window.chartPieCopes) window.chartPieCopes.destroy();
            if(window.chartPieDeptos) window.chartPieDeptos.destroy();
            if(window.chartBarMeses) window.chartBarMeses.destroy();
            if(window.chartBarTalleres) window.chartBarTalleres.destroy();
            if(window.chartBarMarcas) window.chartBarMarcas.destroy();
            if(window.chartBarUnidadesDinero) window.chartBarUnidadesDinero.destroy();

            // Opciones comunes para gráficos circulares
            const pieChartOptions = {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            font: { family: "'Poppins', sans-serif", size: 11, weight: '500' },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 12
                        }
                    }
                }
            };

            // Opciones comunes para gráficos de barras
            const barChartOptions = (isHoriz = false) => ({
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(31, 57, 90, 0.45)', borderColor: '#1f395a' },
                        ticks: { color: '#94a3b8', font: { family: "'Poppins', sans-serif", size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(31, 57, 90, 0.45)', borderColor: '#1f395a' },
                        ticks: { color: '#94a3b8', font: { family: "'Poppins', sans-serif", size: 11 } }
                    }
                }
            });

            // Pie 1: Estados
            const ctxPieEstados = document.getElementById('chart-pie-estados').getContext('2d');
            window.chartPieEstados = new Chart(ctxPieEstados, {
                type: 'pie',
                data: {
                    labels: dataCharts.pie_estados.labels,
                    datasets: [{
                        data: dataCharts.pie_estados.data,
                        backgroundColor: corporatePalette,
                        borderColor: '#112641',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: pieChartOptions
            });

            // Pie 2: Mantenimiento
            const ctxPieMant = document.getElementById('chart-pie-mant').getContext('2d');
            window.chartPieMant = new Chart(ctxPieMant, {
                type: 'doughnut',
                data: {
                    labels: dataCharts.pie_mantenimiento.labels,
                    datasets: [{
                        data: dataCharts.pie_mantenimiento.data,
                        backgroundColor: corporatePalette.slice(2).concat(corporatePalette),
                        borderColor: '#112641',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: pieChartOptions
            });

            // Pie 3: COPEs
            const ctxPieCopes = document.getElementById('chart-pie-copes').getContext('2d');
            window.chartPieCopes = new Chart(ctxPieCopes, {
                type: 'pie',
                data: {
                    labels: dataCharts.pie_copes.labels,
                    datasets: [{
                        data: dataCharts.pie_copes.data,
                        backgroundColor: corporatePalette.slice(4).concat(corporatePalette),
                        borderColor: '#112641',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: pieChartOptions
            });

            // Pie 4: Departamentos
            const ctxPieDeptos = document.getElementById('chart-pie-deptos').getContext('2d');
            window.chartPieDeptos = new Chart(ctxPieDeptos, {
                type: 'doughnut',
                data: {
                    labels: dataCharts.pie_deptos.labels,
                    datasets: [{
                        data: dataCharts.pie_deptos.data,
                        backgroundColor: corporatePalette.slice(5).concat(corporatePalette),
                        borderColor: '#112641',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: pieChartOptions
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
                        backgroundColor: '#40916c',
                        borderColor: '#2d6a4f',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: barChartOptions(false)
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
                        backgroundColor: '#0ea5e9',
                        borderColor: '#0284c7',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: barChartOptions(false)
            });

            // Bar 3: Marcas/Modelos Fallas (Horizontal)
            const ctxBarMarcas = document.getElementById('chart-bar-marcas').getContext('2d');
            window.chartBarMarcas = new Chart(ctxBarMarcas, {
                type: 'bar',
                data: {
                    labels: dataCharts.bar_marcas.labels,
                    datasets: [{
                        label: 'Tickets',
                        data: dataCharts.bar_marcas.data,
                        backgroundColor: '#f59e0b',
                        borderColor: '#d97706',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    ...barChartOptions(true),
                    indexAxis: 'y'
                }
            });

            // Bar 4: Unidades que mas gastan (Horizontal)
            const ctxBarUnidadesDinero = document.getElementById('chart-bar-unidades-dinero').getContext('2d');
            window.chartBarUnidadesDinero = new Chart(ctxBarUnidadesDinero, {
                type: 'bar',
                data: {
                    labels: dataCharts.bar_unidades_dinero.labels,
                    datasets: [{
                        label: 'Gasto Total ($)',
                        data: dataCharts.bar_unidades_dinero.data,
                        backgroundColor: '#ef4444',
                        borderColor: '#dc2626',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    ...barChartOptions(true),
                    indexAxis: 'y'
                }
            });
        }

    } catch (error) {
        console.error("Error cargando analitica:", error);
        for (let key in divs) {
            if (divs[key] && divs[key].innerHTML.includes('Cargando')) divs[key].innerHTML = '<span style="color:#ef4444;">Error de conexión</span>';
        }
    }
}

