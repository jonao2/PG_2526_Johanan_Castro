# Requerimientos del Proyecto - Grúa Torre con Control Dual

## 1. Objetivo

Definir los requerimientos del sistema de control híbrido para una grúa torre, incluyendo las funciones del ESP32, Arduino y la interfaz web.

---

## 2. Requerimientos Funcionales

1. El sistema debe permitir el control remoto de la grúa a través de una interfaz web en el ESP32.
2. El ESP32 debe servir el archivo `index.html` en la raíz `/` mediante un servidor HTTP asíncrono (`uasyncio`).
3. El cliente web debe enviar comandos de movimiento a través de `/cmd?action={COMANDO}`.
4. Los botones deben enviar comandos mientras se mantienen presionados, repitiendo la petición cada 250 ms.
5. El ESP32 debe transmitir un solo byte de comando al Arduino por UART a 9600 bps.
6. El protocolo UART debe usar comandos válidos: `F`, `B`, `U`, `D`, `L`, `R`, `S`.
7. El sistema debe mostrar telemetría en tiempo real con los valores: estado de conexión, IP, SSID, RSSI, uptime, último comando y contador de comandos.
8. El ESP32 debe incluir un menú de inicio en `boot.py` con dos opciones:
   - `1`: iniciar normalmente y ejecutar `main.py`
   - `2`: detener en modo programación y liberar el REPL
9. Si no hay entrada en la terminal en 5 segundos, debe seleccionar automáticamente la opción 1.
10. Si falla la conexión WiFi, `boot.py` debe abortar el arranque y no ejecutar `main.py`.
11. `main.py` no debe intentar conectar al WiFi cuando se importa; solo debe iniciar el servidor si `boot.py` ya completó la conexión.
12. El código `main.py` debe tener una protección `if __name__ == '__main__':` para evitar efectos secundarios al importar el módulo.

---

## 3. Requerimientos de Hardware

1. El Arduino Nano actúa como controlador principal del movimiento.
2. El ESP32 actúa como servidor de comunicaciones y puente WLAN-UART.
3. El ESP32 debe usar UART2 con TX en GPIO 17 y RX en GPIO 16.
4. El Arduino debe recibir los comandos desde el ESP32 por su pin `D0` (RX).
5. El LED de estado del ESP32 debe estar conectado al pin GPIO 2 para feedback visual.
6. La comunicación UART debe ser de un solo byte para minimizar parsing en Arduino.

---

## 4. Requerimientos de Software

1. `ESP32/boot.py` debe usar `uselect`, `sys`, `time`, `network` y `uasyncio`.
2. `ESP32/main.py` debe usar `uasyncio`, `ujson`, `network`, `UART` y `Pin`.
3. `ESP32/index.html` debe ser responsivo y mostrar la telemetría exacta del ESP32.
4. El servidor web debe responder al endpoint `/telemetry` con JSON válido.
5. El archivo `index.html` debe incluir una animación de bienvenida y la interfaz de control.
6. El sistema debe manejar errores de conexión y mostrar estados claros en la interfaz.

---

## 5. Requerimientos No Funcionales

1. La interfaz debe ser clara, moderna y adecuada para calificación de innovación.
2. El tiempo de respuesta de los comandos debe ser bajo para garantizar control en tiempo real.
3. El diseño debe funcionar en desktop y móvil.
4. El proyecto debe estar documentado con los archivos `OpenSpec.md`, `README.md` y `REQUERIMIENTOS.md`.
5. La solución debe ser fácil de revisar y entender por un profesor o evaluador.

---

## 6. Notas

- `OpenSpec.md` describe la arquitectura, el hardware y los protocolos generales.
- `REQUERIMIENTOS.md` describe los requerimientos formales del proyecto.
- `README.md` es la guía de usuario para instalación, configuración y uso.
