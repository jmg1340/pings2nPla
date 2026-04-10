#!/usr/bin/python3
import json
import threading
from datetime import datetime
import time
import subprocess
from decouple import config
import requests



# --- Sustituye esto con tus datos ---
# AQUÍ_VA_EL_TOKEN_DE_TU_BOT
TOKEN_TELEGRAM = config("TOKEN_TELEGRAM")

# CHAT_ID_TELEGRAM 
CHAT_IDS_TELEGRAM = config("CHAT_IDS_TELEGRAM").split(",")
# ------------------------------------

print(f"\n###############\n{CHAT_IDS_TELEGRAM}\n##############")


def enviar_alerta_telegram(mensaje):
    """Envía un mensaje a un chat de Telegram a través de un bot."""


    for chatID in CHAT_IDS_TELEGRAM:

        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage?chat_id={chatID}&text={mensaje}"
        try:
            # Hacemos la petición a la API de Telegram
            requests.get(url)
            print(f"Alerta enviada a Telegram. ChatID: {chatID}")
        except Exception as e:
            print(f"Error enviando alerta a Telegram: {e}")





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
    print(f'Iniciando monitoreo para {obj["descripcio"]} ({obj["ip"]})')    # . Estado inicial: {"OK" if swResposta else "DOWN"}

    swResposta = True  # a l'arrancar no mostra cap missatge si ping = True la primera vegada
    # comptador = 1

    while True:
        # print( "comptador: ", comptador )
        resposta = true_false_ping( obj["ip"] ) 

        if resposta != swResposta:
            if resposta:
                print ( f"ping { obj["ip"] } - { obj["descripcio"] } ...: 🟢 UP \t {str(datetime.now())[:-7]}" )
                enviar_alerta_telegram( f"{ obj["descripcio"] }:\n🟢 UP \t {str(datetime.now())[:-7]}" )
            else:
                print ( f"ping { obj["ip"] } - { obj["descripcio"] } ...: 🔴 DOWN \t {str(datetime.now())[:-7]}" )
                enviar_alerta_telegram( f"{ obj["descripcio"] }:\n🔴 DOWN \t {str(datetime.now())[:-7]}" )


        swResposta = resposta
        time.sleep(30)   # 30 segons

        # comptador += 1








with open('/home/jordi/projectes/python/pings2nPla/LlistaIPs.json') as user_file:
    strllistaIPs = user_file.read()
    jsonLlistaIPs = json.loads( strllistaIPs )


for obj in jsonLlistaIPs:
    threading.Thread(target=doPings, args=( obj, )).start()


