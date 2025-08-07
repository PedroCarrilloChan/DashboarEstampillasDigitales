<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Estampillas Digitales</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #0d1117; /* Fondo oscuro */
            color: #e5e7eb; /* Texto principal claro */
        }
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 0;
        }
        .dashboard-container {
            position: relative;
            z-index: 1;
        }
        /* Efecto Glassmorphism */
        .card { 
            background-color: rgba(31, 41, 55, 0.6); /* Fondo semi-transparente */
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 1rem; 
            padding: 1.5rem; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            background-color: rgba(31, 41, 55, 0.8);
        }
        .kpi-title { color: #9ca3af; font-weight: 600; }
        .kpi-value { color: #ffffff; font-weight: 800; font-size: 2.25rem; line-height: 2.5rem; }
        .kpi-trend-up { color: #34d399; }
        .kpi-trend-down { color: #f87171; }
        .text-gradient {
            background: linear-gradient(90deg, #38bdf8, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        /* Estilos para el calendario */
        input[type="date"] {
            background-color: rgba(31, 41, 55, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e5e7eb;
            border-radius: 0.5rem;
        }
        input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(1);
        }
    </style>
</head>
<body class="p-4 sm:p-6">

    <div id="particles-js"></div>

    <div id="dashboard-content" class="max-w-7xl mx-auto dashboard-container">

        <!-- Encabezado con Calendario -->
        <header class="mb-8">
            <div class="flex flex-wrap justify-between items-center gap-4">
                <div>
                    <h1 class="text-3xl font-extrabold text-gradient">Dashboard de Lealtad por Estampillas</h1>
                    <p class="text-lg text-gray-400 mt-1">Mostrando datos para: <span id="current_date_display" class="font-semibold text-gray-300"></span></p>
                </div>
                <div class="flex items-center gap-2">
                    <input type="date" id="date_picker" class="p-2.5">
                    <button id="fetch_button" class="bg-blue-600 text-white font-semibold rounded-lg p-2.5 hover:bg-blue-700 transition-colors">Consultar</button>
                </div>
            </div>
        </header>

        <!-- Fila de KPIs Principales -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="card">
                <p class="kpi-title">Total de Miembros</p>
                <p class="kpi-value" id="total_members">...</p>
            </div>
            <div class="card">
                <p class="kpi-title">Pases Instalados</p>
                <p class="kpi-value" id="passes_installed">...</p>
            </div>
            <div class="card">
                <p class="kpi-title">Estampillas Dadas</p>
                <p class="kpi-value" id="stamps_given">...</p>
            </div>
        </div>

        <!-- Fila de Análisis de Clientes y Plataformas -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <!-- Clientes Recurrentes -->
            <div class="card">
                <p class="kpi-title mb-2">Clientes Recurrentes</p>
                <div class="flex items-baseline">
                    <p class="kpi-value" id="recurring_customers">...</p>
                    <p class="ml-2 font-semibold" id="recurring_trend">...</p>
                </div>
                <p class="text-sm text-gray-400">Comparado con el mes pasado.</p>
            </div>
            <!-- Adopción -->
            <div class="card flex flex-col justify-center">
                <p class="kpi-title text-center mb-4">Tasa de Adopción de Pases</p>
                <div class="relative w-40 h-40 mx-auto">
                    <svg class="w-full h-full" viewBox="0 0 36 36">
                        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255, 255, 255, 0.1)" stroke-width="3.8" />
                        <path id="adoption_donut" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#3b82f6" stroke-width="3.8" stroke-dasharray="0, 100" stroke-linecap="round" />
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center">
                        <span class="text-3xl font-bold text-white" id="adoption_percentage">...%</span>
                    </div>
                </div>
            </div>
            <!-- Plataformas -->
            <div class="card">
                <p class="kpi-title text-center mb-4">Desglose por Plataforma</p>
                <div class="space-y-4">
                    <div class="flex items-center">
                        <p class="w-20 font-semibold text-gray-300">iPhone</p>
                        <div class="w-full bg-gray-700 rounded-full h-4">
                            <div id="iphone_bar" class="bg-gray-200 h-4 rounded-full" style="width: 0%"></div>
                        </div>
                        <p id="iphone_installs" class="w-16 text-right font-bold text-white">...</p>
                    </div>
                    <div class="flex items-center">
                        <p class="w-20 font-semibold text-gray-300">Android</p>
                        <div class="w-full bg-gray-700 rounded-full h-4">
                            <div id="android_bar" class="bg-green-400 h-4 rounded-full" style="width: 0%"></div>
                        </div>
                        <p id="android_installs" class="w-16 text-right font-bold text-white">...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Fila de Canales y Rendimiento -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Canales de Adquisición -->
            <div class="card">
                <p class="kpi-title mb-4">Canales de Adquisición</p>
                <div id="channels_container" class="space-y-3"></div>
            </div>
            <!-- Rendimiento del Programa -->
            <div class="card">
                 <p class="kpi-title mb-4">Rendimiento del Programa</p>
                 <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                     <div>
                         <p class="text-sm text-gray-400">Tarjetas Llenadas</p>
                         <p class="text-2xl font-bold text-white" id="completed_cards">...