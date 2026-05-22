# 🏗️ Sistema de Control Grúa Torre - Guía del Usuario

## 📋 Descripción General

Este proyecto implementa un **sistema de control híbrido para una grúa torre** que combina control manual (mediante joysticks físicos) y control remoto (vía navegador web). La arquitectura utiliza un **Arduino Nano** como controlador de movimiento y un **ESP32** como servidor web que permite controlar la grúa desde cualquier dispositivo conectado a la red WiFi.

### ✨ Características Principales
- ✅ Control remoto mediante interfaz web intuitiva
- ✅ Control manual con joysticks analógicos  
- ✅ Fusión sensorial inteligente (combinación de ambos controles)
- ✅ Telemetría en tiempo real (IP, señal WiFi, uptime)
- ✅ Diseño responsivo para desktop y móvil
- ✅ Protocolo UART seguro con timeout de emergencia
- ✅ Menú interactivo de inicialización

---

## 🔧 Requisitos Previos

### Hardware Necesario
- **ESP32 DevKit V1** (Controlador de red)
- **Arduino Nano** (Controlador de movimiento)
- **3 Joysticks analógicos** (Carro X, Elevación Y, Giro Z)
- **TB6612FNG** (Controlador motor dual para carro y elevación)
- **DRV8825** (Controlador Stepper para giro)
- **Motor Stepper Nema 17** (Rotación de torre)
- **Motores DC** (Carro y elevación)
- **Cables jumper** y conectores
- **Fuente de alimentación** (compatible con 5V y 12V)

### Software Necesario
- **Arduino IDE** (para programar el Arduino Nano)
- **MicroPython** o **Thonny IDE** (para el ESP32)
- **Navegador web moderno** (Chrome, Firefox, Safari, Edge)

---

## ⚡ Configuración Inicial

### 1️⃣ Configuración del ESP32

#### Paso 1: Actualizar Credenciales WiFi
Abre el archivo `ESP32/boot.py` y modifica:

```python
SSID = 'TU_RED_WIFI'          # Nombre de tu red WiFi
PASSWORD = 'TU_CONTRASEÑA'    # Contraseña de tu red
```

#### Paso 2: Flashear el ESP32
1. Conecta el ESP32 a tu computadora por USB
2. Abre **Thonny** o **Arduino IDE**
3. Carga los archivos:
   - `ESP32/boot.py` → Memoria del ESP32 como `boot.py`
   - `ESP32/main.py` → Memoria del ESP32 como `main.py`
   - `ESP32/index.html` → Memoria del ESP32 como `index.html`
4. Reinicia el ESP32

#### Paso 3: Verificar Conexión
- Abre el monitor serial (9600 baud)
- Deberías ver el menú de inicio:
  ```
  ========================================
        SISTEMA DE CONTROL - GRÚA TORRE
  ========================================
  1. Iniciar sistema normalmente (Modo Ejecución)
  2. Detener en modo programación (Liberar REPL)
  Selecciona una opción (Avanza a opción 1 en 5s)...
  ```
- Presiona `1` o espera 5 segundos
- El ESP32 se conectará a WiFi y mostrará su IP

### 2️⃣ Configuración del Arduino Nano

#### Paso 1: Cargar el Código
1. Abre `Arduino/grua_arduino/grua_arduino.ino` en Arduino IDE
2. Selecciona placa: **Arduino Nano**
3. Selecciona puerto COM
4. Carga el código

#### Paso 2: Verificar Conexión UART
- Los motores deberían responder a los comandos del joystick
- LED del ESP32 parpadea al recibir comandos web

---

## 🚀 Cómo Usar la Interfaz Web

### Acceso a la Interfaz
1. Abre tu navegador web
2. Navega a: `http://<IP_ESP32>` (ej: `http://192.168.1.100`)
3. Verás la pantalla de bienvenida con animación
4. La interfaz de control aparecerá automáticamente

### Controles Disponibles

#### 🎮 Pad Direccional (Carro / Giro)
```
        ⬆️
    ↩️  ⏹️  ↪️
        ⬇️
```
- **⬆️ Adelante**: Mueve el carro hacia adelante
- **⬇️ Atrás**: Mueve el carro hacia atrás
- **↩️ Izquierda**: Gira la torre en sentido antihorario
- **↪️ Derecha**: Gira la torre en sentido horario
- **⏹️ Stop**: Detiene todos los movimientos

#### 📈 Controles de Elevación
- **▲ Subir**: Levanta la carga
- **▼ Bajar**: Baja la carga

### 📊 Panel de Telemetría
La interfaz muestra en tiempo real:
- **IP**: Dirección IP del ESP32
- **SSID**: Nombre de la red WiFi
- **RSSI**: Intensidad de señal (-100 a 0 dBm, mayor es mejor)
- **Uptime**: Tiempo de funcionamiento del sistema
- **Último comando**: Último movimiento ejecutado
- **Comandos**: Total de comandos recibidos

---

## 🏛️ Estructura del Proyecto

```
PG_2526_Johanan_Castro/
├── README.md                    # Esta guía
├── CAMBIOS_IMPLEMENTADOS.md    # Documentación de cambios
├── OpenSpec.md                 # Especificación técnica detallada
├── Arduino/
│   └── grua_arduino/
│       └── grua_arduino.ino    # Código del Arduino Nano
└── ESP32/
    ├── boot.py                 # Script de inicialización
    ├── main.py                 # Servidor web y telemetría
    └── index.html              # Interfaz web del usuario
```

---

## ⚙️ Especificación Técnica Resumida

### Protocolo de Comunicación (UART)
- **Baudrate**: 9600 bps
- **Formato**: 8 bits, sin paridad, 1 bit de stop
- **Comandos**: Un solo byte por comando

#### Diccionario de Comandos
| Comando | Acción |
|:---:|:---|
| `F` | Adelante (Carro +X) |
| `B` | Atrás (Carro -X) |
| `U` | Subir (Elevación +Y) |
| `D` | Bajar (Elevación -Y) |
| `L` | Izquierda (Giro Antihorario) |
| `R` | Derecha (Giro Horario) |
| `S` | Stop (Detener todo) |

### Timeout de Seguridad
- Si el Arduino recibe un comando de movimiento pero **no recibe ningún dato en 1 segundo**, automáticamente detiene el movimiento
- Esto previene movimientos involuntarios por pérdida de conexión

---

## 🔍 Troubleshooting

### Problema: La interfaz web no carga
**Solución:**
1. Verifica que el ESP32 esté conectado a WiFi (check el monitor serial)
2. Confirma la IP del ESP32 y cópiala correctamente en el navegador
3. Asegúrate de estar en la misma red WiFi que el ESP32

### Problema: El ESP32 no se conecta a WiFi
**Solución:**
1. Verifica SSID y PASSWORD en `boot.py`
2. Asegúrate de que tu red no use caracteres especiales
3. Reinicia el router y el ESP32
4. Prueba acercando el ESP32 al router

### Problema: Los motores no responden
**Solución:**
1. Verifica la conexión UART entre ESP32 (GPIO 17) y Arduino (D0)
2. Confirma que ambos están alimentados correctamente
3. Revisa los pines del motor en `grua_arduino.ino`
4. Abre monitor serial del Arduino para ver mensajes de debug

### Problema: La telemetría muestra "Cargando..." indefinidamente
**Solución:**
1. Revisa que el endpoint `/telemetry` esté implementado en `main.py`
2. Comprueba la consola del navegador (F12) para ver errores
3. Reinicia el ESP32

---

## 🎮 Guía de Uso Práctica

### Secuencia de Inicio Recomendada
1. ✅ Enciende la fuente de alimentación
2. ✅ El ESP32 muestra menú → Presiona `1` o espera 5 segundos
3. ✅ Espera mensaje: "WiFi conectada correctamente"
4. ✅ Abre navegador e ingresa IP del ESP32
5. ✅ Espera animación de bienvenida
6. ✅ Interfaz de control lista para usar

### Uso Seguro
- ⚠️ **Primero prueba los movimientos lentamente**
- ⚠️ **Evita cambios de red WiFi durante operación**
- ⚠️ **Cierra navegador después de usar** (activa timeout de seguridad)
- ⚠️ **Supervisa los movimientos en todo momento**

---

## 📊 Ejemplo de Respuesta de Telemetría

```json
{
  "connected": true,
  "ip": "192.168.1.105",
  "ssid": "Mi_WiFi",
  "rssi": -45,
  "uptime": "00:15:32",
  "last_command": "F",
  "command_count": 127,
  "netconf": ["192.168.1.105", "255.255.255.0", "192.168.1.1", "8.8.8.8"]
}
```

---

## 🌐 Endpoints Web Disponibles

| Endpoint | Método | Descripción |
|:---|:---:|:---|
| `/` | GET | Sirve la interfaz web (`index.html`) |
| `/cmd?action={CMD}` | GET | Envía comando de movimiento (F/B/U/D/L/R/S) |
| `/telemetry` | GET | Obtiene datos de telemetría en JSON |

---

## 🚦 Estados de Operación

### LED del ESP32 (GPIO 2)
- **Parpadea**: Comando web recibido
- **Apagado**: En espera de comandos
- **Encendido fijo**: Error o falla

### Monitor Serial del Arduino
- Mensajes de debug con cada comando recibido
- Alertas de timeout
- Estado de motores

---

## 🔐 Consideraciones de Seguridad

✅ **Implementado:**
- Timeout de emergencia (1 segundo)
- Validación de comandos UART
- Feedback visual de movimientos
- Stop manual disponible siempre

⚠️ **Recomendaciones:**
- Usa WiFi privada (no público)
- Contraseña WiFi fuerte
- Supervisa operación remota
- Apaga sistema cuando no esté en uso

---

## 📞 Soporte y Documentación

- **OpenSpec.md**: Especificación técnica detallada del proyecto
- **CAMBIOS_IMPLEMENTADOS.md**: Registro de todas las implementaciones
- **Código comentado**: Los archivos incluyen comentarios detallados

---

## 👤 Información del Proyecto

**Proyecto**: Sistema de Control Grúa Torre con ESP32 + Arduino  
**Versión**: 1.0  
**Fecha**: Mayo 2026  
**Autor**: Johanan Castro  
**Tecnologías**: MicroPython, Arduino C, JavaScript, HTML/CSS  

---

## 📝 Licencia

Este proyecto es educativo y está disponible para uso académico.

---

**¡Disfruta controlando tu grúa torre! 🏗️**
