#!/usr/bin/python3
import json
import threading
from datetime import datetime
import time
import subprocess
from decouple import config
import requests



# Webex Configuration
WEBEX_ACCESS_TOKEN = config("WEBEX_ACCESS_TOKEN")
WEBEX_ROOM_ID = config("WEBEX_ROOM_ID")
MAX_PENDENTS = 50   # màxim d'alertes encuades per dispositiu mentre no hi ha connectivitat
# ------------------------------------

print(f"\n###############\nWebex Room ID: {WEBEX_ROOM_ID}\n##############", flush=True)


def enviar_alerta_webex(mensaje):
    """Envía un mensaje a un chat de Webex a través de un bot. Retorna True si se ha entregado."""
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": WEBEX_ROOM_ID,
        "text": mensaje
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Alerta enviada a Webex. Room ID: {WEBEX_ROOM_ID}", flush=True)
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}", flush=True)
        if response.status_code == 401:
            print("Check your Webex Access Token. It might be invalid or expired.", flush=True)
        elif response.status_code == 404:
            print("Check the Webex Room ID. It might not exist or the bot doesn't have access to it.", flush=True)
        print(f"Response content: {response.text}", flush=True)
    except requests.exceptions.RequestException as req_err:
        print(f"Error enviando alerta a Webex: {req_err}", flush=True)
    return False


def true_false_ping(ip):
    reply = subprocess.run(
            ['ping', '-c', '3', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
    )
    return reply.returncode == 0



def doPings( obj ):

    # Para saber el estado inicial y no enviar alertas al arrancar
    # Hacemos un primer ping para establecer el estado inicial
    # swResposta = true_false_ping( obj["ip"] )
    print(f'Iniciando monitoreo para {obj["descripcio"]} ({obj["ip"]})', flush=True)    # . Estado inicial: {"OK" if swResposta else "DOWN"}

    swResposta = True  # a l'arrancar no mostra cap missatge si ping = True la primera vegada
    # comptador = 1

    # Missatges detectats però encara no entregats a Webex (p.ex. perquè la caiguda
    # també ens ha deixat sense DNS). Guarden l'hora real del canvi d'estat.
    pendents = []

    while True:
        # print( "comptador: ", comptador )
        resposta = true_false_ping( obj["ip"] ) 

        if resposta != swResposta:
            moment = str(datetime.now())[:-7]
            estat = "🟢 UP" if resposta else "🔴 DOWN"
            print ( f"ping { obj["ip"] } - { obj["descripcio"] } ...: {estat} \t {moment}", flush=True )
            pendents.append( f"{ obj["descripcio"] }:\n{estat} \t {moment}" )
            if len( pendents ) > MAX_PENDENTS:
                pendents.pop(0)   # no deixem créixer la cua sense límit
            swResposta = resposta

        # Intenta entregar els pendents en ordre. Si falla, es conserven per al proper cicle.
        while pendents:
            if not enviar_alerta_webex( pendents[0] ):
                print ( f"{ obj["descripcio"] }: {len(pendents)} alerta(es) pendent(s) d'enviar", flush=True )
                break
            pendents.pop(0)

        time.sleep(30)   # 30 segons

        # comptador += 1


with open('/home/jordi/projectes/python/pings2nPla/LlistaIPs.json') as user_file:
    strllistaIPs = user_file.read()
    jsonLlistaIPs = json.loads( strllistaIPs )


for obj in jsonLlistaIPs:
    threading.Thread(target=doPings, args=( obj, )).start()


