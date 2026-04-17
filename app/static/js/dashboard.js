// Espera a que todo el HTML esté cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", function () {

    console.log("dashboard.js cargado.");

    /**
     * Función para procesar los datos que vienen de Python.
     * (Python nos da: [{'nivel': 'Crítica', 'total': 1}, {'nivel': 'Alta', 'total': 2}, ...])
     * (Chart.js quiere: { labels: ['Crítica', 'Alta'], data: [1, 2] })
     */
    function procesarDatosParaGrafica(datosCrudos) {
        const etiquetas = [];
        const valores = [];

        // 'datosCrudos' es la variable que pasamos desde el index.html
        if (!datosCrudos || datosCrudos.length === 0) {
            console.warn("No hay datos para esta gráfica.");
            return { etiquetas: ["Sin datos"], valores: [0] };
        }

        // Usamos .forEach para separar los datos en dos arrays
        datosCrudos.forEach(item => {
            // El nombre de la propiedad debe coincidir con tu consulta SQL
            // (Usamos 'nivel' para prioridad y 'nombre' para tipo)
            etiquetas.push(item.nivel || item.nombre);
            valores.push(item.total);
        });

        return { etiquetas, valores };
    }

    // --- GRÁFICA 1: PRIORIDAD ---
    try {
        // 'datosPrioridad' es el ID de la variable <script> en index.html
        const datosGraficaPrioridad = procesarDatosParaGrafica(datosPrioridad);

        const ctxPrioridad = document.getElementById('graficaPrioridad');

        if (ctxPrioridad) {
            new Chart(ctxPrioridad.getContext('2d'), {
                type: 'doughnut', // Tipo de gráfica (dona)
                data: {
                    labels: datosGraficaPrioridad.etiquetas,
                    datasets: [{
                        label: 'Incidentes por Prioridad',
                        data: datosGraficaPrioridad.valores,
                        backgroundColor: [
                            '#FF6384', // Crítica
                            '#FF9F40', // Alta
                            '#FFCD56', // Media
                            '#4BC0C0'  // Baja
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false, // <-- CLAVE: para que obedezca al CSS
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        } else {
            console.error("No se encontró el canvas #graficaPrioridad");
        }
    } catch (e) {
        console.error("Error al crear gráfica de Prioridad:", e);
        console.log("Datos de Prioridad recibidos:", typeof datosPrioridad, datosPrioridad);
    }


    // --- GRÁFICA 2: TIPO ---
    try {
        // 'datosTipo' es el ID de la variable <script> en index.html
        const datosGraficaTipo = procesarDatosParaGrafica(datosTipo);

        const ctxTipo = document.getElementById('graficaTipo');

        if (ctxTipo) {
            new Chart(ctxTipo.getContext('2d'), {
                type: 'pie', // Tipo de gráfica (pastel)
                data: {
                    labels: datosGraficaTipo.etiquetas,
                    datasets: [{
                        label: 'Incidentes por Tipo',
                        data: datosGraficaTipo.valores,
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCD56',
                            '#4BC0C0',
                            '#9966FF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false, // <-- CLAVE: para que obedezca al CSS
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        } else {
            console.error("No se encontró el canvas #graficaTipo");
        }
    } catch (e) {
        console.error("Error al crear gráfica de Tipo:", e);
        console.log("Datos de Tipo recibidos:", typeof datosTipo, datosTipo);
    }

    // --- GRÁFICA 3: TOP 10 ACTIVOS (Bar Chart) ---
    try {
        const etiquetasActivos = [];
        const valoresActivos = [];

        if (typeof datosTopActivos !== 'undefined' && datosTopActivos.length > 0) {
            datosTopActivos.forEach(item => {
                etiquetasActivos.push(item.hostname);
                valoresActivos.push(item.total_incidentes);
            });
        } else {
            etiquetasActivos.push("Sin datos");
            valoresActivos.push(0);
        }

        const ctxTopActivos = document.getElementById('graficaTopActivos');

        if (ctxTopActivos) {
            new Chart(ctxTopActivos.getContext('2d'), {
                type: 'bar', // Gráfica de barras
                data: {
                    labels: etiquetasActivos,
                    datasets: [{
                        label: 'Número de Incidentes',
                        data: valoresActivos,
                        backgroundColor: '#8b5cf6', // purple-500
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error al crear gráfica de Top Activos:", e);
    }

});