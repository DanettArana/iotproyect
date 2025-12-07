# Script temporal para subir todos los cambios a GitHub
cd $PSScriptRoot

Write-Host "Verificando estado de git..." -ForegroundColor Cyan
git status

Write-Host "`nAgregando todos los archivos modificados..." -ForegroundColor Cyan
git add -A

Write-Host "`nEstado después de agregar archivos:" -ForegroundColor Cyan
git status

Write-Host "`nCreando commit..." -ForegroundColor Cyan
git commit -m "Update: Actualizar proyecto completo con corrección de caché"

Write-Host "`nSubiendo cambios a GitHub..." -ForegroundColor Cyan
git push origin master

Write-Host "`n¡Completado!" -ForegroundColor Green
git log --oneline -1
