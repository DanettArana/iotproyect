# Script para crear Pull Request en GitHub
cd $PSScriptRoot

$branchName = "danettarana-fix-cache"
$baseBranch = "master"
$repoOwner = "Daithniz"
$repoName = "iotproyect"
$prTitle = "Fix: Corregir inconsistencia en claves de caché entre mqtt_client y views"
$prBody = @"
## Descripción
Este PR corrige una inconsistencia en las claves de caché entre `mqtt_client.py` y `views.py`.

## Problema
- El MQTT client creaba claves de caché con formato `sensor_{municipio}_{tipo}` (incluye municipio)
- El endpoint `api_data()` intentaba recuperarlas usando solo `sensor_{tipo}` (sin municipio)
- Esto causaba que los valores en caché nunca se encontraran, generando consultas innecesarias a la BD

## Solución
El cliente MQTT ahora guarda claves de caché en ambos formatos:
- `sensor_{municipio}_{tipo}` - para consultas específicas por municipio
- `sensor_{tipo}` - para compatibilidad con el endpoint legacy `api_data()`

## Archivos modificados
- `dashboard/mqtt_client.py` - Actualizado para guardar claves en ambos formatos
"@

Write-Host "Intentando crear Pull Request..." -ForegroundColor Cyan

# Intentar usar GitHub CLI primero
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "Usando GitHub CLI (gh)..." -ForegroundColor Green
    gh pr create --base $baseBranch --head $branchName --title $prTitle --body $prBody
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n¡Pull Request creado exitosamente!" -ForegroundColor Green
        exit 0
    }
}

# Si GitHub CLI no está disponible, abrir navegador
Write-Host "GitHub CLI no está disponible. Abriendo navegador..." -ForegroundColor Yellow

# Abrir el navegador con la URL para crear el PR
$prUrl = "https://github.com/$repoOwner/$repoName/compare/$baseBranch...$branchName"
Write-Host "`nAbriendo navegador para crear el PR..." -ForegroundColor Cyan
Write-Host "URL: $prUrl" -ForegroundColor Green
Start-Process $prUrl

Write-Host "`nCuando se abra el navegador, GitHub te pedirá:" -ForegroundColor Yellow
Write-Host "1. Título del PR: $prTitle" -ForegroundColor White
Write-Host "2. Descripción: (ya está preparada en el script)" -ForegroundColor White
Write-Host "`nPresiona Enter para ver la descripción completa del PR..." -ForegroundColor Cyan
Read-Host

Write-Host "`nDescripción sugerida para el PR:" -ForegroundColor Cyan
Write-Host $prBody -ForegroundColor White
