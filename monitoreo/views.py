from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
import json
from datetime import datetime, timedelta
from .models import Dato

@csrf_exempt
def recibir_dato(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"})

    try:
        # Leer JSON enviado por mqtt_bridge.py
        data = json.loads(request.body.decode("utf-8"))

        municipio = data.get("ciudad")
        tipo = data.get("tipo")
        valor = data.get("valor")

        if not municipio or not tipo or valor is None:
            return JsonResponse({"error": "Faltan datos"})

        # Convertir valor a número si se puede
        try:
            valor = float(valor)
        except:
            pass  # Si no es número, lo dejamos como texto

        Dato.objects.create(
            municipio=municipio,
            tipo=tipo,
            valor=valor
        )

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)})


def api_data(request):
    """Endpoint legacy para compatibilidad - retorna últimos valores de cada tipo"""
    from django.core.cache import cache
    
    # Intentar obtener de cache primero (más rápido)
    data = {
        "temperatura": cache.get("sensor_temperatura"),
        "humedad": cache.get("sensor_humedad"),
        "calidad": cache.get("sensor_calidad"),
        "iluminacion": cache.get("sensor_iluminacion"),
    }
    
    # Si no hay en cache, obtener de la BD
    if data["temperatura"] is None:
        ultimo_temp = Dato.objects.filter(tipo="temperatura").order_by("-timestamp").first()
        if ultimo_temp:
            data["temperatura"] = ultimo_temp.valor

    if data["humedad"] is None:
        ultimo_hum = Dato.objects.filter(tipo="humedad").order_by("-timestamp").first()
        if ultimo_hum:
            data["humedad"] = ultimo_hum.valor

    if data["calidad"] is None:
        ultimo_cal = Dato.objects.filter(tipo="calidad").order_by("-timestamp").first()
        if ultimo_cal:
            data["calidad"] = ultimo_cal.valor

    if data["iluminacion"] is None:
        ultimo_ilu = Dato.objects.filter(tipo="iluminacion").order_by("-timestamp").first()
        if ultimo_ilu:
            data["iluminacion"] = ultimo_ilu.valor

    return JsonResponse(data)


@require_http_methods(["GET"])
def api_latest(request):
    """
    Endpoint: /api/latest/
    Retorna los últimos datos de sensores.
    Filtros opcionales: ?municipio=<nombre>
    """
    municipio = request.GET.get('municipio')
    
    # Construir query
    query = Dato.objects.all()
    if municipio:
        query = query.filter(municipio=municipio)
    
    # Obtener últimos datos por tipo y municipio
    datos = []
    tipos = ['temperatura', 'humedad', 'calidad', 'iluminacion']
    
    for tipo in tipos:
        tipo_query = query.filter(tipo=tipo)
        if municipio:
            tipo_query = tipo_query.filter(municipio=municipio)
        
        ultimo = tipo_query.order_by('-timestamp').first()
        if ultimo:
            datos.append({
                'municipio': ultimo.municipio,
                'tipo': ultimo.tipo,
                'valor': ultimo.valor,
                'timestamp': ultimo.timestamp.isoformat(),
                'raw_payload': getattr(ultimo, 'raw_payload', None)
            })
    
    return JsonResponse({
        'count': len(datos),
        'data': datos
    })


@require_http_methods(["GET"])
def api_history(request):
    """
    Endpoint: /api/history/
    Retorna histórico de datos.
    Filtros opcionales: 
        ?municipio=<nombre>
        ?tipo=<temperatura|humedad|calidad|iluminacion>
        ?limit=<número> (default: 100)
        ?hours=<número> (últimas N horas)
    """
    municipio = request.GET.get('municipio')
    tipo = request.GET.get('tipo')
    limit = int(request.GET.get('limit', 100))
    hours = request.GET.get('hours')
    
    # Construir query
    query = Dato.objects.all()
    
    if municipio:
        query = query.filter(municipio=municipio)
    
    if tipo:
        query = query.filter(tipo=tipo)
    
    if hours:
        try:
            hours_int = int(hours)
            desde = datetime.now() - timedelta(hours=hours_int)
            query = query.filter(timestamp__gte=desde)
        except ValueError:
            pass
    
    # Ordenar y limitar
    datos = query.order_by('-timestamp')[:limit]
    
    # Serializar
    datos_list = []
    for dato in datos:
        datos_list.append({
            'id': dato.id,
            'municipio': dato.municipio,
            'tipo': dato.tipo,
            'valor': dato.valor,
            'timestamp': dato.timestamp.isoformat(),
            'raw_payload': getattr(dato, 'raw_payload', None)
        })
    
    return JsonResponse({
        'count': len(datos_list),
        'limit': limit,
        'data': datos_list
    })
