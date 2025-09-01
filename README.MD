
## PINGS EN SEGON PLA

### Pings a servidors i switchs executats com a servei en 2n pla en un SO linux. Quan es produeix un DOWN, envia missatge a Telegram. El mateix quan recupera (UP)



> S'ha instal·lat el paquet python-decouple.

~~~ 
pip install python-decouple
~~~

S'han de definir els fitxers:
1. fitxer .env per posar pwds i demés
2. fitxer LlistatIPs.json (array de diccionaris {"ip": "", "descripcio": ""}) 


S'ha creat el fitxer "/etc/systemd/system/alertesPing.service"
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