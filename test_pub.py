#!/usr/bin/env python3
"""
Script de prueba para publicar datos MQTT al broker
Simula sensores IoT enviando datos al tópico sonora/{municipio}/{tipo}

Uso:
    python test_pub.py
"""

import paho.mqtt.client as mqtt
import time
import random
import json

# Configuración
BROKER = "localhost"  # Cambiar a test.mosquitto.org si no tienes broker local
PORT = 1883
TOPIC_BASE = "sonora"

# Municipios y tipos de sensores
MUNICIPIOS = ["Hermosillo", "Ciudad Obregon", "Nogales", "San Luis Rio Colorado"]
TIPOS = ["temperatura", "humedad", "calidad", "iluminacion"]

def publicar_dato(client, municipio, tipo, valor, formato="simple"):
    """
    Publica un dato MQTT en diferentes formatos
    formato: "simple", "json", o "delimitado"
    """
    topic = f"{TOPIC_BASE}/{municipio}/{tipo}"
    
    if formato == "json":
        # Formato JSON
        payload = json.dumps({
            "valor": valor,
            "tipo": tipo,
            "municipio": municipio,
            "unidad": "C" if tipo == "temperatura" else ("%" if tipo == "humedad" else "ppm" if tipo == "calidad" else "lux")
        })
    elif formato == "delimitado":
        # Formato delimitado por ;
        payload = f"{municipio};{tipo};{valor};{int(time.time())}"
    else:
        # Formato simple (solo el valor)
        payload = str(valor)
    
    client.publish(topic, payload)
    print(f"Publicado: {topic} = {payload}")

def main():
    print("Iniciando publicador de datos MQTT de prueba")
    print(f"Conectando a {BROKER}:{PORT}...")
    
    # Crear cliente MQTT
    client = mqtt.Client()
    
    try:
        client.connect(BROKER, PORT, 60)
        print("Conectado al broker MQTT")
    except Exception as e:
        print(f"Error al conectar: {e}")
        print("Asegúrate de que el broker MQTT esté ejecutándose")
        return
    
    client.loop_start()
    
    print("\nPublicando datos... (Ctrl+C para detener)\n")
    
    try:
        contador = 0
        while True:
            municipio = random.choice(MUNICIPIOS)
            tipo = random.choice(TIPOS)
            
            # Generar valores realistas según el tipo
            if tipo == "temperatura":
                valor = round(random.uniform(20, 45), 2)  # 20-45°C
            elif tipo == "humedad":
                valor = round(random.uniform(30, 80), 2)  # 30-80%
            elif tipo == "calidad":
                valor = round(random.uniform(50, 200), 2)  # 50-200 ppm
            else:  # iluminacion
                valor = round(random.uniform(100, 1000), 0)  # 100-1000 lux
            
            # Alternar entre formatos
            formato = random.choice(["simple", "json", "delimitado"])
            publicar_dato(client, municipio, tipo, valor, formato)
            
            contador += 1
            time.sleep(2)  # Publicar cada 2 segundos
            
    except KeyboardInterrupt:
        print("\n\nDeteniendo publicador...")
        client.loop_stop()
        client.disconnect()
        print(f"Total de mensajes publicados: {contador}")

if __name__ == "__main__":
    main()
