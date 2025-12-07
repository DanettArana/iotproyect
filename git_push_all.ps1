# Script para crear branch nuevo y subir cambios a GitHub
cd $PSScriptRoot

$branchName = "danettarana-fix-cache"

Write-Host "Verificando estado de git..." -ForegroundColor Cyan
git status

Write-Host "`nCreando nuevo branch: $branchName" -ForegroundColor Cyan
git checkout -b $branchName

Write-Host "`nAgregando todos los archivos modificados..." -ForegroundColor Cyan
git add -A

Write-Host "`nEstado después de agregar archivos:" -ForegroundColor Cyan
git status

Write-Host "`nCreando commit..." -ForegroundColor Cyan
git commit -m "Fix: Corregir inconsistencia en claves de caché entre mqtt_client y views"

Write-Host "`nSubiendo branch nuevo a GitHub..." -ForegroundColor Cyan
git push -u origin $branchName

Write-Host "`n¡Completado!" -ForegroundColor Green
Write-Host "Branch '$branchName' creado y subido exitosamente." -ForegroundColor Green
Write-Host "Ahora puedes crear un Pull Request en GitHub para que Daithniz revise los cambios." -ForegroundColor Yellow
git log --oneline -1
