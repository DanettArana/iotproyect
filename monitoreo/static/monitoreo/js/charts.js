// ---------- VARIABLES GLOBALES ----------
let municipioFiltro = '';
let chart = null;

// ---------- INICIALIZAR GRÁFICA ----------
function initChart() {
    const ctx = document.getElementById('chart');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura (°C)',
                data: [],
                borderWidth: 3,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                y: { beginAtZero: false }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// ---------- FUNCIÓN PARA OBTENER DATOS ÚLTIMOS ----------
function refreshData() {
    let url = '/monitoreo/api/latest/';
    if (municipioFiltro) {
        url += `?municipio=${encodeURIComponent(municipioFiltro)}`;
    }

    fetch(url)
        .then(r => r.json())
        .then(d => {
            // Actualizar timestamp
            const now = new Date();
            document.getElementById('last-update').innerText = now.toLocaleTimeString('es-MX');

            // Inicializar valores en --
            document.getElementById('temp').innerText = "--";
            document.getElementById('hum').innerText = "--";
            document.getElementById('air').innerText = "--";
            document.getElementById('ilum').innerText = "--";

            // Procesar datos recibidos
            if (d.data && d.data.length > 0) {
                d.data.forEach(item => {
                    const tipo = item.tipo;
                    const valor = item.valor;
                    const municipio = item.municipio;

                    // Actualizar tarjetas según el tipo
                    if (tipo === 'temperatura') {
                        document.getElementById('temp').innerText = valor.toFixed(1) + "°C";
                        
                        // Agregar punto a gráfica
                        if (chart) {
                            const hora = new Date(item.timestamp).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
                            chart.data.labels.push(hora);
                            chart.data.datasets[0].data.push(valor);

                            // Limitar a 20 puntos
                            if (chart.data.labels.length > 20) {
                                chart.data.labels.shift();
                                chart.data.datasets[0].data.shift();
                            }

                            chart.update();
                        }
                    } else if (tipo === 'humedad') {
                        document.getElementById('hum').innerText = valor.toFixed(1) + "%";
                    } else if (tipo === 'calidad') {
                        document.getElementById('air').innerText = valor.toFixed(2) + " ppm";
                    } else if (tipo === 'iluminacion') {
                        document.getElementById('ilum').innerText = valor.toFixed(0) + " lux";
                    }
                });
            }
        })
        .catch(err => console.error("Error al obtener datos:", err));
}

// ---------- FUNCIÓN PARA ACTUALIZAR TABLA DE ÚLTIMOS DATOS ----------
function refreshTable() {
    let url = '/monitoreo/api/history/?limit=20';
    if (municipioFiltro) {
        url += `&municipio=${encodeURIComponent(municipioFiltro)}`;
    }

    fetch(url)
        .then(r => r.json())
        .then(d => {
            const tbody = document.getElementById('datos-table');
            
            if (d.data && d.data.length > 0) {
                tbody.innerHTML = d.data.map(item => {
                    const fecha = new Date(item.timestamp);
                    const fechaStr = fecha.toLocaleString('es-MX');
                    const payload = item.raw_payload ? 
                        (item.raw_payload.length > 50 ? item.raw_payload.substring(0, 50) + '...' : item.raw_payload) 
                        : '-';
                    
                    return `
                        <tr>
                            <td>${item.municipio}</td>
                            <td><span class="badge bg-primary">${item.tipo}</span></td>
                            <td><strong>${item.valor.toFixed(2)}</strong></td>
                            <td>${fechaStr}</td>
                            <td><small class="text-muted">${payload}</small></td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay datos disponibles</td></tr>';
            }
        })
        .catch(err => console.error("Error al obtener histórico:", err));
}

// ---------- MANEJAR CAMBIO DE FILTRO ----------
function initFilters() {
    const municipioFilter = document.getElementById('municipio-filter');
    if (municipioFilter) {
        municipioFilter.addEventListener('change', function() {
            municipioFiltro = this.value;
            
            // Reiniciar gráfica
            if (chart) {
                chart.data.labels = [];
                chart.data.datasets[0].data = [];
                chart.update();
            }
            
            // Actualizar datos
            refreshData();
            refreshTable();
        });
    }
}

// ---------- INICIALIZAR TODO ----------
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initChart();
        initFilters();
        refreshData();
        refreshTable();
        setInterval(refreshData, 3000);
        setInterval(refreshTable, 10000);
    });
} else {
    // DOM ya está cargado
    initChart();
    initFilters();
    refreshData();
    refreshTable();
    setInterval(refreshData, 3000);
    setInterval(refreshTable, 10000);
}
