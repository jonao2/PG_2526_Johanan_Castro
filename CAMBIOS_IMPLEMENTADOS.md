# 📋 CAMBIOS IMPLEMENTADOS - Sistema de Control Grúa Torre

## Actualización Técnica del Proyecto

### 📅 Sesión 21 de Mayo de 2026

#### 1. **boot.py - Sistema de Inicialización y Menú**
Nuevo archivo implementado con las siguientes características:

- **Menú interactivo de inicio**: Permite al usuario seleccionar entre:
  - Opción 1: Inicio normal (Modo Ejecución) - Ejecuta main.py
  - Opción 2: Modo Programación - Libera la consola REPL para desarrollo
  - Timeout automático de 5 segundos para avance sin interacción

- **Gestión de conexión WiFi**:
  - Función `connect_wifi()`: Conecta a la red WiFi (SSID y PASSWORD configurables)
  - Detección de conexión previa
  - Timeout de 15 segundos para intentar conexión
  - Información de configuración de red (IP, Gateway, etc.)
  - Manejo de errores y fallos de conexión

- **Flujo de inicialización**:
  - Verifica conexión WiFi antes de ejecutar main.py
  - Aborta el inicio si falla la conexión
  - Manejo de excepciones en la carga de main.py

---

#### 2. **main.py - Servidor Web y Sistema de Telemetría**
Nuevo archivo implementado con las siguientes características:

##### **2.1 Configuración de Hardware**
- UART2 configurado (TX: GPIO 17, RX: GPIO 16) para comunicación con Arduino
- Baudrate: 9600 bps
- LED de status en GPIO 2 para feedback visual

##### **2.2 Sistema de Telemetría**
Implementada la función `get_telemetry()` que recolecta información del sistema:

**Datos de Uptime:**
- `format_uptime()`: Calcula tiempo de funcionamiento en formato HH:MM:SS
- Actualización en tiempo real desde el inicio del ESP32

**Datos de Red (WiFi):**
- `connected`: Estado de conexión WiFi (bool)
- `ip`: Dirección IP actual
- `ssid`: Nombre de la red WiFi conectada
- `rssi`: Intensidad de señal WiFi (dBm)
- `netconf`: Configuración completa de red (IP, Gateway, Subnet, DNS)

**Datos de Operación:**
- `last_command`: Último comando ejecutado recibido del navegador
- `command_count`: Contador de comandos totales ejecutados

##### **2.3 Servidor Web Asíncrono**
- Función `serve_file()`: Sirve archivo index.html al cliente
- Función `handle_request()`: Maneja peticiones HTTP entrantes
- Despacho de comandos UART hacia el Arduino
- Control asíncrono usando `uasyncio`
- Manejo de errores para archivos no encontrados

---

#### 3. **index.html - Interfaz Web del Usuario**
Archivo de interfaz web para control remoto de la grúa torre desde el navegador.

---

### 🔧 Características Técnicas Implementadas

| Característica | Descripción |
|:---|:---|
| **Arquitectura Híbrida** | Control manual (Joysticks en Arduino) + Control remoto (Web en ESP32) |
| **Comunicación Serial (UART)** | Protocolo de un solo byte a 9600 bps |
| **Servidor Web** | Asíncrono en ESP32 para peticiones HTTP en tiempo real |
| **Telemetría** | Monitoreo continuo de estado del sistema y conexión |
| **Menú de Inicio** | Selección interactiva entre ejecución y programación |
| **Manejo de Errores** | Gestión robusta de fallos de conexión y excepciones |

---

### 📊 Datos Proporcionados por Telemetría

El sistema proporciona los siguientes datos en tiempo real:

```json
{
  "connected": true,
  "ip": "192.168.x.x",
  "ssid": "MI_WIFI",
  "rssi": -50,
  "uptime": "00:05:30",
  "last_command": "ADELANTE",
  "command_count": 15,
  "netconf": ["192.168.x.x", "255.255.255.0", "192.168.x.1", "8.8.8.8"]
}
```

---

### ✅ Estado del Proyecto

- ✅ Comunicación UART Arduino ↔ ESP32 implementada
- ✅ Servidor web asíncrono operativo
- ✅ Sistema de telemetría en tiempo real
- ✅ Menú interactivo de inicio
- ✅ Gestión de conexión WiFi
- ✅ Control remoto via navegador web
- ✅ Feedback LED de estado

---

### 🔐 Configuración Necesaria

En `boot.py`, actualiza las siguientes credenciales:
```python
SSID = 'MI_WIFI'          # Nombre de tu red WiFi
PASSWORD = 'MI_PASSWORD'  # Contraseña de tu red WiFi
```

---

### 📝 Notas de Implementación

1. El protocolo UART utiliza un solo byte para simplificar el parsing en Arduino
2. La telemetría se actualiza en tiempo real sin bloquear el servidor web
3. El menú de inicio permite tanto desarrollo como ejecución automática
4. El timeout de 5 segundos en el menú permite uso autónomo del sistema

---

**Proyecto:** Sistema de Control Grúa Torre con ESP32 + Arduino  
**Versión:** 1.0  
**Fecha de Implementación:** 21 de Mayo de 2026  
**Responsable:** Johanan Castro
