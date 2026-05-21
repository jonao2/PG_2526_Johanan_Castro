import uasyncio as asyncio
import ujson
import time
import network
from machine import UART, Pin

# ----------------------------------------------------
# 1. CONFIGURACIÓN DE HARDWARE
# ----------------------------------------------------
# UART2: TX en GPIO 17 (se conecta al RX del Arduino D0)
# RX en GPIO 16 (no se usa en este proyecto pero se requiere para inicializar)
uart = UART(2, baudrate=9600, tx=17, rx=16)
led = Pin(2, Pin.OUT)

start_time_ms = time.ticks_ms()
last_command = None
command_count = 0

# ----------------------------------------------------
# 2. TELEMETRÍA
# ----------------------------------------------------

def format_uptime():
    elapsed_ms = time.ticks_diff(time.ticks_ms(), start_time_ms)
    seconds = elapsed_ms // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


def get_wifi_ssid(sta_if):
    try:
        return sta_if.config('essid')
    except Exception:
        return 'desconocido'


def get_wifi_rssi(sta_if):
    try:
        return sta_if.status('rssi')
    except Exception:
        return None


def get_telemetry():
    sta_if = network.WLAN(network.STA_IF)
    connected = sta_if.isconnected()
    net_conf = None
    ip = None
    if connected:
        net_conf = sta_if.ifconfig()
        ip = net_conf[0]

    return {
        'connected': connected,
        'ip': ip or 'desconocido',
        'ssid': get_wifi_ssid(sta_if) or 'desconocido',
        'rssi': get_wifi_rssi(sta_if),
        'uptime': format_uptime(),
        'last_command': last_command or 'ninguno',
        'command_count': command_count,
        'netconf': net_conf or ['0.0.0.0', '', '', '']
    }

# ----------------------------------------------------
# 3. FUNCIONES DEL SERVIDOR WEB
# ----------------------------------------------------
async def serve_file(reader, writer):
    """Lee el archivo index.html y lo envía al cliente."""
    try:
        with open('index.html', 'r') as f:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            await writer.drain()
            for line in f:
                writer.write(line)
                await writer.drain()
    except Exception as e:
        writer.write('HTTP/1.0 404 Not Found\r\n\r\nFile index.html Not Found')
        await writer.drain()

async def handle_request(reader, writer):
    """Maneja las peticiones HTTP entrantes y despacha comandos UART."""
    global last_command, command_count

    try:
        request_line = await reader.readline()
        if not request_line:
            return

        request_line = request_line.decode('utf-8')

        # Consumir el resto de los headers para no bloquear el buffer
        while await reader.readline() != b'\r\n':
            pass

        parts = request_line.split(' ')
        if len(parts) > 1:
            path = parts[1]

            if path == '/' or path == '/index.html':
                await serve_file(reader, writer)
            elif path == '/telemetry':
                telemetry = get_telemetry()
                payload = ujson.dumps(telemetry)
                writer.write('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
                writer.write(payload)
                await writer.drain()
            elif path.startswith('/cmd?action='):
                action = path.split('=')[1]
                valid_cmds = ['F', 'B', 'U', 'D', 'L', 'R', 'S']
                
                cmd_descriptions = {
                    'F': 'Adelante',
                    'B': 'Atrás',
                    'U': 'Subir',
                    'D': 'Bajar',
                    'L': 'Izquierda',
                    'R': 'Derecha',
                    'S': 'Stop'
                }
                
                if action in valid_cmds:
                    uart.write(action)
                    led.value(not led.value())
                    last_command = action
                    command_count += 1
                    
                    desc = cmd_descriptions.get(action, 'Desconocido')
                    print(f'[COMANDO] {desc} ({action}) - Total: {command_count}')
                    
                    writer.write('HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')
                    await writer.drain()
                else:
                    writer.write('HTTP/1.0 400 Bad Request\r\n\r\nComando inválido')
                    await writer.drain()
            else:
                writer.write('HTTP/1.0 404 Not Found\r\n\r\n')
                await writer.drain()

    except Exception as e:
        print('Error procesando petición:', e)
    finally:
        writer.close()
        await writer.wait_closed()

# ----------------------------------------------------
# 4. BUCLE PRINCIPAL
# ----------------------------------------------------
async def main():
    print('Iniciando servidor web asíncrono...')
    await asyncio.start_server(handle_request, '0.0.0.0', 80)
    print('Servidor corriendo exitosamente.')

    while True:
        await asyncio.sleep(1)

# Ejecutar el servidor al final de main.py de manera segura
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nServidor web detenido desde el teclado.')
