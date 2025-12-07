# Script simple para abrir la página de creación del Pull Request
$prUrl = "https://github.com/Daithniz/iotproyect/compare/master...danettarana-fix-cache"

Write-Host "Abriendo página para crear Pull Request..." -ForegroundColor Cyan
Write-Host "URL: $prUrl" -ForegroundColor Green

Start-Process $prUrl

Write-Host "`nTítulo sugerido:" -ForegroundColor Yellow
Write-Host "Fix: Corregir inconsistencia en claves de caché entre mqtt_client y views" -ForegroundColor White

Write-Host "`nDescripción sugerida:" -ForegroundColor Yellow
Write-Host @"
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
"@ -ForegroundColor White
