import paho.mqtt.client as mqtt
from monitoreo.models import Dato
from threading import Thread
import time
import json
from django.core.cache import cache
from django.conf import settings

# Configuración desde settings.py
BROKER = getattr(settings, 'MQTT_BROKER', 'localhost')
PORT = getattr(settings, 'MQTT_PORT', 1883)
TOPIC = getattr(settings, 'MQTT_TOPIC', 'sonora/#')
MQTT_USERNAME = getattr(settings, 'MQTT_USERNAME', None)
MQTT_PASSWORD = getattr(settings, 'MQTT_PASSWORD', None)
RECONNECT_DELAY = 5  # segundos entre intentos de reconexión


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT conectado exitosamente. Código:", rc)
        print(f"Broker: {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"Suscrito a: {TOPIC}")
    else:
        print(f"Error de conexión MQTT. Código:", rc)


def on_disconnect(client, userdata, rc):
    print(f"MQTT desconectado. Código: {rc}")
    if rc != 0:
        print(f"Intentando reconectar en {RECONNECT_DELAY} segundos...")
        time.sleep(RECONNECT_DELAY)
        try:
            client.reconnect()
        except Exception as e:
            print(f"Error al reconectar: {e}")


def on_message(client, userdata, msg):
    try:
        payload_raw = msg.payload.decode().strip()
        print("MQTT recibido:", msg.topic, payload_raw)

        # Tópico: sonora/<municipio>/<tipo>
        parts = msg.topic.split("/")
        if len(parts) < 3:
            print("Formato de tópico inválido:", msg.topic)
            return

        municipio = parts[1]
        tipo = parts[2]  # temperatura | humedad | calidad | iluminacion
        
        # Solo procesar tipos de sensores válidos
        tipos_validos = ["temperatura", "humedad", "calidad", "iluminacion"]
        
        if tipo not in tipos_validos:
            print(f"Ignorando tipo de sensor no válido: {tipo}")
            return

        # Intentar parsear como JSON primero
        valor = None
        try:
            data_json = json.loads(payload_raw)
            # Si es JSON, puede venir como objeto con campos
            if isinstance(data_json, dict):
                valor = data_json.get('valor') or data_json.get('value') or data_json.get(tipo)
                # Si no encuentra valor directo, intentar obtener el valor numérico del objeto
                if valor is None:
                    for key, val in data_json.items():
                        if isinstance(val, (int, float)):
                            valor = val
                            break
            elif isinstance(data_json, (int, float)):
                valor = data_json
        except (json.JSONDecodeError, ValueError):
            # Si no es JSON, intentar formato delimitado por ;
            if ";" in payload_raw:
                parts_payload = payload_raw.split(";")
                # Buscar un valor numérico en las partes
                for part in parts_payload:
                    try:
                        valor = float(part.strip())
                        break
                    except ValueError:
                        continue
            else:
                # Último intento: tratar como valor numérico directo
                try:
                    valor = float(payload_raw)
                except ValueError:
                    # Ignorar mensajes no numéricos (como "offline", "Buena", "status", etc.)
                    print(f"Ignorando mensaje no numérico: {msg.topic} = '{payload_raw}'")
                    return

        if valor is None:
            print(f"No se pudo extraer valor numérico de: {payload_raw}")
            return

        # Guardar en caché de Django (para mostrar en el dashboard)
        # Clave con municipio (para consultas específicas)
        cache_key_municipio = f"sensor_{municipio}_{tipo}"
        cache.set(cache_key_municipio, valor, timeout=300)  # 5 minutos de expiración
        print(f"Guardado en cache: {cache_key_municipio} = {valor}")
        
        # Clave sin municipio (para compatibilidad con api_data legacy)
        # Solo actualizar si no existe o si este es el valor más reciente
        cache_key_legacy = f"sensor_{tipo}"
        cache.set(cache_key_legacy, valor, timeout=300)  # 5 minutos de expiración
        print(f"Guardado en cache (legacy): {cache_key_legacy} = {valor}")

        # Guardar en BD con raw_payload (si el campo existe)
        try:
            Dato.objects.create(
                municipio=municipio, 
                tipo=tipo, 
                valor=valor,
                raw_payload=payload_raw
            )
        except Exception as db_error:
            # Si raw_payload no existe, crear sin ese campo
            if 'raw_payload' in str(db_error):
                Dato.objects.create(
                    municipio=municipio, 
                    tipo=tipo, 
                    valor=valor
                )
            else:
                raise
        print(f"Dato guardado: {municipio} - {tipo}: {valor}")

    except Exception as e:
        print(f"Error MQTT: {e}")


def start():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    # Configurar autenticación si está definida
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        print(f"Autenticación MQTT configurada para usuario: {MQTT_USERNAME}")
    
    # Configurar reconexión automática
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    
    while True:
        try:
            print(f"Conectando al broker MQTT: {BROKER}:{PORT}...")
            client.connect(BROKER, PORT, 60)
            client.loop_forever()
        except Exception as e:
            print(f"Error de conexión: {e}")
            print(f"Reintentando en {RECONNECT_DELAY} segundos...")
            time.sleep(RECONNECT_DELAY)


def run():
    t = Thread(target=start)
    t.daemon = True
    t.start()
    print("Cliente MQTT iniciado en segundo plano")
