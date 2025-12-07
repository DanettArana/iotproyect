# Script para iniciar Mosquitto
$mosquittoPath = "C:\Program Files\mosquitto\mosquitto.exe"
$configPath = "C:\Program Files\mosquitto\mosquitto.conf"

Write-Host "Verificando instalación de Mosquitto..." -ForegroundColor Cyan

if (Test-Path $mosquittoPath) {
    Write-Host "Mosquitto encontrado en: $mosquittoPath" -ForegroundColor Green
} else {
    Write-Host "No se encontró mosquitto.exe en: $mosquittoPath" -ForegroundColor Red
    exit 1
}

# Verificar si ya está corriendo
$process = Get-Process -Name "mosquitto" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Mosquitto ya está corriendo (PID: $($process.Id))" -ForegroundColor Yellow
    Write-Host "Mosquitto está listo para usar en localhost:1883" -ForegroundColor Green
    exit 0
}

# Verificar si el puerto 1883 está en uso
$port = Get-NetTCPConnection -LocalPort 1883 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "El puerto 1883 ya está en uso" -ForegroundColor Yellow
    Write-Host "Mosquitto (o otro broker MQTT) está listo para usar" -ForegroundColor Green
    exit 0
}

Write-Host "Iniciando Mosquitto..." -ForegroundColor Cyan

# Intentar iniciar como servicio primero
try {
    $service = Get-Service -Name "mosquitto" -ErrorAction SilentlyContinue
    if ($service) {
        if ($service.Status -eq "Stopped") {
            Start-Service -Name "mosquitto"
            Write-Host "Servicio Mosquitto iniciado" -ForegroundColor Green
            Start-Sleep -Seconds 2
            exit 0
        } else {
            Write-Host "Servicio Mosquitto ya está corriendo" -ForegroundColor Green
            exit 0
        }
    }
} catch {
    Write-Host "No se encontró servicio de Mosquitto, iniciando manualmente..." -ForegroundColor Yellow
}

# Iniciar manualmente
try {
    if (Test-Path $configPath) {
        Start-Process -FilePath $mosquittoPath -ArgumentList "-c", $configPath -WindowStyle Hidden
        Write-Host "Mosquitto iniciado con archivo de configuración" -ForegroundColor Green
    } else {
        Start-Process -FilePath $mosquittoPath -WindowStyle Hidden
        Write-Host "Mosquitto iniciado (sin archivo de configuración)" -ForegroundColor Green
    }
    
    Write-Host "Esperando 3 segundos para que Mosquitto inicie..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    # Verificar que esté corriendo
    $process = Get-Process -Name "mosquitto" -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Mosquitto está corriendo (PID: $($process.Id))" -ForegroundColor Green
        Write-Host "Listo para usar en localhost:1883" -ForegroundColor Green
    } else {
        Write-Host "Mosquitto se inició pero no se detecta el proceso" -ForegroundColor Yellow
        Write-Host "   Verifica manualmente si está funcionando" -ForegroundColor Yellow
    }
    
    # Verificar puerto
    $port = Get-NetTCPConnection -LocalPort 1883 -ErrorAction SilentlyContinue
    if ($port) {
        Write-Host "Puerto 1883 está activo" -ForegroundColor Green
    } else {
        Write-Host "Puerto 1883 no está activo aún, puede tardar unos segundos más" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Error al iniciar Mosquitto: $_" -ForegroundColor Red
    exit 1
}


