import sys
import uselect
import time
import network
import uasyncio as asyncio

SSID = 'MI_WIFI'
PASSWORD = 'MI_PASSWORD'


def menu_inicio(timeout_segundos=5):
    """
    Muestra un menú en la terminal. Avanza automáticamente si no hay respuesta.
    """
    print("\n" + "="*40)
    print("      SISTEMA DE CONTROL - GRÚA TORRE")
    print("="*40)
    print("1. Iniciar sistema normalmente (Modo Ejecución)")
    print("2. Detener en modo programación (Liberar REPL)")
    print(f"Selecciona una opción (Avanza a opción 1 en {timeout_segundos}s)...")
    
    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)
    
    tiempo_inicio = time.time()
    while (time.time() - tiempo_inicio) < timeout_segundos:
        if poller.poll(100):
            caracter = sys.stdin.read(1)
            if caracter == '1':
                print("\n-> Opción 1 seleccionada. Iniciando...")
                return True
            elif caracter == '2':
                print("\n-> Opción 2 seleccionada. Modo programación activo.")
                print("Consola REPL liberada. Puedes subir o modificar archivos.")
                return False
    
    print("\n-> Tiempo de espera agotado. Iniciando de forma automática...")
    return True


def connect_wifi(ssid, password, timeout_segundos=15):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if sta_if.isconnected():
        print("WiFi ya está conectado.")
        print("Configuración de red:", sta_if.ifconfig())
        return True

    print("Conectando a la red WiFi...")
    sta_if.connect(ssid, password)

    inicio = time.time()
    while not sta_if.isconnected() and (time.time() - inicio) < timeout_segundos:
        sys.stdout.write('.')
        time.sleep(0.5)

    if sta_if.isconnected():
        print("\nWiFi conectada correctamente.")
        print("Configuración de red:", sta_if.ifconfig())
        return True

    print("\nNo se pudo conectar al WiFi.")
    return False


if menu_inicio(timeout_segundos=5):
    if connect_wifi(SSID, PASSWORD):
        try:
            import main
            asyncio.run(main.main())
        except Exception as e:
            print("Error iniciando main.py:", e)
            sys.exit()
    else:
        print("Se aborta el inicio por fallo de conexión WiFi.")
        sys.exit()
else:
    sys.exit()
