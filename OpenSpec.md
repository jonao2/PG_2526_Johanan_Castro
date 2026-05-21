# OpenSpec: Proyecto Grúa Torre con Control Dual

## 1. Visión General del Sistema
La grúa torre implementa una arquitectura de control híbrido (Manual y Remoto) que se integra mediante dos microcontroladores en una topología de "Actuador/Servidor".

### 1.1 Microcontroladores
1. **Controlador Principal (Actuador): Arduino Nano**
   - Ejecuta la lógica de control estricto de tiempo (generación PWM y control del Stepper Motor).
   - Combina intenciones físicas (Joysticks) e intenciones de red (UART).
2. **Controlador de Comunicaciones (Servidor Web): ESP32 DevKit V1**
   - Levanta un servidor web asíncrono y gestiona conexiones WiFi.
   - Traduce peticiones HTTP entrantes y despacha un solo byte (Character) por puerto serial.

---

## 2. Especificación de Hardware (Pinout)

### 2.1 Arduino Nano (Capa de Control Físico)
| Componente | Pin/Señal | Propósito |
| :--- | :---: | :--- |
| Joystick X (Carro) | `A0` | Entrada analógica (Eje X) |
| Joystick Y (Elevación) | `A1` | Entrada analógica (Eje Y) |
| Joystick Z (Giro) | `A2` | Entrada analógica (Giro de la torre) |
| TB6612FNG (AIN1) | `D2` | Dirección Carro 1 |
| TB6612FNG (AIN2) | `D4` | Dirección Carro 2 |
| TB6612FNG (PWMA) | `D3` | Velocidad Carro (PWM) |
| TB6612FNG (BIN1) | `D7` | Dirección Elevación 1 |
| TB6612FNG (BIN2) | `D8` | Dirección Elevación 2 |
| TB6612FNG (PWMB) | `D5` | Velocidad Elevación (PWM) |
| DRV8825 (STEP) | `D9` | Pulso Stepper (Nema 17) |
| DRV8825 (DIR) | `D10`| Dirección Stepper |
| ESP32 TX | `D0 (RX)` | Recepción de comandos Seriales remotos |

### 2.2 ESP32 (Capa de Red)
| Componente | Pin/Señal | Propósito |
| :--- | :---: | :--- |
| Arduino D0 (RX) | `GPIO 17 (TX2)`| Envío de comandos al actuador |
| LED Status | `GPIO 2` | Feedback visual en peticiones recibidas |

---

## 3. Especificación de Protocolos

### 3.1 Protocolo UART (ESP32 -> Arduino)
El protocolo es de **un solo byte**, simplificando al máximo el *parsing* en el Arduino y asegurando rapidez. Se utiliza `9600 bps` para asegurar fiabilidad sobre cables de jumper sin apantallar.

*   **Baudrate:** 9600
*   **Data Bits:** 8
*   **Parity:** Ninguna
*   **Stop Bits:** 1

**Diccionario de Comandos (ASCII):**
*   `'F'` : Adelante / Carro Avance (+X)
*   `'B'` : Atrás / Carro Retroceso (-X)
*   `'U'` : Subir / Elevación Ascenso (+Y)
*   `'D'` : Bajar / Elevación Descenso (-Y)
*   `'L'` : Izquierda / Giro Stepper (Antihorario)
*   `'R'` : Derecha / Giro Stepper (Horario)
*   `'S'` : Stop / Detener todos los movimientos accionados por red

> **Timeout de Seguridad:** Si el Arduino recibe un comando de movimiento (ej. `'F'`), asume que el usuario mantiene presionado el botón. Sin embargo, si pasan **1000 milisegundos** sin recibir *ningún* byte adicional, el Arduino establecerá la aportación de velocidad de red a 0 por seguridad (falla de red, cierre de navegador, etc.).

### 3.2 Protocolo Web (HTTP REST-like)
El ESP32 implementa un servidor `uasyncio` que responde a peticiones simples.

#### Endpoint 1: Interfaz de Usuario
*   **URL:** `/`
*   **Método:** `GET`
*   **Respuesta:** HTTP 200 OK, `Content-Type: text/html`. Sirve el archivo estático `index.html`.

#### Endpoint 2: Comando de Movimiento
*   **URL:** `/cmd?action={COMANDO}`
*   **Método:** `GET`
*   **Parámetro `action`:** Caracteres válidos (`F`, `B`, `U`, `D`, `L`, `R`, `S`).
*   **Descripción:** Inicia, mantiene o detiene un movimiento de la grúa. El cliente web (navegador) lanza esta petición cada `250ms` mientras el usuario mantiene presionado un botón en pantalla (usando *Fetch API* en JavaScript).
*   **Respuesta:** HTTP 200 OK con payload "OK".

---

## 4. Lógica de Fusión Sensorial (Joystick + Web)
La innovación en el código Arduino es el "Control Mixto".
La posición analógica de los Joysticks se mapea a una velocidad de -255 a 255.
El comando web se interpreta como una señal digital extrema (1 o -1), multiplicándose por la velocidad máxima (255) o pasos por segundo máximos en el caso del stepper.

Ambas intenciones se suman de forma algebraica:
```cpp
int finalElev = constrain(joyElev + (webElev * 255), -255, 255);
```
*Si alguien tira del joystick hacia abajo (-255) mientras otro usuario envía un comando web para subir (+255), la velocidad resultante es 0 (Seguridad y prioridad balanceada).*

---

## 5. Requisitos de software añadidos

### 5.1 Flujo de arranque del ESP32
1. `boot.py` se ejecuta primero en el ESP32.
2. Muestra un menú en la terminal con dos opciones:
   - `1`: iniciar normalmente y continuar con el sistema.
   - `2`: detener en modo programación y liberar el REPL.
3. Si no hay entrada del usuario en `5 segundos`, continúa automáticamente con la opción 1.
4. Si se elige opción 1, `boot.py` conecta al WiFi y solo entonces importa y arranca `main.py`.
5. Si no se conecta al WiFi, el arranque se interrumpe y no se ejecuta `main.py`.

### 5.2 Separación de responsabilidades en software
* `ESP32/boot.py`: manejo de arranque, menú de usuario, conexión WiFi y lanzamiento de `main.py`.
* `ESP32/main.py`: servidor web `uasyncio`, entrega de `index.html`, recepción de comandos HTTP y envío de comandos UART al Arduino.

### 5.3 Configuración del WiFi
* El ESP32 requiere las constantes `SSID` y `PASSWORD` definidas en `ESP32/boot.py`.
* Estas credenciales se deben personalizar antes de flashear el ESP32.

### 5.4 Comportamiento del servidor web
* `main.py` ya no realiza la conexión WiFi por sí mismo cuando se importa.
* Permite que `boot.py` controle la fase de inicialización.
* El servidor solo se inicia si `boot.py` completa la conexión WiFi.

### 5.5 Buenas prácticas de ejecución
* `main.py` debe contener una ejecución segura bajo `if __name__ == '__main__':`.
* Esto evita efectos secundarios no deseados al importar el módulo desde `boot.py`.

### 5.6 Componentes nuevos del software
* `boot.py` usa `uselect`, `sys`, `time`, `network` y `uasyncio`.
* `main.py` usa `uasyncio`, `UART` y `Pin`.
* El servidor HTTP asíncrono responde a `/` e `/cmd?action=...`.
