import network
import time

# Configuración de credenciales WiFi (Modificar según entorno)
ssid = 'MI_WIFI'
password = 'MI_PASSWORD'

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Conectando a la red WiFi...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        # Esperar hasta que se establezca la conexión
        while not sta_if.isconnected():
            time.sleep(0.5)
            print('.', end='')
    
    print('\nConexión WiFi establecida.')
    print('Configuración de red (IP, Máscara, Gateway, DNS):', sta_if.ifconfig())
    print('Abre la IP mostrada en tu navegador web para controlar la grúa.')

# Iniciar conexión al encender el dispositivo
do_connect()
