import uasyncio as asyncio
import machine
from machine import UART, Pin

# ----------------------------------------------------
# 1. CONFIGURACIÓN DE HARDWARE
# ----------------------------------------------------
# UART2: TX en GPIO 17 (se conecta al RX del Arduino D0)
# RX en GPIO 16 (no se usa en este proyecto pero se requiere para inicializar)
uart = UART(2, baudrate=9600, tx=17, rx=16) 

# LED integrado para indicar actividad (Opcional, en algunos ESP32 es el GPIO 2)
led = Pin(2, Pin.OUT)

# ----------------------------------------------------
# 2. FUNCIONES DEL SERVIDOR WEB
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
    try:
        request_line = await reader.readline()
        if not request_line:
            return
            
        request_line = request_line.decode('utf-8')
        
        # Consumir el resto de los headers para no bloquear el buffer
        while await reader.readline() != b'\r\n':
            pass
            
        # Parsear la ruta de la petición (ej. "GET /cmd?action=F HTTP/1.1")
        parts = request_line.split(' ')
        if len(parts) > 1:
            path = parts[1]
            
            # Raíz: servir la interfaz web
            if path == '/':
                await serve_file(reader, writer)
                
            # Endpoint de comandos
            elif path.startswith('/cmd?action='):
                action = path.split('=')[1]
                
                # Validar comandos permitidos
                valid_cmds = ['F', 'B', 'U', 'D', 'L', 'R', 'S']
                if action in valid_cmds:
                    # Enviar por puerto serial al Arduino
                    uart.write(action)
                    
                    # Toggle del LED para feedback visual
                    led.value(not led.value()) 
                    
                    # Respuesta de éxito al cliente
                    writer.write('HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK')
                    await writer.drain()
            else:
                writer.write('HTTP/1.0 404 Not Found\r\n\r\n')
                await writer.drain()
                
    except Exception as e:
        print("Error procesando petición:", e)
    finally:
        writer.close()
        await writer.wait_closed()

# ----------------------------------------------------
# 3. BUCLE PRINCIPAL
# ----------------------------------------------------
async def main():
    print('Iniciando servidor web asíncrono...')
    # Levantar servidor en el puerto 80 para cualquier IP local
    server = await asyncio.start_server(handle_request, '0.0.0.0', 80)
    print('Servidor corriendo exitosamente.')
    
    # Mantener el loop vivo
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Servidor detenido manualmente.')
