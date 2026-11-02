
## PINGS EN SEGON PLA

### Pings a servidors i switchs executats com a servei en 2n pla en un SO linux. Quan es produeix un DOWN, envia missatge a Webex. El mateix quan recupera (UP)


> S'ha instal·lat el paquet python-decouple.

~~~ 
pip install python-decouple
~~~

S'han de definir els fitxers:
1. fitxer .env per posar pwds i demés
2. fitxer LlistaIPs.json (array de diccionaris {"ip": "", "descripcio": ""}) 

Variables del .env que fa servir `main.py`:

| Variable | Descripció |
|---|---|
| `WEBEX_ACCESS_TOKEN` | Token del bot de Webex |
| `WEBEX_ROOM_ID` | ID de la sala on s'envien les alertes |

> `TOKEN_TELEGRAM` i `CHAT_IDS_TELEGRAM` només els fa servir `main_telegram_.py`, la versió antiga anterior a la migració a Webex.


## Funcionament

Un fil (`threading.Thread`) per cada IP de `LlistaIPs.json`. Cada 30 s fa `ping -c 3`
i **només** notifica quan l'estat canvia respecte del cicle anterior. En arrancar
s'assumeix que tot està UP, per no enviar una allau d'alertes a l'inici.


### Cua d'alertes pendents

Quan un tall de xarxa fa caure els dispositius monitoritzats, sovint deixa el servidor
també sense DNS (els servidors DNS de la casa estan a la pròpia llista monitoritzada).
En aquest cas `webexapis.com` no es pot resoldre i **l'alerta de DOWN es perdia**: al
recuperar-se la connexió només arribava l'UP, i semblava un UP sense DOWN previ.

Per evitar-ho, `enviar_alerta_webex()` retorna `True`/`False` i cada fil manté una cua
`pendents`:

1. En detectar un canvi d'estat es congela el text del missatge amb **l'hora real de la
   detecció** i s'encua. `swResposta` s'actualitza al moment, de manera que mentre el
   dispositiu segueixi DOWN **no s'encua res més** (només es notifiquen canvis reals).
2. Cada cicle s'intenta buidar la cua en ordre. Si l'enviament falla, els missatges es
   conserven i es reintenten al cicle següent.
3. Quan torna la connectivitat arriben tots els missatges seguits, en ordre i amb les
   hores correctes de quan va passar cada cosa.

`MAX_PENDENTS` (50) limita la mida de la cua per dispositiu, per si hi hagués un tall
molt llarg amb el dispositiu fent *flapping*.


### Logs

Tots els `print()` porten `flush=True`. Sense això la sortida cap al journal queda
*block-buffered* i els missatges hi apareixen amb molt de retard (s'han arribat a veure
diferències de dies entre la marca de temps de `journalctl` i la de dins del missatge).

~~~
journalctl -u jmg_alertesPing.service -f
~~~


## Servei systemd

S'ha creat el fitxer "/etc/systemd/system/jmg_alertesPing.service"
amb el següent contingut:


~~~

[Unit]
Description=Servei d'alertes per mointorejar IPs
After=network.target

[Service]
# Usuario que ejecutará el script (puede ser tu usuario o uno específico)
User=jordi

# Directorio de trabajo del script (¡importante!)
WorkingDirectory=/home/jordi/projectes/python/pings2nPla

# Comando para ejecutar el script
# Usamos la ruta completa a python3 y a tu script
# ExecStart=/usr/bin/python3 /home/jordi/projectes/python/pings2nPla/main.py
ExecStart=/home/jordi/projectes/python/pings2nPla/entvirt/bin/python3 /home/jordi/projectes/python/pings2nPla/main.py


# Política de reinicio: si el script falla, se reiniciará siempre
Restart=always

[Install]
WantedBy=multi-user.target

~~~



Explicación rápida de lo que hace esto:

[Unit]: Describe el servicio y le dice que espere a que la red esté activa (After=network.target).

[Service]: Especifica quién ejecuta el script (User), dónde lo ejecuta (WorkingDirectory) y cómo lo ejecuta (ExecStart). Lo más importante es Restart=always, que es tu seguro de vida: si el script se cierra por un error, systemd lo levantará de nuevo.

[Install]: Le dice al sistema que este servicio debe iniciarse en el arranque normal del sistema.

Després de tocar `main.py`:

~~~
sudo systemctl restart jmg_alertesPing.service
~~~
