from django.shortcuts import render
from monitoreo.models import Dato
from django.db import connection

def index(request):
    # Verificar si la columna raw_payload existe, y agregarla si no existe
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(monitoreo_dato)")
    columns = [col[1] for col in cursor.fetchall()]
    has_raw_payload = 'raw_payload' in columns
    
    # Si no existe la columna, agregarla automáticamente
    if not has_raw_payload:
        try:
            cursor.execute("ALTER TABLE monitoreo_dato ADD COLUMN raw_payload TEXT NULL")
            connection.commit()
            # Registrar la migración como aplicada
            from django.db.migrations.recorder import MigrationRecorder
            from django.apps import apps
            MigrationRecorder.Migration.objects.get_or_create(
                app='monitoreo',
                name='0002_dato_raw_payload'
            )
            has_raw_payload = True
        except Exception as e:
            # Si falla, continuar sin la columna
            pass
    
    # Obtener lista de municipios únicos
    try:
        municipios = Dato.objects.values_list('municipio', flat=True).distinct().order_by('municipio')
    except Exception:
        municipios = []
    
    # Obtener últimos 20 registros para la tabla
    try:
        ultimos_datos = Dato.objects.all().order_by('-timestamp')[:20]
    except Exception:
        ultimos_datos = []
    
    context = {
        'municipios': municipios,
        'ultimos_datos': ultimos_datos,
        'has_raw_payload': has_raw_payload,
    }
    return render(request, 'dashboard/index.html', context)
