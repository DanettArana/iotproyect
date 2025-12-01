import json
import requests
import paho.mqtt.client as mqtt

API_URL = "http://127.0.0.1:8000/monitoreo/recibir/"

# Cuando conecta al broker
def on_connect(client, userdata, flags, rc):
    print("Conectado MQTT. Código:", rc)
    client.subscribe("sonora/sensores/#")   # suscribirse a todos los sensores
    print("Suscrito a: sonora/sensores/#")

# Cuando llega un mensaje MQTT
def on_message(client, userdata, msg):
    try:
        raw = msg.payload.decode()

        # Espera formato: ciudad | tipo | valor
        partes = [p.strip() for p in raw.split("|")]

        if len(partes) != 3:
            print("Formato inválido:", raw)
            return

        municipio, tipo, valor = partes

        print(f"Recibido MQTT → {municipio} | {tipo} | {valor}")

        payload = {
            "ciudad": municipio,
            "tipo": tipo,
            "valor": valor
        }

        r = requests.post(API_URL, json=payload)
        print("Respuesta Django:", r.text)

    except Exception as e:
        print("Error procesando mensaje:", e)


# -------------------
# CONFIGURACIÓN MQTT
# -------------------

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Conectando al broker...")
client.connect("broker.hivemq.com", 1883, 60)

print("Escuchando MQTT...")
client.loop_forever()
